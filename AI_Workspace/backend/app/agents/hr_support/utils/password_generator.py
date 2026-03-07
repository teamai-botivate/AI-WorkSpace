"""
Botivate HR Support - Password Generator Utility
Generates secure random passwords for employee auto-provisioning.
"""

import secrets
import string


def generate_secure_password(length: int = 12) -> str:
    """
    Generate a strong random password containing:
    - Uppercase letters
    - Lowercase letters
    - Digits
    - Special characters
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    # Ensure at least one of each category
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*"),
    ]
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)
