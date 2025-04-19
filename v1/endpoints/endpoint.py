from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from v1.models.user import User
from v1.schemas.user import UserCreate, UserRead, UserUpdate
from core.database import get_db
from core.security import hash_password, verify_password, get_current_user, create_access_token
from typing import List
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/token")

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/token",
    summary="Obtenir un token JWT",
    description="Authentifie un utilisateur et retourne un token JWT à utiliser dans les endpoints protégés.",
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    auth: str = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            return get_current_user(token, db)
        except Exception:
            return None
    return None

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur",
    description="Crée un nouvel utilisateur avec un email, un mot de passe et un rôle. L'email doit être unique. Seuls les admins peuvent créer des admins."
)
def create_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Crée un utilisateur et retourne ses informations publiques. Auth requis pour créer un admin (sauf si aucun admin n'existe)."""
    if user.role == "admin":
        admin_exists = db.query(User).filter(User.role == "admin").first()
        if not admin_exists:
            # Aucun admin n'existe, autoriser la création sans authentification
            pass
        else:
            current_user = get_current_user_optional(request, db)
            if not current_user or current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Seul un admin peut créer un autre admin.")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=True,
        role=user.role or "user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Récupérer un utilisateur par ID",
    description="Retourne les informations publiques d'un utilisateur à partir de son identifiant. Auth requis."
)
def get_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@router.get(
    "/",
    response_model=List[UserRead],
    summary="Lister les utilisateurs (admin seulement)",
    description="Retourne une liste paginée d'utilisateurs. Auth admin requis."
)
def list_users(
    skip: int = Query(0, ge=0, description="Nombre d'utilisateurs à ignorer (pour la pagination)"),
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum d'utilisateurs à retourner (max 100)"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = get_current_user(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return db.query(User).offset(skip).limit(limit).all()

@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Mettre à jour complètement un utilisateur (admin seulement)",
    description="Remplace toutes les informations d'un utilisateur par les nouvelles valeurs. Auth admin requis."
)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email is not None:
        user_obj.email = user_update.email
    if user_update.password is not None:
        user_obj.hashed_password = hash_password(user_update.password)
    if user_update.is_active is not None:
        user_obj.is_active = user_update.is_active
    if user_update.role is not None:
        user_obj.role = user_update.role
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Mettre à jour partiellement un utilisateur (admin seulement)",
    description="Met à jour partiellement les informations d'un utilisateur. Seuls les champs fournis sont modifiés. Auth admin requis."
)
def partial_update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email is not None:
        user_obj.email = user_update.email
    if user_update.password is not None:
        user_obj.hashed_password = hash_password(user_update.password)
    if user_update.is_active is not None:
        user_obj.is_active = user_update.is_active
    if user_update.role is not None:
        user_obj.role = user_update.role
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur (admin seulement)",
    description="Supprime un utilisateur à partir de son identifiant. Auth admin requis."
)
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_obj)
    db.commit()
    return None