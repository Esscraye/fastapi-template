# FastAPI Template – Production Ready

Ce template fournit une base solide pour développer des APIs FastAPI robustes, versionnées et prêtes pour la production.

## Fonctionnalités principales
- Structure modulaire par version (`v1/`, `v2/`, ...)
- Configuration centralisée (`core/config.py`, `.env`)
- Authentification JWT & gestion des utilisateurs
- Connexion et migrations base de données (SQLAlchemy + Alembic)
- Logging structuré (console + fichiers)
- Tests unitaires par version
- Docker ready
- Documentation interactive automatique (Swagger/OpenAPI, Redoc)
- **Gestion des rôles utilisateurs (admin/user) et permissions**
- **Création automatisée d'un admin par script**

## Lancer le projet
```bash
# Créer et activer un virtualenv
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements-dev.txt

# Copier le fichier d'exemple d'environnement
cp .env.example .env

# Lancer les migrations (après avoir configuré .env)
alembic upgrade head

# Créer un utilisateur admin par défaut (optionnel)
python -m scripts.create_admin admin@example.com monSuperMotDePasse

# Lancer l'application
uvicorn main:app --reload
```

## Exécuter avec Docker
- Prérequis : Docker
```bash
docker build --no-cache -t fastapi-app .
docker run --rm -d -p 8000:8000 --env-file .env fastapi-app
```
L'application sera accessible à http://localhost:8000

## Documentation interactive
- Swagger UI : http://localhost:8000/docs
- Redoc : http://localhost:8000/redoc

## Gestion des migrations
Voir [alembic/README.md](alembic/README.md)

## Structure du projet
```
core/           # Configuration, sécurité, DB, logging
v1/             # Endpoints, modèles, schémas versionnés
alembic/        # Migrations DB
...
```

## Gestion des rôles et permissions
- Deux rôles : `admin` et `user`.
- Seuls les admins peuvent créer, modifier ou supprimer des utilisateurs, ou créer d'autres admins.
- Les rôles sont stockés dans la base et encodés dans le token JWT.
- Les endpoints critiques sont protégés par des guards (`require_role`).

## Tests de sécurité et d'accès
- Des tests valident que seuls les admins peuvent accéder aux routes sensibles.
- Les utilisateurs standards ne peuvent ni créer d'admin, ni accéder aux endpoints réservés aux admins.
- Les fixtures génèrent des tokens pour chaque rôle lors des tests.

## Variables d'environnement
- Le projet nécessite un fichier `.env` à la racine, contenant au minimum :
  - `DATABASE_URL`
  - `SECRET_KEY`
- Un exemple est fourni dans `.env.example`.

## Bonnes pratiques
- Versionne les endpoints et les schémas
- Utilise les dépendances FastAPI pour la sécurité et la DB
- Documente chaque endpoint avec des docstrings
- Écris des tests pour chaque version

## À compléter
- Ajouter des endpoints
- Étendre la sécurité (OAuth2, permissions...)
- Ajouter la CI/CD (GitHub Actions, ...)
