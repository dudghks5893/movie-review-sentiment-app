from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db


# SQLAlchemy 모델 기준으로 DB 테이블을 생성한다.
# movies.db 파일이 없으면 자동 생성되고, movies 테이블도 자동 생성된다.
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="Movie Review Sentiment API",
    description="영화 정보와 사용자 리뷰, 감성 분석 결과를 관리하는 FastAPI 백엔드입니다.",
    version="1.0.0",
)

# CORS 설정
# Streamlit 프론트엔드에서 FastAPI 백엔드로 API 요청을 보낼 수 있도록 허용한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    서버 상태 확인용 기본 엔드포인트.

    브라우저에서 http://127.0.0.1:8000 접속 시
    API 서버가 정상 실행 중인지 확인할 수 있다.
    """

    return {
        "message": "Movie Review Sentiment API is running.",
        "docs": "/docs",
    }


@app.post("/movies", response_model=schemas.MovieResponse, tags=["Movies"])
def create_movie(
    movie: schemas.MovieCreate,
    db: Session = Depends(get_db),
):
    """
    영화 등록 API.

    요청 body로 영화 정보를 받아 DB에 저장한다.
    """

    return crud.create_movie(db=db, movie=movie)


@app.get("/movies", response_model=list[schemas.MovieResponse], tags=["Movies"])
def get_movies(
    db: Session = Depends(get_db),
):
    """
    전체 영화 조회 API.

    DB에 저장된 모든 영화 목록을 반환한다.
    """

    return crud.get_movies(db=db)


@app.get("/movies/{movie_id}", response_model=schemas.MovieResponse, tags=["Movies"])
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 영화 조회 API.

    URL 경로로 전달받은 movie_id에 해당하는 영화 정보를 반환한다.
    """

    movie = crud.get_movie(db=db, movie_id=movie_id)

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

    URL 경로로 전달받은 movie_id에 해당하는 영화를 삭제한다.
    """

    movie = crud.delete_movie(db=db, movie_id=movie_id)

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie
