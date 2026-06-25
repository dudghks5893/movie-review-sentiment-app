from sqlalchemy.orm import Session

import models
import schemas


def create_movie(db: Session, movie: schemas.MovieCreate):
    """
    영화 등록 함수.

    전달받은 영화 정보를 Movie 모델 객체로 변환한 뒤 DB에 저장한다.
    """

    db_movie = models.Movie(
        title=movie.title,
        release_date=movie.release_date,
        director=movie.director,
        genre=movie.genre,
        poster_url=movie.poster_url,
    )

    # DB에 새 영화 객체 추가
    db.add(db_movie)

    # 변경사항 저장
    db.commit()

    # DB에서 생성된 id, created_at 값을 객체에 반영
    db.refresh(db_movie)

    return db_movie


def get_movies(db: Session):
    """
    전체 영화 조회 함수.

    최근 등록된 영화가 위에 보이도록 id 기준 내림차순으로 조회한다.
    """

    return db.query(models.Movie).order_by(models.Movie.id.desc()).all()


def get_movie(db: Session, movie_id: int):
    """
    특정 영화 조회 함수.

    movie_id에 해당하는 영화 1개를 조회한다.
    없으면 None을 반환한다.
    """

    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def delete_movie(db: Session, movie_id: int):
    """
    특정 영화 삭제 함수.

    movie_id에 해당하는 영화가 있으면 삭제하고,
    없으면 None을 반환한다.
    """

    movie = get_movie(db, movie_id)

    if movie is None:
        return None

    db.delete(movie)
    db.commit()

    return movie
