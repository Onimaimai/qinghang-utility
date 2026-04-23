from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User, Credential
from schemas import UserCreate, UserResponse, Token
from security import get_password_hash, verify_password
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_DAYS

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建新用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        pushplus_token=user.pushplus_token,
        balance_threshold=user.balance_threshold,
        water_balance_threshold=user.water_balance_threshold,
        created_at=user.created_at,
        has_credential=False
    )


@router.post("/login", response_model=Token)
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )

    # 设置 HttpOnly Cookie，有效期 365 天
    response.set_cookie(
        key="token",
        value=access_token,
        max_age=365 * 24 * 60 * 60,  # 365 天
        httponly=True,
        samesite="lax",
        path="/"
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    """登出，清除 cookie"""
    response.delete_cookie(key="token", path="/")
    return {"message": "已登出"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    has_credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first() is not None

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        pushplus_token=current_user.pushplus_token,
        balance_threshold=current_user.balance_threshold,
        water_balance_threshold=current_user.water_balance_threshold,
        created_at=current_user.created_at,
        has_credential=has_credential
    )
