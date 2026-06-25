import os

import pandas as pd
import requests
import streamlit as st


# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------

st.set_page_config(
    page_title="Movie Review Sentiment App",
    page_icon="🎬",
    layout="wide",
)


# Streamlit Community Cloud 배포 시에는 st.secrets["API_BASE_URL"] 사용
# 로컬 실행 시에는 환경변수 또는 기본값 http://127.0.0.1:8000 사용
def get_api_base_url():
    """
    FastAPI 백엔드 서버 주소를 가져온다.

    로컬 개발:
        http://127.0.0.1:8000

    Streamlit Cloud 배포:
        .streamlit/secrets.toml 또는 Streamlit Cloud Secrets에
        API_BASE_URL 값을 등록해서 사용한다.
    """

    try:
        return st.secrets["API_BASE_URL"]
    except Exception:
        return os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


API_BASE_URL = get_api_base_url()


# ------------------------------------------------------------
# API 호출 함수
# ------------------------------------------------------------

def request_get(path, params=None):
    """
    FastAPI GET 요청 공통 함수.
    """

    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        st.error(f"GET 요청 실패: {error}")
        return None


def request_post(path, payload):
    """
    FastAPI POST 요청 공통 함수.
    """

    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        st.error(f"POST 요청 실패: {error}")
        return None


def request_delete(path):
    """
    FastAPI DELETE 요청 공통 함수.
    """

    try:
        response = requests.delete(
            f"{API_BASE_URL}{path}",
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        st.error(f"DELETE 요청 실패: {error}")
        return None


def load_movies():
    """
    전체 영화 목록을 불러온다.
    """

    result = request_get("/movies")
    return result if result is not None else []


def load_recent_reviews(limit=10):
    """
    최근 리뷰 목록을 불러온다.
    """

    result = request_get("/reviews", params={"limit": limit})
    return result if result is not None else []


def load_movie_reviews(movie_id):
    """
    특정 영화의 리뷰 목록을 불러온다.
    """

    result = request_get(f"/movies/{movie_id}/reviews")
    return result if result is not None else []


def load_movie_rating(movie_id):
    """
    특정 영화의 평균 감성 점수를 불러온다.
    """

    return request_get(f"/movies/{movie_id}/rating")


# ------------------------------------------------------------
# 화면 표시 함수
# ------------------------------------------------------------

def sentiment_badge(label):
    """
    감성 분석 라벨을 화면에 표시하기 좋은 텍스트로 변환한다.
    """

    if label == "positive":
        return "긍정"
    if label == "negative":
        return "부정"
    return "중립"


def format_score(score):
    """
    감성 점수를 소수점 4자리로 표시한다.
    """

    try:
        return f"{float(score):.4f}"
    except Exception:
        return "0.0000"


def render_movie_card(movie):
    """
    영화 1개의 정보를 카드 형태로 표시한다.
    """

    poster_url = movie.get("poster_url")

    col1, col2 = st.columns([1, 3])

    with col1:
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.info("포스터 없음")

    with col2:
        st.subheader(movie.get("title", "제목 없음"))
        st.write(f"**개봉일**: {movie.get('release_date', '-')}")
        st.write(f"**감독**: {movie.get('director', '-')}")
        st.write(f"**장르**: {movie.get('genre', '-')}")
        st.caption(f"영화 ID: {movie.get('id')}")

        rating = load_movie_rating(movie.get("id"))
        if rating:
            st.write(
                f"**평균 감성 점수**: {format_score(rating.get('average_sentiment_score', 0))} "
                f"/ **전체 분위기**: {sentiment_badge(rating.get('rating_label'))} "
                f"/ **리뷰 수**: {rating.get('review_count', 0)}개"
            )


def render_reviews_table(reviews):
    """
    리뷰 목록을 표 형태로 표시한다.
    """

    if not reviews:
        st.info("등록된 리뷰가 없습니다.")
        return

    rows = []
    for review in reviews:
        rows.append(
            {
                "리뷰 ID": review.get("id"),
                "영화 ID": review.get("movie_id"),
                "작성자": review.get("author"),
                "리뷰 내용": review.get("content"),
                "감성": sentiment_badge(review.get("sentiment_label")),
                "점수": format_score(review.get("sentiment_score")),
                "등록일": review.get("created_at"),
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ------------------------------------------------------------
# 메인 화면
# ------------------------------------------------------------

st.title("🎬 영화 리뷰 감성 분석 웹앱")
st.caption("Streamlit 프론트엔드와 FastAPI 백엔드를 연결한 영화 리뷰 감성 분석 서비스입니다.")

with st.sidebar:
    st.header("서버 설정")
    st.write("현재 API 서버")
    st.code(API_BASE_URL)

    if st.button("새로고침"):
        st.rerun()


# 백엔드 서버 상태 확인
server_status = request_get("/")

if server_status:
    st.success("FastAPI 백엔드 서버 연결 성공")
else:
    st.warning("FastAPI 백엔드 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.")


tab_movies, tab_add_movie, tab_add_review, tab_reviews = st.tabs(
    [
        "영화 목록",
        "영화 추가",
        "리뷰 등록",
        "리뷰 조회",
    ]
)


# ------------------------------------------------------------
# 탭 1. 영화 목록
# ------------------------------------------------------------

with tab_movies:
    st.header("영화 목록")

    movies = load_movies()

    if not movies:
        st.info("등록된 영화가 없습니다. '영화 추가' 탭에서 영화를 등록하세요.")
    else:
        for movie in movies:
            with st.container(border=True):
                render_movie_card(movie)

                delete_col, _ = st.columns([1, 5])
                with delete_col:
                    if st.button(
                        "영화 삭제",
                        key=f"delete_movie_{movie.get('id')}",
                    ):
                        deleted = request_delete(f"/movies/{movie.get('id')}")
                        if deleted:
                            st.success(f"'{movie.get('title')}' 영화가 삭제되었습니다.")
                            st.rerun()


# ------------------------------------------------------------
# 탭 2. 영화 추가
# ------------------------------------------------------------

with tab_add_movie:
    st.header("영화 추가")

    with st.form("movie_form"):
        title = st.text_input("영화 제목", placeholder="예: 파묘")
        release_date = st.text_input("개봉일", placeholder="예: 2024-02-22")
        director = st.text_input("감독", placeholder="예: 장재현")
        genre = st.text_input("장르", placeholder="예: 미스터리, 오컬트")
        poster_url = st.text_input("포스터 URL", placeholder="https://example.com/poster.jpg")

        submitted = st.form_submit_button("영화 등록")

        if submitted:
            if not title or not release_date or not director or not genre:
                st.error("제목, 개봉일, 감독, 장르는 필수 입력값입니다.")
            else:
                payload = {
                    "title": title,
                    "release_date": release_date,
                    "director": director,
                    "genre": genre,
                    "poster_url": poster_url or None,
                }

                created_movie = request_post("/movies", payload)

                if created_movie:
                    st.success(f"'{created_movie['title']}' 영화가 등록되었습니다.")
                    st.json(created_movie)


# ------------------------------------------------------------
# 탭 3. 리뷰 등록
# ------------------------------------------------------------

with tab_add_review:
    st.header("리뷰 등록")

    movies = load_movies()

    if not movies:
        st.info("리뷰를 등록하려면 먼저 영화를 추가해야 합니다.")
    else:
        movie_options = {
            f"{movie['title']} (ID: {movie['id']})": movie["id"]
            for movie in movies
        }

        with st.form("review_form"):
            selected_movie_label = st.selectbox(
                "리뷰를 등록할 영화",
                options=list(movie_options.keys()),
            )
            author = st.text_input("작성자 이름", placeholder="예: 홍길동")
            content = st.text_area(
                "리뷰 내용",
                placeholder="예: 배우들의 연기가 좋고 몰입감이 뛰어났습니다.",
                height=160,
            )

            submitted = st.form_submit_button("리뷰 등록 및 감성 분석")

            if submitted:
                if not author or not content:
                    st.error("작성자와 리뷰 내용을 입력하세요.")
                else:
                    movie_id = movie_options[selected_movie_label]

                    payload = {
                        "movie_id": movie_id,
                        "author": author,
                        "content": content,
                    }

                    created_review = request_post("/reviews", payload)

                    if created_review:
                        st.success("리뷰가 등록되었고 감성 분석이 완료되었습니다.")

                        st.write("분석 결과")
                        st.metric(
                            label="감성",
                            value=sentiment_badge(created_review["sentiment_label"]),
                            delta=format_score(created_review["sentiment_score"]),
                        )

                        st.json(created_review)


# ------------------------------------------------------------
# 탭 4. 리뷰 조회
# ------------------------------------------------------------

with tab_reviews:
    st.header("리뷰 조회")

    movies = load_movies()

    st.subheader("최근 리뷰 10개")
    recent_reviews = load_recent_reviews(limit=10)
    render_reviews_table(recent_reviews)

    st.divider()

    st.subheader("영화별 리뷰 조회")

    if not movies:
        st.info("등록된 영화가 없습니다.")
    else:
        movie_options = {
            f"{movie['title']} (ID: {movie['id']})": movie["id"]
            for movie in movies
        }

        selected_movie_label = st.selectbox(
            "리뷰를 조회할 영화",
            options=list(movie_options.keys()),
            key="review_lookup_movie",
        )

        selected_movie_id = movie_options[selected_movie_label]

        rating = load_movie_rating(selected_movie_id)

        if rating:
            col1, col2, col3 = st.columns(3)

            col1.metric("리뷰 수", rating.get("review_count", 0))
            col2.metric("평균 감성 점수", format_score(rating.get("average_sentiment_score", 0)))
            col3.metric("전체 분위기", sentiment_badge(rating.get("rating_label")))

        movie_reviews = load_movie_reviews(selected_movie_id)
        render_reviews_table(movie_reviews)
