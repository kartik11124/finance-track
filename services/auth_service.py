"""Authentication and User Profile Service.
Handles secure password hashing, user registration, validation, and session verification.
"""

import re
from typing import Any, Dict, Optional, Tuple
from werkzeug.security import check_password_hash, generate_password_hash
from database.database import execute_insert, execute_one, execute_query, execute_update


EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def register_user(name: str, email: str, password: str) -> Tuple[bool, str, Optional[int]]:
    """Register a new user with hashed password and default profile.
    Returns: (success, message, user_id)
    """
    clean_name = name.strip()
    clean_email = email.strip().lower()

    if not clean_name:
        return False, "Full name cannot be empty.", None

    if not clean_email or not EMAIL_REGEX.match(clean_email):
        return False, "Please enter a valid email address.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    # Check for existing email
    existing = execute_one("SELECT id FROM users WHERE email = ?;", (clean_email,))
    if existing:
        return False, "An account with this email address already exists.", None

    # Secure password hashing (PBKDF2/scrypt via Werkzeug)
    hashed_pw = generate_password_hash(password, method="scrypt")

    user_id = execute_insert(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?);",
        (clean_name, clean_email, hashed_pw)
    )

    # Initialize default user profile
    execute_insert(
        """
        INSERT INTO user_profiles (user_id, risk_tolerance, investment_horizon, primary_goal, emergency_fund_months)
        VALUES (?, 'MEDIUM', 'LONG', 'Wealth Creation', 3);
        """,
        (user_id,)
    )

    return True, "Registration successful. You may now log in.", user_id


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticate user credentials.
    Returns: (success, message, user_dict)
    """
    clean_email = email.strip().lower()

    if not clean_email or not password:
        return False, "Email and password are required.", None

    user = execute_one(
        "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?;",
        (clean_email,)
    )

    if not user:
        return False, "Invalid email or password.", None

    if not check_password_hash(user["password_hash"], password):
        return False, "Invalid email or password.", None

    user_info = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"]
    }
    return True, "Authentication successful.", user_info


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user record by ID."""
    return execute_one("SELECT id, name, email, created_at FROM users WHERE id = ?;", (user_id,))


def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Retrieve user financial profile or create default if missing."""
    profile = execute_one(
        """
        SELECT risk_tolerance, investment_horizon, primary_goal, emergency_fund_months, updated_at
        FROM user_profiles
        WHERE user_id = ?;
        """,
        (user_id,)
    )
    if profile:
        return dict(profile)

    # If missing, create default
    execute_insert(
        """
        INSERT INTO user_profiles (user_id, risk_tolerance, investment_horizon, primary_goal, emergency_fund_months)
        VALUES (?, 'MEDIUM', 'LONG', 'Wealth Creation', 3);
        """,
        (user_id,)
    )
    return {
        "risk_tolerance": "MEDIUM",
        "investment_horizon": "LONG",
        "primary_goal": "Wealth Creation",
        "emergency_fund_months": 3
    }


def update_user_profile(
    user_id: int,
    risk_tolerance: str,
    investment_horizon: str,
    primary_goal: str,
    emergency_fund_months: int = 3
) -> bool:
    """Update risk tolerance and goals."""
    valid_risks = ("LOW", "MEDIUM", "HIGH")
    valid_horizons = ("SHORT", "MEDIUM", "LONG")

    risk = risk_tolerance.upper() if risk_tolerance.upper() in valid_risks else "MEDIUM"
    horizon = investment_horizon.upper() if investment_horizon.upper() in valid_horizons else "LONG"
    goal = primary_goal.strip() if primary_goal and primary_goal.strip() else "Wealth Creation"
    months = max(1, min(12, int(emergency_fund_months)))

    existing = execute_one("SELECT id FROM user_profiles WHERE user_id = ?;", (user_id,))
    if existing:
        execute_update(
            """
            UPDATE user_profiles
            SET risk_tolerance = ?, investment_horizon = ?, primary_goal = ?,
                emergency_fund_months = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?;
            """,
            (risk, horizon, goal, months, user_id)
        )
    else:
        execute_insert(
            """
            INSERT INTO user_profiles (user_id, risk_tolerance, investment_horizon, primary_goal, emergency_fund_months)
            VALUES (?, ?, ?, ?, ?);
            """,
            (user_id, risk, horizon, goal, months)
        )
    return True
