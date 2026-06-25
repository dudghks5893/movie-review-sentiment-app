from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from database import Base


class Movie(Base):
    """
    movies 테이블과 매핑되는 SQLAlchemy 모델.

    영화 제목, 개봉일, 감독, 장르, 포스터 URL을 저장한다.
    """

    __tablename__ = "movies"

    # 영화 고유 ID
    id = Column(Integer, primary_key=True, index=True)

    # 영화 기본 정보
    title = Column(String, nullable=False, index=True)
    release_date = Column(String, nullable=False)
    director = Column(String, nullable=False)
    genre = Column(String, nullable=False)

    # 포스터 이미지 URL
    poster_url = Column(String, nullable=True)

    # 데이터 등록 시각
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Review(Base):
    """
    reviews 테이블과 매핑되는 SQLAlchemy 모델.

    사용자가 작성한 리뷰와 감성 분석 결과를 저장한다.
    """

    __tablename__ = "reviews"

    # 리뷰 고유 ID
    id = Column(Integer, primary_key=True, index=True)

    # 리뷰가 연결된 영화 ID
    # movies.id를 참조하는 외래키다.
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)

    # 리뷰 작성자 이름
    author = Column(String, nullable=False)

    # 리뷰 내용
    content = Column(Text, nullable=False)

    # 감성 분석 결과 라벨
    # 예: positive, negative, neutral
    sentiment_label = Column(String, nullable=False)

    # 감성 분석 점수
    # positive는 양수, negative는 음수로 저장한다.
    sentiment_score = Column(Float, nullable=False)

    # 리뷰 등록 시각
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
