# Alembic (Migrations)

## Initialisation

- Le fichier `env.py` est configuré pour utiliser la config FastAPI et charger tous les modèles (ex : `v1/models/user.py`).
- Vérifie que `alembic.ini` existe à la racine du projet (sinon, initialise Alembic avec `alembic init alembic`).

## Commandes principales

- Créer une migration automatique :
  ```bash
  alembic revision --autogenerate -m "create user table"
  ```
- Appliquer les migrations :
  ```bash
  alembic upgrade head
  ```
- Voir le statut :
  ```bash
  alembic current
  ```

## Bonnes pratiques
- Importe tous les modèles dans `alembic/env.py` pour que la détection automatique fonctionne.
- Ne modifie pas les migrations générées automatiquement sans comprendre leur impact.
- Versionne le dossier `alembic/versions/` dans git.