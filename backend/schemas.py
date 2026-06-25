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


class MovieUpdate(BaseModel):
    """
    영화 정보 수정 요청 모델.

    모든 필드는 선택값이다.
    입력된 필드만 기존 영화 정보에 반영한다.
    """

    title: Optional[str] = Field(default=None, example="파묘")
    release_date: Optional[str] = Field(default=None, example="2024-02-22")
    director: Optional[str] = Field(default=None, example="장재현")
    genre: Optional[str] = Field(default=None, example="미스터리, 오컬트")
    poster_url: Optional[str] = Field(default=None, example="https://example.com/poster.jpg")


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
    """

    movie_id: int = Field(..., example=1)
    author: str = Field(..., example="원이연")
    content: str = Field(..., example="배우들의 연기가 좋고 몰입감이 뛰어났습니다.")


class ReviewResponse(BaseModel):
    """
    리뷰 응답 모델.
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
