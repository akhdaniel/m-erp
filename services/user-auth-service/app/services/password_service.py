"""
Enhanced password service with comprehensive policy enforcement.
Provides secure password hashing, strength validation, and policy compliance.
"""

import bcrypt
import re
import math
from datetime import datetime, timedelta
from typing import Union, List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc


class PasswordPolicyConfig:
  """Password policy configuration."""
  
  # Length requirements
  MIN_LENGTH = 8
  MAX_LENGTH = 128
  RECOMMENDED_LENGTH = 12
  
  # Character requirements
  REQUIRE_UPPERCASE = True
  REQUIRE_LOWERCASE = True
  REQUIRE_DIGITS = True
  REQUIRE_SPECIAL_CHARS = True
  MIN_SPECIAL_CHARS = 1
  
  # Advanced requirements
  MIN_UNIQUE_CHARS = 6
  MAX_REPEATED_CHARS = 2
  MAX_SEQUENTIAL_CHARS = 3
  
  # History and reuse
  PASSWORD_HISTORY_COUNT = 5
  PASSWORD_MIN_AGE_HOURS = 24
  
  # Complexity scoring
  MIN_COMPLEXITY_SCORE = 60
  
  # Common patterns to avoid
  FORBIDDEN_PATTERNS = [
    r'(.)\1{3,}',  # 4+ repeated characters
    r'(012|123|234|345|456|567|678|789)',  # Sequential numbers
    r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
    r'(qwer|asdf|zxcv|qazw|wsxe|edcr)',  # Keyboard patterns
  ]
  
  # Common weak passwords
  COMMON_PASSWORDS = {
    'password', '123456', 'password123', 'admin', 'qwerty', 'letmein',
    'welcome', 'monkey', '1234567890', 'password1', 'abc123', 'Password1',
    'iloveyou', 'princess', 'rockyou', '12345678', 'abc123', 'nicole',
    'daniel', 'babygirl', 'michael', 'ashley', 'login', 'sunshine'
  }


class PasswordService:
  """Enhanced password service with comprehensive policy enforcement."""
  
  # Number of salt rounds for bcrypt (12 is a good balance of security and performance)
  SALT_ROUNDS = 12
  
  @classmethod
  def hash_password(cls, password: str) -> str:
    """
    Hash a password using bcrypt with salt.
    
    Args:
      password: Plain text password to hash
      
    Returns:
      str: Hashed password string
      
    Raises:
      ValueError: If password is empty or None
    """
    if not password:
      raise ValueError("Password cannot be empty")
    
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=cls.SALT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')
  
  @classmethod
  def verify_password(cls, password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
      password: Plain text password to verify
      password_hash: Hashed password from database
      
    Returns:
      bool: True if password matches, False otherwise
    """
    if not password or not password_hash:
      return False
    
    try:
      # Convert to bytes
      password_bytes = password.encode('utf-8')
      hash_bytes = password_hash.encode('utf-8')
      
      # Verify password
      return bcrypt.checkpw(password_bytes, hash_bytes)
    
    except (ValueError, TypeError):
      # Handle any bcrypt errors (invalid hash format, etc.)
      return False
  
  @classmethod
  def is_password_strong(cls, password: str) -> bool:
    """
    Check if password meets comprehensive strength requirements.
    
    Args:
      password: Password to check
      
    Returns:
      bool: True if password meets all policy requirements
    """
    if not password:
      return False
    
    validation_result = cls.validate_password_policy(password)
    return validation_result["is_valid"]
  
  @classmethod
  def validate_password_policy(cls, password: str, user_context: Optional[Dict[str, str]] = None) -> Dict[str, any]:
    """
    Comprehensive password policy validation.
    
    Args:
      password: Password to validate
      user_context: Optional user context (email, name) for personal info checks
      
    Returns:
      Dict containing validation results and feedback
    """
    if not password:
      return {
        "is_valid": False,
        "score": 0,
        "feedback": ["Password is required"],
        "strength": "Very Weak",
        "violations": ["empty_password"]
      }
    
    feedback = []
    violations = []
    score = 0
    
    # Length validation
    if len(password) < PasswordPolicyConfig.MIN_LENGTH:
      feedback.append(f"Password must be at least {PasswordPolicyConfig.MIN_LENGTH} characters long")
      violations.append("min_length")
    elif len(password) >= PasswordPolicyConfig.RECOMMENDED_LENGTH:
      score += 20
    else:
      score += 10
    
    if len(password) > PasswordPolicyConfig.MAX_LENGTH:
      feedback.append(f"Password must not exceed {PasswordPolicyConfig.MAX_LENGTH} characters")
      violations.append("max_length")
      
    # Character type requirements
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = sum(1 for c in password if c in '!@#$%^&*()_+-=[]{}|;:,.<>?')
    
    if PasswordPolicyConfig.REQUIRE_UPPERCASE and not has_upper:
      feedback.append("Password must contain at least one uppercase letter")
      violations.append("missing_uppercase")
    elif has_upper:
      score += 10
      
    if PasswordPolicyConfig.REQUIRE_LOWERCASE and not has_lower:
      feedback.append("Password must contain at least one lowercase letter")
      violations.append("missing_lowercase")
    elif has_lower:
      score += 10
      
    if PasswordPolicyConfig.REQUIRE_DIGITS and not has_digit:
      feedback.append("Password must contain at least one number")
      violations.append("missing_digit")
    elif has_digit:
      score += 10
      
    if PasswordPolicyConfig.REQUIRE_SPECIAL_CHARS and has_special < PasswordPolicyConfig.MIN_SPECIAL_CHARS:
      feedback.append(f"Password must contain at least {PasswordPolicyConfig.MIN_SPECIAL_CHARS} special character(s)")
      violations.append("missing_special")
    elif has_special >= PasswordPolicyConfig.MIN_SPECIAL_CHARS:
      score += 15
      
    # Advanced complexity checks
    unique_chars = len(set(password.lower()))
    if unique_chars < PasswordPolicyConfig.MIN_UNIQUE_CHARS:
      feedback.append(f"Password must contain at least {PasswordPolicyConfig.MIN_UNIQUE_CHARS} unique characters")
      violations.append("insufficient_unique_chars")
    else:
      score += 10
      
    # Check for repeated characters
    repeated_violations = cls._check_repeated_characters(password)
    if repeated_violations:
      feedback.extend(repeated_violations)
      violations.append("repeated_chars")
      
    # Check for sequential patterns
    sequential_violations = cls._check_sequential_patterns(password)
    if sequential_violations:
      feedback.extend(sequential_violations)
      violations.append("sequential_patterns")
      
    # Check for forbidden patterns
    pattern_violations = cls._check_forbidden_patterns(password)
    if pattern_violations:
      feedback.extend(pattern_violations)
      violations.append("forbidden_patterns")
      
    # Check for common passwords
    if password.lower() in PasswordPolicyConfig.COMMON_PASSWORDS:
      feedback.append("Password is too common and easily guessable")
      violations.append("common_password")
      score -= 30
      
    # Check for personal information
    if user_context:
      personal_violations = cls._check_personal_info(password, user_context)
      if personal_violations:
        feedback.extend(personal_violations)
        violations.append("personal_info")
        
    # Calculate complexity bonus
    complexity_bonus = cls._calculate_complexity_bonus(password)
    score += complexity_bonus
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    # Determine strength level
    strength = cls._get_strength_level(score)
    
    # Password is valid if no violations and meets minimum score
    is_valid = len(violations) == 0 and score >= PasswordPolicyConfig.MIN_COMPLEXITY_SCORE
    
    return {
      "is_valid": is_valid,
      "score": score,
      "feedback": feedback,
      "strength": strength,
      "violations": violations,
      "has_uppercase": has_upper,
      "has_lowercase": has_lower,
      "has_digits": has_digit,
      "has_special": has_special >= PasswordPolicyConfig.MIN_SPECIAL_CHARS,
      "unique_chars": unique_chars,
      "length": len(password)
    }
  
  @classmethod
  def generate_password_strength_feedback(cls, password: str, user_context: Optional[Dict[str, str]] = None) -> List[str]:
    """
    Generate comprehensive feedback on password strength.
    
    Args:
      password: Password to analyze
      user_context: Optional user context for personal info checks
      
    Returns:
      List[str]: List of feedback messages for improvement
    """
    if not password:
      return ["Password is required"]
    
    validation_result = cls.validate_password_policy(password, user_context)
    return validation_result["feedback"]
  
  @classmethod
  def _check_repeated_characters(cls, password: str) -> List[str]:
    """Check for excessive repeated characters."""
    violations = []
    
    # Count consecutive repeated characters
    i = 0
    while i < len(password):
      count = 1
      while i + count < len(password) and password[i] == password[i + count]:
        count += 1
      
      if count > PasswordPolicyConfig.MAX_REPEATED_CHARS:
        violations.append(f"Password contains too many repeated characters ({password[i]} repeated {count} times)")
        break
      
      i += count
    
    return violations
  
  @classmethod
  def _check_sequential_patterns(cls, password: str) -> List[str]:
    """Check for sequential character patterns."""
    violations = []
    password_lower = password.lower()
    
    # Check for ascending sequences
    for i in range(len(password_lower) - PasswordPolicyConfig.MAX_SEQUENTIAL_CHARS + 1):
      sequence = password_lower[i:i + PasswordPolicyConfig.MAX_SEQUENTIAL_CHARS]
      if cls._is_sequential(sequence):
        violations.append(f"Password contains sequential characters: {sequence}")
        break
    
    return violations
  
  @classmethod
  def _is_sequential(cls, sequence: str) -> bool:
    """Check if a sequence is sequential (ascending or descending)."""
    if len(sequence) < 3:
      return False
    
    # Check ascending
    ascending = all(ord(sequence[i]) == ord(sequence[i-1]) + 1 for i in range(1, len(sequence)))
    
    # Check descending
    descending = all(ord(sequence[i]) == ord(sequence[i-1]) - 1 for i in range(1, len(sequence)))
    
    return ascending or descending
  
  @classmethod
  def _check_forbidden_patterns(cls, password: str) -> List[str]:
    """Check for forbidden patterns using regex."""
    violations = []
    password_lower = password.lower()
    
    for pattern in PasswordPolicyConfig.FORBIDDEN_PATTERNS:
      if re.search(pattern, password_lower):
        violations.append("Password contains forbidden patterns (keyboard sequences or repeated characters)")
        break
    
    return violations
  
  @classmethod
  def _check_personal_info(cls, password: str, user_context: Dict[str, str]) -> List[str]:
    """Check if password contains personal information."""
    violations = []
    password_lower = password.lower()
    
    # Check against email
    if 'email' in user_context:
      email_parts = user_context['email'].lower().split('@')[0].split('.')
      for part in email_parts:
        if len(part) >= 3 and part in password_lower:
          violations.append("Password should not contain parts of your email address")
          break
    
    # Check against name components
    for field in ['first_name', 'last_name', 'name']:
      if field in user_context:
        name_lower = user_context[field].lower()
        if len(name_lower) >= 3 and name_lower in password_lower:
          violations.append("Password should not contain your name")
          break
    
    return violations
  
  @classmethod
  def _calculate_complexity_bonus(cls, password: str) -> int:
    """Calculate complexity bonus based on character variety and entropy."""
    bonus = 0
    
    # Character set variety bonus
    char_sets = 0
    if any(c.islower() for c in password):
      char_sets += 1
    if any(c.isupper() for c in password):
      char_sets += 1
    if any(c.isdigit() for c in password):
      char_sets += 1
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
      char_sets += 1
    
    bonus += char_sets * 5
    
    # Length bonus (beyond minimum)
    if len(password) > PasswordPolicyConfig.RECOMMENDED_LENGTH:
      bonus += min(10, len(password) - PasswordPolicyConfig.RECOMMENDED_LENGTH)
    
    # Entropy estimation
    entropy = cls._estimate_entropy(password)
    if entropy > 50:
      bonus += 10
    elif entropy > 40:
      bonus += 5
    
    return bonus
  
  @classmethod
  def _estimate_entropy(cls, password: str) -> float:
    """Estimate password entropy in bits."""
    if not password:
      return 0
    
    # Character set size estimation
    charset_size = 0
    if any(c.islower() for c in password):
      charset_size += 26
    if any(c.isupper() for c in password):
      charset_size += 26
    if any(c.isdigit() for c in password):
      charset_size += 10
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
      charset_size += 32
    
    if charset_size == 0:
      return 0
    
    # Basic entropy calculation
    entropy = len(password) * math.log2(charset_size)
    
    # Reduce entropy for repeated patterns
    unique_chars = len(set(password))
    if unique_chars < len(password):
      entropy *= (unique_chars / len(password))
    
    return entropy
  
  @classmethod
  def _get_strength_level(cls, score: int) -> str:
    """Get password strength level based on score."""
    if score >= 90:
      return "Very Strong"
    elif score >= 80:
      return "Strong"
    elif score >= 60:
      return "Moderate"
    elif score >= 40:
      return "Weak"
    else:
      return "Very Weak"
  
  @classmethod
  async def check_password_history(cls, db: AsyncSession, user_id: int, new_password: str) -> bool:
    """
    Check if password has been used recently.
    
    Args:
      db: Database session
      user_id: User ID to check
      new_password: New password to validate
      
    Returns:
      bool: True if password is acceptable (not in recent history)
    """
    try:
      # Import here to avoid circular imports
      from app.models.password_history import PasswordHistory
      
      # Get recent password hashes
      stmt = select(PasswordHistory.password_hash).where(
        PasswordHistory.user_id == user_id
      ).order_by(desc(PasswordHistory.created_at)).limit(PasswordPolicyConfig.PASSWORD_HISTORY_COUNT)
      
      result = await db.execute(stmt)
      recent_hashes = result.scalars().all()
      
      # Check if new password matches any recent password
      for old_hash in recent_hashes:
        if cls.verify_password(new_password, old_hash):
          return False
      
      return True
    
    except ImportError:
      # If password history model doesn't exist, allow password change
      return True
    except Exception:
      # On any error, allow password change (fail open for availability)
      return True
  
  @classmethod
  async def add_to_password_history(cls, db: AsyncSession, user_id: int, password_hash: str):
    """
    Add password hash to user's password history.
    
    Args:
      db: Database session
      user_id: User ID
      password_hash: Hashed password to store
    """
    try:
      from app.models.password_history import PasswordHistory
      
      # Add new password to history
      history_entry = PasswordHistory(
        user_id=user_id,
        password_hash=password_hash,
        created_at=datetime.utcnow()
      )
      
      db.add(history_entry)
      
      # Clean up old history entries (keep only configured count)
      old_entries_stmt = select(PasswordHistory).where(
        PasswordHistory.user_id == user_id
      ).order_by(desc(PasswordHistory.created_at)).offset(PasswordPolicyConfig.PASSWORD_HISTORY_COUNT)
      
      old_entries_result = await db.execute(old_entries_stmt)
      old_entries = old_entries_result.scalars().all()
      
      for old_entry in old_entries:
        await db.delete(old_entry)
      
      await db.commit()
    
    except ImportError:
      # If password history model doesn't exist, skip history tracking
      pass
    except Exception:
      # On any error, continue without history tracking
      pass
  
  @classmethod
  def generate_secure_password(cls, length: int = 12) -> str:
    """
    Generate a secure password that meets policy requirements.
    
    Args:
      length: Desired password length (minimum 12)
      
    Returns:
      str: Generated secure password
    """
    import secrets
    import string
    
    length = max(length, PasswordPolicyConfig.RECOMMENDED_LENGTH)
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    # Ensure at least one character from each required set
    password_chars = [
      secrets.choice(lowercase),
      secrets.choice(uppercase),
      secrets.choice(digits),
      secrets.choice(special)
    ]
    
    # Fill remaining length with random characters from all sets
    all_chars = lowercase + uppercase + digits + special
    for _ in range(length - 4):
      password_chars.append(secrets.choice(all_chars))
    
    # Shuffle the password characters
    secrets.SystemRandom().shuffle(password_chars)
    
    password = ''.join(password_chars)
    
    # Verify the generated password meets policy
    if cls.is_password_strong(password):
      return password
    else:
      # Recursively try again (very unlikely to be needed)
      return cls.generate_secure_password(length)
  
  @classmethod
  def get_password_policy_info(cls) -> Dict[str, any]:
    """
    Get current password policy information for display to users.
    
    Returns:
      Dict containing policy requirements
    """
    return {
      "requirements": {
        "min_length": PasswordPolicyConfig.MIN_LENGTH,
        "max_length": PasswordPolicyConfig.MAX_LENGTH,
        "recommended_length": PasswordPolicyConfig.RECOMMENDED_LENGTH,
        "require_uppercase": PasswordPolicyConfig.REQUIRE_UPPERCASE,
        "require_lowercase": PasswordPolicyConfig.REQUIRE_LOWERCASE,
        "require_digits": PasswordPolicyConfig.REQUIRE_DIGITS,
        "require_special_chars": PasswordPolicyConfig.REQUIRE_SPECIAL_CHARS,
        "min_special_chars": PasswordPolicyConfig.MIN_SPECIAL_CHARS,
        "min_unique_chars": PasswordPolicyConfig.MIN_UNIQUE_CHARS,
        "max_repeated_chars": PasswordPolicyConfig.MAX_REPEATED_CHARS,
        "password_history_count": PasswordPolicyConfig.PASSWORD_HISTORY_COUNT,
        "min_complexity_score": PasswordPolicyConfig.MIN_COMPLEXITY_SCORE
      },
      "guidelines": [
        f"Use at least {PasswordPolicyConfig.MIN_LENGTH} characters (recommended: {PasswordPolicyConfig.RECOMMENDED_LENGTH}+)",
        "Include uppercase and lowercase letters",
        "Include numbers and special characters",
        "Avoid personal information (name, email)",
        "Avoid common passwords and patterns",
        "Use unique passwords for different accounts"
      ],
      "forbidden": [
        "Personal information (name, email, birthday)",
        "Common passwords (password, 123456, qwerty)",
        "Keyboard patterns (qwerty, asdf, 123)",
        "Repeated characters (aaaa, 1111)",
        "Sequential patterns (abc, 123, xyz)"
      ]
    }