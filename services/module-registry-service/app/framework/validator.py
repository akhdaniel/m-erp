"""
Module validation system for manifest, dependencies, and security checks
"""
import re
import ast
import hashlib
import tempfile
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
import logging
from app.framework.manifest import ModuleManifest, ManifestValidator

logger = logging.getLogger(__name__)


class SecurityLevel(str, Enum):
    """Security levels for module validation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationResult:
    """Result of module validation"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.security_issues: List[Dict[str, Any]] = []
        self.dependency_issues: List[str] = []
        
    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False
        
    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)
        
    def add_security_issue(self, level: SecurityLevel, message: str, details: Optional[str] = None):
        """Add security issue"""
        issue = {
            "level": level,
            "message": message,
            "details": details
        }
        self.security_issues.append(issue)
        
        # Critical and high security issues are validation errors
        if level in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
            self.add_error(f"Security issue ({level}): {message}")
    
    def add_dependency_issue(self, message: str):
        """Add dependency issue"""
        self.dependency_issues.append(message)
        self.add_error(f"Dependency issue: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "security_issues": self.security_issues,
            "dependency_issues": self.dependency_issues
        }


class DependencyValidator:
    """Validator for module dependencies"""
    
    def __init__(self, available_modules: Optional[List[str]] = None):
        self.available_modules = available_modules or []
        self.available_services = [
            "user-auth-service",
            "company-partner-service", 
            "module-registry-service",
            "service-registry",
            "audit-service",
            "notification-service"
        ]
        
    def validate_dependencies(self, manifest: ModuleManifest) -> List[str]:
        """Validate module dependencies"""
        issues = []
        
        for dep in manifest.dependencies or []:
            if dep.type == "module":
                if not dep.optional and dep.name not in self.available_modules:
                    issues.append(f"Required module dependency '{dep.name}' is not available")
                    
            elif dep.type == "service":
                if not dep.optional and dep.name not in self.available_services:
                    issues.append(f"Required service dependency '{dep.name}' is not available")
                    
            elif dep.type == "python_package":
                # TODO: Add Python package validation
                pass
                
            elif dep.type == "system":
                # TODO: Add system dependency validation
                pass
        
        return issues
    
    def check_circular_dependencies(self, manifest: ModuleManifest, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Check for circular dependencies"""
        issues = []
        
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for module in dependency_graph:
            if module not in visited:
                if has_cycle(module, visited, set()):
                    issues.append(f"Circular dependency detected involving module '{manifest.name}'")
                    break
        
        return issues


class SecurityValidator:
    """Validator for module security"""
    
    # Dangerous Python functions and modules
    DANGEROUS_IMPORTS = {
        'os', 'subprocess', 'sys', 'eval', 'exec', 'compile', 
        'open', '__import__', 'globals', 'locals', 'vars',
        'getattr', 'setattr', 'delattr', 'hasattr'
    }
    
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input'
    }
    
    RESTRICTED_MODULES = {
        'socket', 'urllib', 'urllib2', 'urllib3', 'requests',
        'ftplib', 'smtplib', 'poplib', 'imaplib',
        'threading', 'multiprocessing', 'subprocess',
        'ctypes', 'cffi', 'gc', 'sys', 'os'
    }
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        self.security_level = security_level
        
    def analyze_python_code(self, code: str, filename: str = "<string>") -> List[Dict[str, Any]]:
        """Analyze Python code for security issues"""
        issues = []
        
        try:
            tree = ast.parse(code, filename=filename)
            
            for node in ast.walk(tree):
                # Check for dangerous imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.RESTRICTED_MODULES:
                            issues.append({
                                "level": SecurityLevel.HIGH,
                                "message": f"Restricted module import: {alias.name}",
                                "line": node.lineno,
                                "filename": filename
                            })
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.RESTRICTED_MODULES:
                        issues.append({
                            "level": SecurityLevel.HIGH,
                            "message": f"Restricted module import: {node.module}",
                            "line": node.lineno,
                            "filename": filename
                        })
                
                # Check for dangerous function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.DANGEROUS_FUNCTIONS:
                            issues.append({
                                "level": SecurityLevel.CRITICAL,
                                "message": f"Dangerous function call: {node.func.id}",
                                "line": node.lineno,
                                "filename": filename
                            })
                
                # Check for attribute access to dangerous modules
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id in self.DANGEROUS_IMPORTS:
                            issues.append({
                                "level": SecurityLevel.MEDIUM,
                                "message": f"Access to potentially dangerous module: {node.value.id}.{node.attr}",
                                "line": node.lineno,
                                "filename": filename
                            })
        
        except SyntaxError as e:
            issues.append({
                "level": SecurityLevel.HIGH,
                "message": f"Python syntax error: {e}",
                "line": e.lineno,
                "filename": filename
            })
        
        return issues
    
    def validate_package_structure(self, package_data: bytes) -> List[Dict[str, Any]]:
        """Validate package structure for security issues"""
        issues = []
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(package_data)
            tmp_file.flush()
            
            try:
                # Try to extract as tar.gz
                with tarfile.open(tmp_file.name, 'r:gz') as tar:
                    members = tar.getmembers()
                    
                    for member in members:
                        # Check for path traversal
                        if '..' in member.name or member.name.startswith('/'):
                            issues.append({
                                "level": SecurityLevel.CRITICAL,
                                "message": f"Path traversal detected: {member.name}",
                                "details": "Package contains files outside extraction directory"
                            })
                        
                        # Check for suspicious file extensions
                        if member.name.endswith(('.exe', '.dll', '.so', '.dylib')):
                            issues.append({
                                "level": SecurityLevel.HIGH,
                                "message": f"Executable file detected: {member.name}",
                                "details": "Package contains binary executable files"
                            })
                        
                        # Check file size (bomb protection)
                        if member.size > 100 * 1024 * 1024:  # 100MB
                            issues.append({
                                "level": SecurityLevel.MEDIUM,
                                "message": f"Large file detected: {member.name} ({member.size} bytes)",
                                "details": "Package contains unusually large files"
                            })
            
            except tarfile.TarError:
                # Try as zip file
                try:
                    with zipfile.ZipFile(tmp_file.name, 'r') as zip_file:
                        for info in zip_file.infolist():
                            # Check for path traversal
                            if '..' in info.filename or info.filename.startswith('/'):
                                issues.append({
                                    "level": SecurityLevel.CRITICAL,
                                    "message": f"Path traversal detected: {info.filename}",
                                    "details": "Package contains files outside extraction directory"
                                })
                
                except zipfile.BadZipFile:
                    issues.append({
                        "level": SecurityLevel.HIGH,
                        "message": "Invalid package format",
                        "details": "Package is not a valid tar.gz or zip file"
                    })
        
        return issues
    
    def analyze_package_python_files(self, package_data: bytes) -> List[Dict[str, Any]]:
        """Analyze Python files in package for security issues"""
        issues = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract package
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(package_data)
                tmp_file.flush()
                
                try:
                    with tarfile.open(tmp_file.name, 'r:gz') as tar:
                        tar.extractall(temp_path)
                except tarfile.TarError:
                    try:
                        with zipfile.ZipFile(tmp_file.name, 'r') as zip_file:
                            zip_file.extractall(temp_path)
                    except zipfile.BadZipFile:
                        return issues
                
                # Analyze Python files
                for py_file in temp_path.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            code = f.read()
                            file_issues = self.analyze_python_code(code, str(py_file.relative_to(temp_path)))
                            issues.extend(file_issues)
                    except Exception as e:
                        issues.append({
                            "level": SecurityLevel.MEDIUM,
                            "message": f"Could not analyze file {py_file.name}: {e}",
                            "details": "File analysis failed"
                        })
        
        return issues


class ModuleValidator:
    """Complete module validator"""
    
    def __init__(self, 
                 available_modules: Optional[List[str]] = None,
                 security_level: SecurityLevel = SecurityLevel.MEDIUM):
        self.dependency_validator = DependencyValidator(available_modules)
        self.security_validator = SecurityValidator(security_level)
        
    def validate_manifest(self, manifest_dict: Dict[str, Any]) -> ValidationResult:
        """Validate module manifest"""
        result = ValidationResult()
        
        # Basic manifest validation
        is_valid, errors = ManifestValidator.validate_manifest_dict(manifest_dict)
        if not is_valid:
            for error in errors:
                result.add_error(f"Manifest validation: {error}")
            return result
        
        # Create manifest object
        manifest = ModuleManifest(**manifest_dict)
        
        # Security checks on manifest
        security_warnings = ManifestValidator.check_security_requirements(manifest)
        for warning in security_warnings:
            result.add_security_issue(SecurityLevel.MEDIUM, warning)
        
        # Validate dependencies
        dependency_issues = self.dependency_validator.validate_dependencies(manifest)
        for issue in dependency_issues:
            result.add_dependency_issue(issue)
        
        return result
    
    def validate_package(self, package_data: bytes, manifest: ModuleManifest) -> ValidationResult:
        """Validate module package"""
        result = ValidationResult()
        
        # Basic package structure validation
        structure_issues = self.security_validator.validate_package_structure(package_data)
        for issue in structure_issues:
            result.add_security_issue(
                SecurityLevel(issue["level"]), 
                issue["message"], 
                issue.get("details")
            )
        
        # Analyze Python code in package
        if not result.security_issues or all(issue["level"] != SecurityLevel.CRITICAL for issue in result.security_issues):
            code_issues = self.security_validator.analyze_package_python_files(package_data)
            for issue in code_issues:
                result.add_security_issue(
                    SecurityLevel(issue["level"]), 
                    issue["message"],
                    issue.get("details")
                )
        
        # Package integrity check
        package_hash = hashlib.sha256(package_data).hexdigest()
        result.add_warning(f"Package hash: {package_hash}")
        
        return result
    
    def validate_complete_module(
        self, 
        manifest_dict: Dict[str, Any], 
        package_data: Optional[bytes] = None
    ) -> ValidationResult:
        """Validate complete module (manifest + package)"""
        result = ValidationResult()
        
        # Validate manifest
        manifest_result = self.validate_manifest(manifest_dict)
        result.errors.extend(manifest_result.errors)
        result.warnings.extend(manifest_result.warnings)
        result.security_issues.extend(manifest_result.security_issues)
        result.dependency_issues.extend(manifest_result.dependency_issues)
        
        # If manifest is invalid, don't validate package
        if not manifest_result.is_valid:
            result.is_valid = False
            return result
        
        # Validate package if provided
        if package_data:
            manifest = ModuleManifest(**manifest_dict)
            package_result = self.validate_package(package_data, manifest)
            result.errors.extend(package_result.errors)
            result.warnings.extend(package_result.warnings)
            result.security_issues.extend(package_result.security_issues)
        
        # Update overall validity
        result.is_valid = len(result.errors) == 0
        
        return result