from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Ajoute le dossier parent au sys.path pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import get_settings
from core.database import Base
import v1.models.user  # Importe tous les modèles ici

# Cette variable est utilisée par Alembic
config = context.config

# Configure le logging
fileConfig(config.config_file_name)

# Récupère l'URL de la base de données depuis la config FastAPI
settings = get_settings()
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option('sqlalchemy.url'),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
