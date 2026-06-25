from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class Movie(Base):
    """
    movies 테이블과 매핑되는 SQLAlchemy 모델.

    영화 제목, 개봉일, 감독, 장르, 포스터 URL을 저장한다.
    """

    # 실제 SQLite DB에 생성될 테이블 이름
    __tablename__ = "movies"

    # 영화 고유 ID
    id = Column(Integer, primary_key=True, index=True)

    # 영화 제목
    title = Column(String, nullable=False, index=True)

    # 개봉일
    # 날짜 계산이 필요한 프로젝트가 아니므로 문자열로 관리한다.
    release_date = Column(String, nullable=False)

    # 감독 이름
    director = Column(String, nullable=False)

    # 영화 장르
    genre = Column(String, nullable=False)

    # 포스터 이미지 URL
    # 포스터가 없어도 등록 가능하도록 nullable=True로 설정한다.
    poster_url = Column(String, nullable=True)

    # 데이터 등록 시각
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
