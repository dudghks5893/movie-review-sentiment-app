import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# 현재 파일(database.py)이 위치한 backend 폴더 경로
BASE_DIR = Path(__file__).resolve().parent

# 기본 DB 경로는 backend/movies.db
# 배포 환경에서는 MOVIES_DB_PATH 환경변수로 DB 저장 위치를 바꿀 수 있다.
db_path_from_env = os.getenv("MOVIES_DB_PATH")

if db_path_from_env:
    DB_PATH = Path(db_path_from_env)
else:
    DB_PATH = BASE_DIR / "movies.db"

# DB 파일이 저장될 폴더가 없으면 생성한다.
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    FastAPI 의존성 주입용 DB 세션 함수.

    API 요청마다 DB 세션을 생성하고,
    요청 처리가 끝나면 세션을 닫는다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
