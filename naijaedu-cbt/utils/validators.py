"""
NaijaEdu CBT - Input Validators
Returns (is_valid: bool, message: str) tuples for all form fields.
"""

import re
from typing import Tuple


def validate_username(value: str) -> Tuple[bool, str]:
    value = value.strip()
    if not value:
        return False, "Username is required."
    if len(value) < 3:
        return False, "Username must be at least 3 characters."
    if len(value) > 20:
        return False, "Username must be at most 20 characters."
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        return False, "Username may only contain letters, numbers, and underscores."
    return True, ""


def validate_password(value: str) -> Tuple[bool, str]:
    if not value:
        return False, "Password is required."
    if len(value) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", value):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", value):
        return False, "Password must contain at least one number."
    return True, ""


def validate_login_password(value: str) -> Tuple[bool, str]:
    """Lighter check used only on the login screen."""
    if not value:
        return False, "Password is required."
    if len(value) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


def validate_full_name(value: str) -> Tuple[bool, str]:
    value = value.strip()
    if not value:
        return False, "Full name is required."
    if len(value) < 3:
        return False, "Full name must be at least 3 characters."
    return True, ""


def validate_email(value: str) -> Tuple[bool, str]:
    value = value.strip()
    if not value:
        return True, ""  # Email is optional
    pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
    if not re.fullmatch(pattern, value):
        return False, "Enter a valid email address."
    return True, ""


def validate_exam_number(value: str) -> Tuple[bool, str]:
    value = value.strip()
    if not value:
        return True, ""  # Optional field
    if not re.fullmatch(r"\d{8}[A-Za-z]{2}", value):
        return False, "Exam number must be 8 digits followed by 2 letters (e.g. 12345678AB)."
    return True, ""


def validate_confirm_password(password: str, confirm: str) -> Tuple[bool, str]:
    if not confirm:
        return False, "Please confirm your password."
    if password != confirm:
        return False, "Passwords do not match."
    return True, ""


def password_strength(value: str) -> str:
    """Return 'weak' | 'medium' | 'strong'."""
    if len(value) < 8:
        return "weak"
    has_upper   = bool(re.search(r"[A-Z]", value))
    has_digit   = bool(re.search(r"\d",   value))
    has_special = bool(re.search(r"[^A-Za-z0-9]", value))
    score = sum([has_upper, has_digit, has_special])
    if score >= 2:
        return "strong"
    return "medium"
