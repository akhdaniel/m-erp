"""
Security validation script - comprehensive security testing and reporting.
Runs all security tests and generates a security assessment report.
"""

import pytest
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class SecurityTestResult:
    """Container for security test results."""
    
    def __init__(self):
        self.passed_tests: List[str] = []
        self.failed_tests: List[str] = []
        self.skipped_tests: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.security_features: Dict[str, bool] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.start_time: datetime = datetime.utcnow()
        self.end_time: datetime = None
        
    def add_passed_test(self, test_name: str):
        """Add a passed test."""
        self.passed_tests.append(test_name)
        
    def add_failed_test(self, test_name: str):
        """Add a failed test."""
        self.failed_tests.append(test_name)
        
    def add_skipped_test(self, test_name: str):
        """Add a skipped test."""
        self.skipped_tests.append(test_name)
        
    def add_error(self, error: str):
        """Add an error."""
        self.errors.append(error)
        
    def add_warning(self, warning: str):
        """Add a warning."""
        self.warnings.append(warning)
        
    def set_feature_status(self, feature: str, status: bool):
        """Set security feature status."""
        self.security_features[feature] = status
        
    def set_performance_metric(self, metric: str, value: float):
        """Set performance metric."""
        self.performance_metrics[metric] = value
        
    def finish(self):
        """Mark validation as finished."""
        self.end_time = datetime.utcnow()
        
    @property
    def duration(self) -> float:
        """Get test duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    @property
    def total_tests(self) -> int:
        """Get total number of tests."""
        return len(self.passed_tests) + len(self.failed_tests) + len(self.skipped_tests)
        
    @property
    def pass_rate(self) -> float:
        """Get test pass rate."""
        if self.total_tests == 0:
            return 0.0
        return len(self.passed_tests) / self.total_tests * 100
        
    @property
    def security_score(self) -> float:
        """Calculate overall security score."""
        if not self.security_features:
            return 0.0
            
        enabled_features = sum(1 for status in self.security_features.values() if status)
        return enabled_features / len(self.security_features) * 100


class SecurityValidator:
    """Main security validation class."""
    
    def __init__(self):
        self.result = SecurityTestResult()
        
    def run_security_tests(self) -> SecurityTestResult:
        """Run comprehensive security tests."""
        print("🔐 Starting Security Validation...")
        print("=" * 50)
        
        # Run different test categories
        self._run_middleware_tests()
        self._run_integration_tests()
        self._run_e2e_security_tests()
        self._run_audit_tests()
        self._run_lockout_tests()
        self._validate_security_features()
        self._check_performance()
        
        self.result.finish()
        return self.result
        
    def _run_middleware_tests(self):
        """Run middleware integration tests."""
        print("\n🔧 Testing Security Middleware...")
        
        try:
            # Run middleware tests
            exit_code = pytest.main([
                "tests/test_middleware_integration.py",
                "-v",
                "--tb=short",
                "-q"
            ])
            
            if exit_code == 0:
                self.result.add_passed_test("Middleware Integration")
                self.result.set_feature_status("Security Middleware", True)
                print("✅ Middleware tests passed")
            else:
                self.result.add_failed_test("Middleware Integration")
                self.result.set_feature_status("Security Middleware", False)
                print("❌ Middleware tests failed")
                
        except Exception as e:
            self.result.add_error(f"Middleware test error: {str(e)}")
            print(f"⚠️ Middleware test error: {str(e)}")
            
    def _run_integration_tests(self):
        """Run security integration tests."""
        print("\n🔗 Testing Security Integration...")
        
        try:
            exit_code = pytest.main([
                "tests/test_security_integration.py",
                "-v",
                "--tb=short",
                "-q"
            ])
            
            if exit_code == 0:
                self.result.add_passed_test("Security Integration")
                self.result.set_feature_status("Security Integration", True)
                print("✅ Integration tests passed")
            else:
                self.result.add_failed_test("Security Integration")
                self.result.set_feature_status("Security Integration", False)
                print("❌ Integration tests failed")
                
        except Exception as e:
            self.result.add_error(f"Integration test error: {str(e)}")
            print(f"⚠️ Integration test error: {str(e)}")
            
    def _run_e2e_security_tests(self):
        """Run end-to-end security tests."""
        print("\n🎯 Testing End-to-End Security...")
        
        try:
            exit_code = pytest.main([
                "tests/test_security_e2e.py",
                "-v",
                "--tb=short",
                "-q"
            ])
            
            if exit_code == 0:
                self.result.add_passed_test("E2E Security")
                self.result.set_feature_status("Attack Protection", True)
                print("✅ E2E security tests passed")
            else:
                self.result.add_failed_test("E2E Security")
                self.result.set_feature_status("Attack Protection", False)
                print("❌ E2E security tests failed")
                
        except Exception as e:
            self.result.add_error(f"E2E test error: {str(e)}")
            print(f"⚠️ E2E test error: {str(e)}")
            
    def _run_audit_tests(self):
        """Run audit logging tests."""
        print("\n📋 Testing Audit Logging...")
        
        try:
            exit_code = pytest.main([
                "tests/test_audit_service.py",
                "tests/test_audit_middleware.py",
                "tests/test_audit_endpoints.py",
                "-v",
                "--tb=short",
                "-q"
            ])
            
            if exit_code == 0:
                self.result.add_passed_test("Audit Logging")
                self.result.set_feature_status("Audit Logging", True)
                print("✅ Audit logging tests passed")
            else:
                self.result.add_failed_test("Audit Logging")
                self.result.set_feature_status("Audit Logging", False)
                print("❌ Audit logging tests failed")
                
        except Exception as e:
            self.result.add_error(f"Audit test error: {str(e)}")
            print(f"⚠️ Audit test error: {str(e)}")
            
    def _run_lockout_tests(self):
        """Run account lockout tests."""
        print("\n🔒 Testing Account Lockout...")
        
        try:
            exit_code = pytest.main([
                "tests/test_account_lockout.py",
                "-v",
                "--tb=short",
                "-q"
            ])
            
            if exit_code == 0:
                self.result.add_passed_test("Account Lockout")
                self.result.set_feature_status("Account Lockout", True)
                print("✅ Account lockout tests passed")
            else:
                self.result.add_failed_test("Account Lockout")
                self.result.set_feature_status("Account Lockout", False)
                print("❌ Account lockout tests failed")
                
        except Exception as e:
            self.result.add_error(f"Lockout test error: {str(e)}")
            print(f"⚠️ Lockout test error: {str(e)}")
            
    def _validate_security_features(self):
        """Validate security feature configuration."""
        print("\n🛡️ Validating Security Features...")
        
        try:
            from app.core.config import settings
            
            # Check security configurations
            security_checks = {
                "Rate Limiting": hasattr(settings, 'rate_limiting_enabled') and settings.rate_limiting_enabled,
                "Audit Logging": hasattr(settings, 'audit_logging_enabled') and settings.audit_logging_enabled,
                "Redis Available": hasattr(settings, 'redis_url') and settings.redis_url,
                "Debug Disabled": not settings.debug if hasattr(settings, 'debug') else True,
                "Secure JWT": len(settings.secret_key) >= 32 if hasattr(settings, 'secret_key') else False,
            }
            
            for feature, enabled in security_checks.items():
                self.result.set_feature_status(feature, enabled)
                if enabled:
                    print(f"✅ {feature}")
                else:
                    print(f"❌ {feature}")
                    self.result.add_warning(f"{feature} is not properly configured")
                    
        except Exception as e:
            self.result.add_error(f"Feature validation error: {str(e)}")
            print(f"⚠️ Feature validation error: {str(e)}")
            
    def _check_performance(self):
        """Check security performance metrics."""
        print("\n⚡ Checking Security Performance...")
        
        try:
            from fastapi.testclient import TestClient
            from app.main import app
            
            client = TestClient(app)
            
            # Test response times with security middleware
            start_time = time.time()
            
            # Make test requests
            for i in range(10):
                response = client.get("/health")
                assert response.status_code == 200
                
            end_time = time.time()
            avg_response_time = (end_time - start_time) / 10
            
            self.result.set_performance_metric("Average Response Time", avg_response_time)
            
            # Test security header overhead
            start_time = time.time()
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "wrong"
            })
            end_time = time.time()
            
            security_overhead = end_time - start_time
            self.result.set_performance_metric("Security Overhead", security_overhead)
            
            # Verify security headers are present
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-Request-ID",
                "X-Response-Time"
            ]
            
            headers_present = all(header in response.headers for header in required_headers)
            self.result.set_feature_status("Security Headers", headers_present)
            
            print(f"✅ Average response time: {avg_response_time:.3f}s")
            print(f"✅ Security overhead: {security_overhead:.3f}s")
            print(f"✅ Security headers: {'Present' if headers_present else 'Missing'}")
            
        except Exception as e:
            self.result.add_error(f"Performance check error: {str(e)}")
            print(f"⚠️ Performance check error: {str(e)}")
            
    def generate_report(self, output_file: str = "security_report.json"):
        """Generate comprehensive security report."""
        report = {
            "security_validation_report": {
                "timestamp": self.result.start_time.isoformat(),
                "duration_seconds": self.result.duration,
                "summary": {
                    "total_tests": self.result.total_tests,
                    "passed_tests": len(self.result.passed_tests),
                    "failed_tests": len(self.result.failed_tests),
                    "skipped_tests": len(self.result.skipped_tests),
                    "pass_rate_percent": round(self.result.pass_rate, 2),
                    "security_score_percent": round(self.result.security_score, 2)
                },
                "test_results": {
                    "passed": self.result.passed_tests,
                    "failed": self.result.failed_tests,
                    "skipped": self.result.skipped_tests
                },
                "security_features": self.result.security_features,
                "performance_metrics": self.result.performance_metrics,
                "issues": {
                    "errors": self.result.errors,
                    "warnings": self.result.warnings
                },
                "recommendations": self._generate_recommendations()
            }
        }
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on test results."""
        recommendations = []
        
        # Check for failed tests
        if self.result.failed_tests:
            recommendations.append(
                f"Address {len(self.result.failed_tests)} failed security tests before production deployment"
            )
            
        # Check security features
        disabled_features = [
            feature for feature, enabled in self.result.security_features.items() 
            if not enabled
        ]
        
        if disabled_features:
            recommendations.append(
                f"Enable disabled security features: {', '.join(disabled_features)}"
            )
            
        # Check performance
        if "Average Response Time" in self.result.performance_metrics:
            avg_time = self.result.performance_metrics["Average Response Time"]
            if avg_time > 1.0:
                recommendations.append(
                    f"Optimize performance - average response time is {avg_time:.3f}s"
                )
                
        # Check errors and warnings
        if self.result.errors:
            recommendations.append(
                f"Resolve {len(self.result.errors)} security errors before deployment"
            )
            
        if self.result.warnings:
            recommendations.append(
                f"Review {len(self.result.warnings)} security warnings"
            )
            
        # Security score recommendations
        if self.result.security_score < 80:
            recommendations.append(
                "Security score is below 80% - review and improve security configuration"
            )
            
        return recommendations
        
    def print_summary_report(self):
        """Print a summary security report to console."""
        print("\n" + "=" * 60)
        print("🔐 SECURITY VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Test Results:")
        print(f"   Total Tests: {self.result.total_tests}")
        print(f"   Passed: {len(self.result.passed_tests)} ✅")
        print(f"   Failed: {len(self.result.failed_tests)} ❌")
        print(f"   Skipped: {len(self.result.skipped_tests)} ⏭️")
        print(f"   Pass Rate: {self.result.pass_rate:.1f}%")
        
        print(f"\n🛡️ Security Score: {self.result.security_score:.1f}%")
        
        print(f"\n🔧 Security Features:")
        for feature, enabled in self.result.security_features.items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
            
        print(f"\n⚡ Performance:")
        for metric, value in self.result.performance_metrics.items():
            print(f"   {metric}: {value:.3f}s")
            
        if self.result.errors:
            print(f"\n🚨 Errors ({len(self.result.errors)}):")
            for error in self.result.errors:
                print(f"   ❌ {error}")
                
        if self.result.warnings:
            print(f"\n⚠️ Warnings ({len(self.result.warnings)}):")
            for warning in self.result.warnings:
                print(f"   ⚠️ {warning}")
                
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
                
        print(f"\n⏱️ Total Duration: {self.result.duration:.2f} seconds")
        
        # Overall assessment
        if self.result.pass_rate >= 95 and self.result.security_score >= 90:
            print(f"\n🎉 SECURITY ASSESSMENT: EXCELLENT")
            print("   System is ready for production deployment")
        elif self.result.pass_rate >= 85 and self.result.security_score >= 80:
            print(f"\n✅ SECURITY ASSESSMENT: GOOD")
            print("   System has good security posture with minor improvements needed")
        elif self.result.pass_rate >= 70 and self.result.security_score >= 70:
            print(f"\n⚠️ SECURITY ASSESSMENT: FAIR")
            print("   System needs security improvements before production")
        else:
            print(f"\n🚨 SECURITY ASSESSMENT: POOR")
            print("   System has significant security issues - DO NOT DEPLOY")
            
        print("=" * 60)


def main():
    """Main function to run security validation."""
    validator = SecurityValidator()
    
    try:
        # Run all security tests
        result = validator.run_security_tests()
        
        # Generate reports
        report_data = validator.generate_report()
        validator.print_summary_report()
        
        print(f"\n📄 Detailed report saved to: security_report.json")
        
        # Exit with appropriate code
        if result.pass_rate >= 90 and result.security_score >= 80:
            exit(0)  # Success
        else:
            exit(1)  # Security issues found
            
    except Exception as e:
        print(f"\n🚨 Security validation failed with error: {str(e)}")
        exit(2)  # Validation error


if __name__ == "__main__":
    main()