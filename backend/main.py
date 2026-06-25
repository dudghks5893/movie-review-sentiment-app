from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db
from sentiment import MODEL_NAME, analyze_sentiment


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Review Sentiment API",
    description="영화 정보와 사용자 리뷰, 감성 분석 결과를 관리하는 FastAPI 백엔드입니다.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    서버 상태 확인용 기본 엔드포인트.
    """

    return {
        "message": "Movie Review Sentiment API is running.",
        "docs": "/docs",
        "sentiment_model": MODEL_NAME,
    }


@app.post("/movies", response_model=schemas.MovieResponse, tags=["Movies"])
def create_movie(
    movie: schemas.MovieCreate,
    db: Session = Depends(get_db),
):
    """
    영화 등록 API.
    """

    return crud.create_movie(db=db, movie=movie)


@app.get("/movies", response_model=list[schemas.MovieResponse], tags=["Movies"])
def get_movies(
    db: Session = Depends(get_db),
):
    """
    전체 영화 조회 API.
    """

    return crud.get_movies(db=db)


@app.get("/movies/{movie_id}", response_model=schemas.MovieResponse, tags=["Movies"])
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 영화 조회 API.
    """

    movie = crud.get_movie(db=db, movie_id=movie_id)

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


@app.put("/movies/{movie_id}", response_model=schemas.MovieResponse, tags=["Movies"])
def update_movie(
    movie_id: int,
    movie_update: schemas.MovieUpdate,
    db: Session = Depends(get_db),
):
    """
    특정 영화 정보 수정 API.

    제목, 개봉일, 감독, 장르, 포스터 URL을 수정할 수 있다.
    """

    movie = crud.update_movie(
        db=db,
        movie_id=movie_id,
        movie_update=movie_update,
    )

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


@app.delete("/movies/{movie_id}", response_model=schemas.MovieResponse, tags=["Movies"])
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 영화 삭제 API.

    영화 삭제 시 해당 영화의 리뷰도 함께 삭제된다.
    """

    movie = crud.delete_movie(db=db, movie_id=movie_id)

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


@app.post("/reviews", response_model=schemas.ReviewResponse, tags=["Reviews"])
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
):
    """
    리뷰 등록 API.
    """

    db_review = crud.create_review(db=db, review=review)

    if db_review is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return db_review


@app.get("/reviews", response_model=list[schemas.ReviewResponse], tags=["Reviews"])
def get_reviews(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    전체 리뷰 조회 API.
    """

    return crud.get_reviews(db=db, limit=limit)


@app.get(
    "/movies/{movie_id}/reviews",
    response_model=list[schemas.ReviewResponse],
    tags=["Reviews"],
)
def get_reviews_by_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 영화의 리뷰 목록 조회 API.
    """

    movie = crud.get_movie(db=db, movie_id=movie_id)

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return crud.get_reviews_by_movie(db=db, movie_id=movie_id)


@app.delete("/reviews/{review_id}", response_model=schemas.ReviewResponse, tags=["Reviews"])
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 리뷰 삭제 API.
    """

    review = crud.delete_review(db=db, review_id=review_id)

    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    return review


@app.get("/movies/{movie_id}/rating", response_model=schemas.RatingResponse, tags=["Ratings"])
def get_movie_rating(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 영화의 평균 감성 점수 조회 API.
    """

    rating = crud.get_movie_rating(db=db, movie_id=movie_id)

    if rating is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return rating


@app.get("/sentiment/test", response_model=schemas.SentimentResponse, tags=["Sentiment"])
def test_sentiment(
    text: str = Query(..., example="배우들의 연기가 좋고 몰입감이 뛰어났습니다."),
):
    """
    감성 분석 모델 테스트 API.
    """

    result = analyze_sentiment(text)

    return {
        "text": text,
        "sentiment_label": result["sentiment_label"],
        "sentiment_score": result["sentiment_score"],
        "model_name": result["model_name"],
    }
