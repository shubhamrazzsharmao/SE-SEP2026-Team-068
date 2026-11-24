from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

_url = get_settings().database_url
# Accept the connection string exactly as Supabase shows it (postgresql:// or postgres://):
# SQLAlchemy would pick the psycopg2 driver for those, but only psycopg 3 is installed.
for _prefix in ("postgresql://", "postgres://"):
    if _url.startswith(_prefix):
        _url = "postgresql+psycopg://" + _url[len(_prefix):]

if _url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
else:
    # prepare_threshold=None keeps psycopg compatible with Supabase's pooler in
    # transaction mode (port 6543) as well as session mode (port 5432).
    _connect_args = {"prepare_threshold": None}

engine = create_engine(_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
