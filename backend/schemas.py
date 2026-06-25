from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MovieBase(BaseModel):
    """
    영화 데이터의 공통 필드.
    """

    title: str = Field(..., example="파묘")
    release_date: str = Field(..., example="2024-02-22")
    director: str = Field(..., example="장재현")
    genre: str = Field(..., example="미스터리, 오컬트")
    poster_url: Optional[str] = Field(
        default=None,
        example="https://example.com/poster.jpg",
    )


class MovieCreate(MovieBase):
    """
    영화 등록 요청 모델.
    """

    pass


class MovieResponse(MovieBase):
    """
    영화 응답 모델.
    """

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """
    리뷰 등록 요청 모델.

    클라이언트는 영화 ID, 작성자, 리뷰 내용만 전달한다.
    감성 분석 결과는 서버에서 자동 생성한다.
    """

    movie_id: int = Field(..., example=1)
    author: str = Field(..., example="원이연")
    content: str = Field(..., example="배우들의 연기가 좋고 몰입감이 뛰어났습니다.")


class ReviewResponse(BaseModel):
    """
    리뷰 응답 모델.

    DB에 저장된 리뷰 정보와 감성 분석 결과를 반환한다.
    """

    id: int
    movie_id: int
    author: str
    content: str
    sentiment_label: str
    sentiment_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingResponse(BaseModel):
    """
    영화별 평균 감성 점수 응답 모델.

    sentiment_score 평균값을 기준으로 영화 리뷰의 전체 분위기를 보여준다.
    """

    movie_id: int
    review_count: int
    average_sentiment_score: float
    rating_label: str


class SentimentResponse(BaseModel):
    """
    감성 분석 테스트 응답 모델.
    """

    text: str
    sentiment_label: str
    sentiment_score: float
    model_name: str
