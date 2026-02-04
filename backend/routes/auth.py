"""
Authentication Routes
Handles user signup, login, and account management with JWT tokens
"""

from fastapi import APIRouter, HTTPException, status, Depends
from schemas import UserSignup, UserLogin, AuthResponse, ErrorResponse
from services.auth_service import auth_service
from services.jwt_service import create_access_token
from middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(request: UserSignup):
    """User signup endpoint - Creates account and returns JWT token"""
    try:
        logger.info(f"📝 Signup request: {request.username}")
        
        result = await auth_service.signup(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        if result.get("success"):
            user_id = result.get("user_id")
            # Generate JWT token
            token = create_access_token(user_id)
            
            logger.info(f"✅ User created: {request.username}, token generated")
            return AuthResponse(
                success=True,
                message=result.get("message"),
                user=result.get("user"),
                user_id=user_id,
                token=token
            )
        else:
            logger.warning(f"❌ Signup failed: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: UserLogin):
    """User login endpoint - Authenticates and returns JWT token"""
    try:
        logger.info(f"🔐 Login request: {request.username}")
        
        result = await auth_service.login(
            username=request.username,
            password=request.password
        )
        
        if result.get("success"):
            user_id = result.get("user_id")
            # Generate JWT token
            token = create_access_token(user_id)
            
            logger.info(f"✅ User logged in: {request.username}, token generated")
            return AuthResponse(
                success=True,
                message=result.get("message"),
                user=result.get("user"),
                user_id=user_id,
                token=token
            )
        else:
            logger.warning(f"❌ Login failed: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/user/{user_id}", response_model=AuthResponse)
async def get_user(user_id: int, current_user_id: int = Depends(get_current_user)):
    """Get user information - Requires JWT authentication"""
    try:
        logger.info(f"👤 Getting user info: {user_id}")
        
        user = await auth_service.get_user_by_id(user_id)
        
        if user:
            logger.info(f"✅ User retrieved: {user_id}")
            return AuthResponse(
                success=True,
                message="User found",
                user=user,
                user_id=user.get("id")
            )
        else:
            logger.warning(f"❌ User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get user error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )
