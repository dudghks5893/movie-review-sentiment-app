from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# 현재 파일(database.py)이 위치한 backend 폴더 경로를 기준으로 DB 파일 경로를 설정한다.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "movies.db"

# SQLite 데이터베이스 연결 주소
# 예: sqlite:////Users/.../movie-review-sentiment-app/backend/movies.db
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy 엔진 생성
# check_same_thread=False는 FastAPI에서 SQLite를 사용할 때 필요한 설정이다.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# DB 세션 생성기
# API 요청이 들어올 때마다 DB 작업을 수행할 수 있는 세션을 만든다.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# SQLAlchemy 모델 클래스들이 상속받을 기본 클래스
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
