from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import (
    generate_session_token,
    set_auth_cookie,
    clear_auth_cookie,
    require_current_user,
    get_current_user_optional,
    hash_password,
    verify_password,
    verify_google_credential,
    exchange_google_code,
)
from app.services.user_service import user_service
from app.schemas.auth import (
    LoginRequest,
    GoogleAuthRequest,
    AuthResponse,
    LogoutResponse,
    RegisterRequest,
)
from app.schemas.user import UserResponse, UserCreate
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing learner by email and password.
    Supports secure PBKDF2 password verification.
    Preserves seamless demo access for pre-seeded learners.
    """
    clean_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(clean_email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No learner account found with email '{payload.email}'. Please verify your email or click Create account.",
        )

    # If the user has a password hash on file, verify it
    if user.password_hash:
        if not payload.password or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password. Please verify your credentials and try again.",
            )
    else:
        # Pre-seeded account without password hash yet (e.g. Alex Mercer demo account)
        # If password is provided, securely store its hash for subsequent logins
        if payload.password:
            user.password_hash = hash_password(payload.password)
            db.commit()

    token = generate_session_token(user.id)
    set_auth_cookie(response, token)

    return AuthResponse(
        user=user,
        token=token,
        message=f"Welcome back, {user.name}!",
        is_new_user=False,
        needs_onboarding=False,
    )


@router.post("/google", response_model=AuthResponse)
def google_sign_in(
    payload: GoogleAuthRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticate or register a learner via Google Identity Services (GIS).
    Accepts either a verified Google OpenID Connect ID token credential or an authorization code.
    Matches existing SkillPath users by email without creating duplicates.
    New learners start with a completely isolated, clean state without demo data.
    """
    claims = None
    if payload.credential:
        claims = verify_google_credential(payload.credential)
    elif payload.code:
        claims = exchange_google_code(payload.code, payload.redirect_uri)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid Google credential or authorization code is required for Google Sign-In.",
        )

    google_sub = claims.get("sub")
    email = (claims.get("email") or "").strip().lower()
    name = claims.get("name") or claims.get("given_name") or email.split("@")[0]
    picture = claims.get("picture")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Google account does not contain a verified email address.",
        )

    # 1. Existing Account Matching
    # Look for existing user by email or Google sub
    user = db.query(User).filter(
        (User.email.ilike(email)) | (User.google_id == google_sub)
    ).first()

    if user:
        # Existing account found: Link Google ID and avatar if not already stored
        updated = False
        if not user.google_id and google_sub:
            user.google_id = google_sub
            updated = True
        if picture and not user.avatar_url:
            user.avatar_url = picture
            updated = True
        if updated:
            db.commit()
            db.refresh(user)

        token = generate_session_token(user.id)
        set_auth_cookie(response, token)

        return AuthResponse(
            user=user,
            token=token,
            message=f"Welcome back, {user.name}!",
            is_new_user=False,
            needs_onboarding=False,
        )

    # 2. New Google Learner: Clean Initial State (ZERO Demo Data)
    new_user = User(
        name=name,
        email=email,
        experience_level="Intermediate",
        target_role_id=1,  # Default to primary Data Analyst target role
        weekly_learning_hours=10,
        learning_goal="Build verified competence and achieve career readiness",
        google_id=google_sub,
        avatar_url=picture,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = generate_session_token(new_user.id)
    set_auth_cookie(response, token)

    return AuthResponse(
        user=new_user,
        token=token,
        message="Account created successfully with Google. Please complete your learning profile.",
        is_new_user=True,
        needs_onboarding=True,
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response):
    """
    Terminate the active learner session and clear cookies.
    """
    clear_auth_cookie(response)
    return LogoutResponse(
        success=True,
        message="Logged out successfully.",
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(require_current_user)):
    """
    Retrieve currently authenticated learner profile.
    """
    return current_user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Register a new learner profile and immediately establish their authenticated session.
    Clean initial state without demo data.
    """
    clean_email = payload.email.strip().lower()
    existing = db.query(User).filter(User.email.ilike(clean_email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please sign in.",
        )

    try:
        user_create = UserCreate(
            name=payload.name,
            email=clean_email,
            experience_level=payload.experience_level or "Intermediate",
            target_role_id=payload.target_role_id,
            weekly_learning_hours=payload.weekly_learning_hours or 10,
            learning_goal=payload.learning_goal,
        )
        new_user = user_service.create_user(db, user_create)
        if payload.password:
            new_user.password_hash = hash_password(payload.password)
            db.commit()
            db.refresh(new_user)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )

    token = generate_session_token(new_user.id)
    set_auth_cookie(response, token)

    return AuthResponse(
        user=new_user,
        token=token,
        message="Account created successfully.",
        is_new_user=True,
        needs_onboarding=False,
    )
