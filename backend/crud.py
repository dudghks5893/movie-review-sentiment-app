from sqlalchemy.orm import Session

import models
import schemas
from sentiment import analyze_sentiment


def create_movie(db: Session, movie: schemas.MovieCreate):
    """
    영화 등록 함수.
    """

    db_movie = models.Movie(
        title=movie.title,
        release_date=movie.release_date,
        director=movie.director,
        genre=movie.genre,
        poster_url=movie.poster_url,
    )

    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    return db_movie


def get_movies(db: Session):
    """
    전체 영화 조회 함수.
    """

    return db.query(models.Movie).order_by(models.Movie.id.desc()).all()


def get_movie(db: Session, movie_id: int):
    """
    특정 영화 조회 함수.
    """

    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def update_movie(db: Session, movie_id: int, movie_update: schemas.MovieUpdate):
    """
    특정 영화 정보 수정 함수.

    전달받은 값이 있는 필드만 기존 데이터에 반영한다.
    """

    movie = get_movie(db, movie_id)

    if movie is None:
        return None

    update_data = movie_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)

    return movie


def delete_movie(db: Session, movie_id: int):
    """
    특정 영화 삭제 함수.

    영화 삭제 전, 해당 영화에 연결된 리뷰를 먼저 삭제한다.
    """

    movie = get_movie(db, movie_id)

    if movie is None:
        return None

    db.query(models.Review).filter(models.Review.movie_id == movie_id).delete()

    db.delete(movie)
    db.commit()

    return movie


def create_review(db: Session, review: schemas.ReviewCreate):
    """
    리뷰 등록 함수.

    리뷰 내용을 감성 분석한 뒤 분석 결과와 함께 저장한다.
    """

    movie = get_movie(db, review.movie_id)

    if movie is None:
        return None

    sentiment_result = analyze_sentiment(review.content)

    db_review = models.Review(
        movie_id=review.movie_id,
        author=review.author,
        content=review.content,
        sentiment_label=sentiment_result["sentiment_label"],
        sentiment_score=sentiment_result["sentiment_score"],
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return db_review


def get_reviews(db: Session, limit: int = 10):
    """
    전체 리뷰 조회 함수.
    """

    return (
        db.query(models.Review)
        .order_by(models.Review.id.desc())
        .limit(limit)
        .all()
    )


def get_reviews_by_movie(db: Session, movie_id: int):
    """
    특정 영화의 리뷰 목록 조회 함수.
    """

    return (
        db.query(models.Review)
        .filter(models.Review.movie_id == movie_id)
        .order_by(models.Review.id.desc())
        .all()
    )


def get_review(db: Session, review_id: int):
    """
    특정 리뷰 조회 함수.
    """

    return db.query(models.Review).filter(models.Review.id == review_id).first()


def delete_review(db: Session, review_id: int):
    """
    특정 리뷰 삭제 함수.
    """

    review = get_review(db, review_id)

    if review is None:
        return None

    db.delete(review)
    db.commit()

    return review


def get_movie_rating(db: Session, movie_id: int):
    """
    특정 영화의 평균 감성 점수를 계산한다.
    """

    movie = get_movie(db, movie_id)

    if movie is None:
        return None

    reviews = get_reviews_by_movie(db, movie_id)

    if not reviews:
        return {
            "movie_id": movie_id,
            "review_count": 0,
            "average_sentiment_score": 0.0,
            "rating_label": "neutral",
        }

    average_score = sum(review.sentiment_score for review in reviews) / len(reviews)
    average_score = round(average_score, 4)

    if average_score > 0.15:
        rating_label = "positive"
    elif average_score < -0.15:
        rating_label = "negative"
    else:
        rating_label = "neutral"

    return {
        "movie_id": movie_id,
        "review_count": len(reviews),
        "average_sentiment_score": average_score,
        "rating_label": rating_label,
    }
