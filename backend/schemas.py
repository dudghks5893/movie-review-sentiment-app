from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MovieBase(BaseModel):
    """
    영화 데이터의 공통 필드.

    영화 생성 요청과 응답 모델에서 공통으로 사용하는 필드를 정의한다.
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

    클라이언트가 POST /movies 요청을 보낼 때 사용하는 데이터 구조다.
    현재는 MovieBase와 동일한 필드를 사용한다.
    """

    pass


class MovieResponse(MovieBase):
    """
    영화 응답 모델.

    DB에 저장된 영화 데이터를 클라이언트에게 반환할 때 사용하는 구조다.
    id와 created_at은 서버에서 자동으로 생성된다.
    """

    id: int
    created_at: datetime

    # SQLAlchemy 모델 객체를 Pydantic 응답 모델로 변환할 수 있도록 설정한다.
    model_config = ConfigDict(from_attributes=True)
