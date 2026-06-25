import os
from typing import Dict, List

import requests


# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------

# FastAPI 서버 주소
# 로컬 실행: http://127.0.0.1:8000
# Docker 실행: http://127.0.0.1:8000
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# ------------------------------------------------------------
# 제출 캡쳐용 영화 데이터
# ------------------------------------------------------------

MOVIES = [
    {
        "title": "파묘",
        "release_date": "2024-02-22",
        "director": "장재현",
        "genre": "미스터리, 오컬트",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwiLKBwfCp_98JMOmNczh4DIxEiNvBeiPU64S66pLz-g&s=10",
    },
    {
        "title": "괴물",
        "release_date": "2006-07-27",
        "director": "봉준호",
        "genre": "드라마, 스릴러, 괴수",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ76R15FbtVDU0gtFulsjGfngazINM60o4jU-iOcEOyxQ&s=10",
    },
    {
        "title": "범죄도시4",
        "release_date": "2024-04-24",
        "director": "허명행",
        "genre": "범죄, 액션",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3SLGHbSqU_RO5XDnIGUmOLF6zQwZvLFrm9oZETW6OYw&s=10",
    },
]


# ------------------------------------------------------------
# 제출 캡쳐용 리뷰 데이터
# 각 영화당 10개 이상 등록되도록 구성한다.
# ------------------------------------------------------------

REVIEWS_BY_TITLE = {
    "파묘": [
        "배우들의 연기가 좋고 몰입감이 뛰어났습니다.",
        "분위기가 강렬하고 장면마다 긴장감이 잘 살아있었습니다.",
        "오컬트 장르의 매력이 잘 드러나서 인상적이었습니다.",
        "초반부터 집중하게 만드는 힘이 있는 영화였습니다.",
        "연출과 음악이 잘 어울려서 완성도가 높게 느껴졌습니다.",
        "소재는 흥미로웠지만 중간 전개가 조금 지루했습니다.",
        "기대했던 것보다 설명이 부족해서 아쉬웠습니다.",
        "후반부는 몰입감이 좋았고 배우들의 호흡도 좋았습니다.",
        "무서운 분위기보다 긴장감 중심이라 보기 편했습니다.",
        "전체적으로 독특하고 기억에 남는 작품이었습니다.",
    ],
    "괴물": [
        "배우들의 연기가 매우 훌륭했고 긴장감이 끝까지 이어졌습니다.",
        "역사적 사건을 몰입감 있게 풀어낸 점이 좋았습니다.",
        "전개가 빠르고 장면마다 힘이 있어서 집중해서 봤습니다.",
        "인물 간 대립이 강렬해서 인상 깊었습니다.",
        "완성도 높은 연출과 배우들의 표현력이 돋보였습니다.",
        "내용은 좋았지만 보는 내내 답답한 감정이 컸습니다.",
        "무거운 분위기라 다시 보기에는 조금 부담스러웠습니다.",
        "역사적 배경을 다시 생각하게 만드는 영화였습니다.",
        "긴장감과 메시지가 모두 살아있는 작품이었습니다.",
        "전체적으로 추천할 만한 완성도 높은 영화였습니다.",
    ],
    "범죄도시4": [
        "액션 장면이 시원하고 속도감이 좋아서 재밌었습니다.",
        "마동석 배우의 캐릭터가 확실해서 보는 재미가 있었습니다.",
        "가볍게 보기 좋은 오락 영화로 만족스러웠습니다.",
        "전투 장면이 강렬하고 통쾌한 느낌이 좋았습니다.",
        "시리즈 특유의 분위기가 잘 살아있었습니다.",
        "이야기 구조가 익숙해서 새로움은 조금 부족했습니다.",
        "악역의 매력이 기대보다 아쉬웠습니다.",
        "전개는 단순하지만 액션 중심으로 보기에는 충분했습니다.",
        "큰 고민 없이 즐기기 좋은 영화였습니다.",
        "전체적으로 재미있고 관객 친화적인 작품이었습니다.",
    ],
}


# ------------------------------------------------------------
# API 요청 함수
# ------------------------------------------------------------

def get_movies() -> List[Dict]:
    """
    현재 DB에 등록된 영화 목록을 가져온다.
    """

    response = requests.get(f"{API_BASE_URL}/movies", timeout=30)
    response.raise_for_status()
    return response.json()


def find_movie_by_title(title: str):
    """
    영화 제목으로 기존 등록 여부를 확인한다.
    """

    movies = get_movies()

    for movie in movies:
        if movie["title"] == title:
            return movie

    return None


def create_movie(movie: Dict) -> Dict:
    """
    영화가 없으면 새로 등록한다.
    """

    response = requests.post(
        f"{API_BASE_URL}/movies",
        json=movie,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def update_movie(movie_id: int, movie: Dict) -> Dict:
    """
    이미 등록된 영화는 최신 정보로 수정한다.
    포스터 URL이 깨졌을 때도 이 함수로 교체된다.
    """

    response = requests.put(
        f"{API_BASE_URL}/movies/{movie_id}",
        json=movie,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_reviews_by_movie(movie_id: int) -> List[Dict]:
    """
    특정 영화에 등록된 리뷰 목록을 가져온다.
    """

    response = requests.get(
        f"{API_BASE_URL}/movies/{movie_id}/reviews",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def create_review(movie_id: int, content: str, author: str) -> Dict:
    """
    리뷰를 등록한다.
    리뷰 등록 시 FastAPI 백엔드에서 감성 분석이 자동 실행된다.
    """

    payload = {
        "movie_id": movie_id,
        "author": author,
        "content": content,
    }

    response = requests.post(
        f"{API_BASE_URL}/reviews",
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


# ------------------------------------------------------------
# 데이터 등록 실행 함수
# ------------------------------------------------------------

def seed_movies():
    """
    제출용 영화 3개를 등록한다.

    이미 같은 제목의 영화가 있으면 새로 만들지 않고 수정한다.
    """

    created_or_updated_movies = {}

    for movie in MOVIES:
        existing_movie = find_movie_by_title(movie["title"])

        if existing_movie:
            updated_movie = update_movie(existing_movie["id"], movie)
            created_or_updated_movies[movie["title"]] = updated_movie
            print(f"[UPDATE] {movie['title']} / ID: {updated_movie['id']}")
        else:
            created_movie = create_movie(movie)
            created_or_updated_movies[movie["title"]] = created_movie
            print(f"[CREATE] {movie['title']} / ID: {created_movie['id']}")

    return created_or_updated_movies


def seed_reviews(movies_by_title: Dict):
    """
    각 영화당 리뷰가 10개 이상이 되도록 부족한 만큼만 추가한다.
    """

    for title, movie in movies_by_title.items():
        movie_id = movie["id"]
        existing_reviews = get_reviews_by_movie(movie_id)
        existing_count = len(existing_reviews)

        target_reviews = REVIEWS_BY_TITLE[title]
        missing_count = max(0, 10 - existing_count)

        if missing_count == 0:
            print(f"[SKIP] {title}: 이미 리뷰 {existing_count}개 이상 등록됨")
            continue

        reviews_to_add = target_reviews[:missing_count]

        for index, content in enumerate(reviews_to_add, start=1):
            author = f"테스트유저{existing_count + index}"
            review = create_review(movie_id, content, author)

            print(
                f"[REVIEW] {title} / "
                f"review_id={review['id']} / "
                f"{review['sentiment_label']} / "
                f"{review['sentiment_score']}"
            )


def main():
    """
    전체 시드 데이터 등록 실행 함수.
    """

    print("=== Movie Review Sentiment App Seed Data Start ===")
    print(f"API_BASE_URL: {API_BASE_URL}")

    # 서버 연결 확인
    response = requests.get(f"{API_BASE_URL}/", timeout=30)
    response.raise_for_status()
    print("[OK] FastAPI server connected")

    # 영화 등록 또는 수정
    movies_by_title = seed_movies()

    # 리뷰 등록
    seed_reviews(movies_by_title)

    print("=== Seed Data Completed ===")


if __name__ == "__main__":
    main()
