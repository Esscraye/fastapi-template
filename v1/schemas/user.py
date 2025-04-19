# Schéma User Pydantic pour v1

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    """
    Champs de base pour un utilisateur.
    """
    email: EmailStr = Field(..., description="Adresse email de l'utilisateur.")
    is_active: Optional[bool] = Field(True, description="Statut d'activation de l'utilisateur.")
    role: Optional[Literal["user", "admin"]] = Field("user", description="Rôle de l'utilisateur (user ou admin).")

class UserCreate(UserBase):
    """
    Schéma utilisé lors de la création d'un utilisateur (requiert un mot de passe).
    """
    password: str = Field(..., min_length=8, description="Mot de passe de l'utilisateur (min 8 caractères).")
    role: Optional[Literal["user", "admin"]] = Field("user", description="Rôle de l'utilisateur (user ou admin).")

class UserRead(UserBase):
    """
    Schéma retourné en lecture (API) pour un utilisateur.
    """
    id: int = Field(..., description="Identifiant unique de l'utilisateur.")
    created_at: datetime = Field(..., description="Date de création de l'utilisateur.")

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    """
    Schéma utilisé pour la mise à jour complète (PUT) ou partielle (PATCH) d'un utilisateur.
    """
    email: Optional[EmailStr] = Field(None, description="Nouvelle adresse email.")
    password: Optional[str] = Field(None, min_length=8, description="Nouveau mot de passe.")
    is_active: Optional[bool] = Field(None, description="Nouveau statut d'activation.")
    role: Optional[Literal["user", "admin"]] = Field(None, description="Nouveau rôle (user ou admin).")

class UserInDB(UserBase):
    """
    Schéma interne incluant le hash du mot de passe.
    """
    id: int
    hashed_password: str
    created_at: datetime

    class Config:
        orm_mode = True
