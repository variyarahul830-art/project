"""
Authentication Service
Handles user signup, login, and password management
Future: JWT token generation and validation
"""

import logging
from typing import Optional, Dict, Any
import hashlib
import secrets
from services import hasura_client

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password with salt
        Future: Can be replaced with bcrypt for production
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password with salt
        """
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, pwd_hash = password_hash.split('$')
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return computed_hash.hex() == pwd_hash
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    async def signup(username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Create new user account
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            
        Returns:
            Dict with success status and user data
        """
        try:
            # Check if username already exists
            existing_user = await hasura_client.get_user_by_username(username)
            if existing_user:
                logger.warning(f"Signup failed: Username '{username}' already exists")
                return {
                    "success": False,
                    "message": "Username already exists",
                    "error_code": "USERNAME_EXISTS"
                }
            
            # Check if email already exists
            existing_email = await hasura_client.get_user_by_email(email)
            if existing_email:
                logger.warning(f"Signup failed: Email '{email}' already exists")
                return {
                    "success": False,
                    "message": "Email already registered",
                    "error_code": "EMAIL_EXISTS"
                }
            
            # Hash password
            password_hash = AuthService.hash_password(password)
            
            # Create user
            user = await hasura_client.create_user(
                username=username,
                email=email,
                password_hash=password_hash
            )
            
            if user:
                logger.info(f"✅ User signed up: {username}")
                return {
                    "success": True,
                    "message": "User created successfully",
                    "user": user,
                    "user_id": user.get("id")
                }
            else:
                logger.error(f"Failed to create user: {username}")
                return {
                    "success": False,
                    "message": "Failed to create user",
                    "error_code": "USER_CREATION_FAILED"
                }
                
        except Exception as e:
            logger.error(f"Signup error: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Signup failed: {str(e)}",
                "error_code": "SIGNUP_ERROR"
            }
    
    @staticmethod
    async def login(username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate session
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            Dict with success status and user data
        """
        try:
            # Try to find user by username first, then by email
            user = await hasura_client.get_user_by_username(username)
            if not user:
                user = await hasura_client.get_user_by_email(username)
            
            if not user:
                logger.warning(f"Login failed: User '{username}' not found")
                return {
                    "success": False,
                    "message": "Invalid username or password",
                    "error_code": "INVALID_CREDENTIALS"
                }
            
            # Check if user is active
            if not user.get("is_active"):
                logger.warning(f"Login failed: User '{username}' is inactive")
                return {
                    "success": False,
                    "message": "User account is inactive",
                    "error_code": "USER_INACTIVE"
                }
            
            # Verify password
            if not AuthService.verify_password(password, user.get("password_hash", "")):
                logger.warning(f"Login failed: Invalid password for '{username}'")
                return {
                    "success": False,
                    "message": "Invalid username or password",
                    "error_code": "INVALID_CREDENTIALS"
                }
            
            logger.info(f"✅ User logged in: {username}")
            
            # Return user info (without password hash)
            user_response = {
                "id": user.get("id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_active": user.get("is_active"),
                "created_at": user.get("created_at")
            }
            
            return {
                "success": True,
                "message": "Login successful",
                "user": user_response,
                "user_id": user.get("id")
                # Future: Add JWT token here
                # "token": generate_jwt_token(user.get("id"))
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Login failed: {str(e)}",
                "error_code": "LOGIN_ERROR"
            }
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None
        """
        try:
            user = await hasura_client.get_user_by_id(user_id)
            if user:
                # Remove password hash from response
                user.pop("password_hash", None)
                return user
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None


# Create service instance
auth_service = AuthService()
