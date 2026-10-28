from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Institution
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.security import (
    create_access_token, get_current_user, AuthenticatedUser
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user with username and return signed JWT token.
    Supports predefined demo roles for evaluation without mandatory Keycloak running.
    """
    username = login_data.username.strip()
    user = db.query(User).filter(User.username == username).first()

    # If demo login or user not found, support standard demo accounts
    if not user:
        # Predefined demo accounts
        demo_accounts = {
            "aicte_admin": ("aicte_admin", "AICTE National Administrator", None),
            "inst_admin": ("institution_admin", "Institute Director", "AICTE-1-001"),
            "inst_operator": ("institution_operator", "Institute Registrar / Operator", "AICTE-1-001"),
            "verifier": ("verifier", "Credential Verification Officer", None),
            "auditor": ("auditor", "Internal Security Auditor", None),
        }
        if username in demo_accounts:
            role, full_name, inst_code = demo_accounts[username]
            inst_id = None
            if inst_code:
                inst = db.query(Institution).filter(Institution.aicte_code == inst_code).first()
                if inst:
                    inst_id = inst.id

            user = User(
                username=username,
                email=f"{username}@aicte.gov.in",
                full_name=full_name,
                role=role,
                institution_id=inst_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "institution_id": str(user.institution_id) if user.institution_id else None
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return authenticated user profile."""
    user = db.query(User).filter(User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User record not found")
    return UserResponse.model_validate(user)
