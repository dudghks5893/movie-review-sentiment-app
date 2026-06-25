# Movie Review Sentiment App

영화 정보, 사용자 리뷰, 리뷰 감성 분석 결과를 제공하는 웹 애플리케이션입니다.
프론트엔드는 Streamlit, 백엔드는 FastAPI로 구현하였으며, 리뷰 감성 분석 모델은 ONNX Runtime 기반으로 서빙합니다.

<img width="1200" height="800" alt="05_영화 목록 UI" src="https://github.com/user-attachments/assets/dcfac053-82db-4e78-82b5-990e4488dbb3" />

## 1. 서비스 개요

본 서비스는 사용자가 영화 정보를 등록하고, 각 영화에 대한 리뷰를 작성하면 리뷰 내용을 자동으로 감성 분석하여 긍정/부정 결과와 감성 점수를 제공합니다.

주요 기능은 다음과 같습니다.

* 영화 목록 조회
* 영화 등록
* 영화 정보 수정
* 영화 삭제
* 리뷰 등록
* 리뷰 감성 분석 자동 실행
* 최근 리뷰 10개 조회
* 영화별 리뷰 조회
* 영화별 평균 감성 점수 조회

## 2. 배포 주소

### Frontend

* Streamlit Community Cloud
* URL: `https://movie-review-sentiment-app-vq5qouaykydcrxl5peo2tb.streamlit.app/`

### Backend

* Render
* URL: `https://movie-review-sentiment-backend.onrender.com`
* FastAPI Docs: `https://movie-review-sentiment-backend.onrender.com/docs`

### Docker Image

* Docker Hub: `yhlucas/movie-review-sentiment-backend:latest`

## 3. 기술 스택

### Frontend

* Streamlit
* Requests
* Pandas

### Backend

* FastAPI
* Uvicorn
* SQLAlchemy
* SQLite
* Pydantic

### Model Serving

* Hugging Face Transformers
* ONNX
* ONNX Runtime
* INT8 Dynamic Quantization

### Deployment

* Streamlit Community Cloud
* Render
* Docker
* Docker Hub

## 4. 프로젝트 구조

```text
movie-review-sentiment-app/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── sentiment.py
│   ├── seed_data.py
│   ├── export_onnx.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-export.txt
│   └── model_artifacts/
│       ├── sentiment_int8.onnx
│       ├── tokenizer.json
│       └── tokenizer_config.json
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
├── report/
│   └── screenshots/
│
├── README.md
└── .gitignore
```

## 5. 데이터베이스 구조

본 프로젝트는 SQLite를 사용하여 영화와 리뷰 데이터를 관리합니다.

### movies 테이블

| 컬럼명          | 설명          |
| ------------ | ----------- |
| id           | 영화 고유 ID    |
| title        | 영화 제목       |
| release_date | 개봉일         |
| director     | 감독          |
| genre        | 장르          |
| poster_url   | 포스터 이미지 URL |
| created_at   | 등록 시각       |

### reviews 테이블

| 컬럼명             | 설명       |
| --------------- | -------- |
| id              | 리뷰 고유 ID |
| movie_id        | 영화 ID    |
| author          | 작성자      |
| content         | 리뷰 내용    |
| sentiment_label | 감성 분석 라벨 |
| sentiment_score | 감성 분석 점수 |
| created_at      | 등록 시각    |

영화와 리뷰는 1:N 관계입니다.
하나의 영화는 여러 개의 리뷰를 가질 수 있습니다.

## 6. API 기능

### Movies

| Method | Endpoint             | 설명       |
| ------ | -------------------- | -------- |
| GET    | `/movies`            | 전체 영화 조회 |
| GET    | `/movies/{movie_id}` | 특정 영화 조회 |
| POST   | `/movies`            | 영화 등록    |
| PUT    | `/movies/{movie_id}` | 영화 정보 수정 |
| DELETE | `/movies/{movie_id}` | 영화 삭제    |

### Reviews

| Method | Endpoint                     | 설명            |
| ------ | ---------------------------- | ------------- |
| GET    | `/reviews`                   | 최근 리뷰 조회      |
| GET    | `/movies/{movie_id}/reviews` | 특정 영화 리뷰 조회   |
| POST   | `/reviews`                   | 리뷰 등록 및 감성 분석 |
| DELETE | `/reviews/{review_id}`       | 리뷰 삭제         |

### Ratings

| Method | Endpoint                    | 설명              |
| ------ | --------------------------- | --------------- |
| GET    | `/movies/{movie_id}/rating` | 영화별 평균 감성 점수 조회 |

### Sentiment

| Method | Endpoint          | 설명        |
| ------ | ----------------- | --------- |
| GET    | `/sentiment/test` | 감성 분석 테스트 |

## 7. 감성 분석 모델

감성 분석 모델은 Hugging Face의 한국어 영화 리뷰 감성 분류 모델을 사용했습니다.

* 모델명: `daekeun-ml/koelectra-small-v3-nsmc`
* 입력: 사용자 리뷰 텍스트
* 출력:

  * `positive`
  * `negative`
  * 감성 점수

## 8. 모델 경량화

배포 환경의 리소스 사용량을 줄이기 위해 PyTorch 모델을 ONNX 형식으로 변환하고, ONNX Runtime 기반 INT8 동적 양자화를 적용했습니다.

| 모델 형식     |       용량 |
| --------- | -------: |
| ONNX FP32 | 54.07 MB |
| ONNX INT8 | 13.95 MB |

최종 백엔드에서는 `sentiment_int8.onnx` 모델을 사용하여 감성 분석을 수행합니다.

## 9. 로컬 실행 방법

### 9.1 가상환경 생성 및 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 9.2 백엔드 실행

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload
```

백엔드 실행 주소:

```text
http://127.0.0.1:8000
```

FastAPI Docs:

```text
http://127.0.0.1:8000/docs
```

### 9.3 프론트엔드 실행

새 터미널에서 실행합니다.

```bash
source .venv/bin/activate
pip install -r frontend/requirements.txt
cd frontend
streamlit run app.py
```

프론트엔드 실행 주소:

```text
http://localhost:8501
```

## 10. 테스트 데이터 등록

백엔드 서버가 실행 중인 상태에서 아래 명령어를 실행하면 영화 3개와 각 영화당 리뷰 10개 이상이 등록됩니다.

```bash
python backend/seed_data.py
```

배포 서버에 데이터를 등록할 경우:

```bash
API_BASE_URL="https://movie-review-sentiment-backend.onrender.com" python backend/seed_data.py
```

## 11. Docker 실행 방법

### 11.1 Docker 이미지 빌드

```bash
docker build -t movie-review-sentiment-backend ./backend
```

### 11.2 Docker 컨테이너 실행

```bash
docker run --name movie-review-sentiment-api \
-p 8000:8000 \
-e PORT=8000 \
movie-review-sentiment-backend
```

### 11.3 Docker Hub 이미지 실행

```bash
docker run --name movie-review-sentiment-api \
-p 8000:8000 \
-e PORT=8000 \
yhlucas/movie-review-sentiment-backend:latest
```

## 12. 주요 구현 결과

* Streamlit 기반 프론트엔드 구현
* FastAPI 기반 백엔드 구현
* SQLite 기반 영화/리뷰 데이터 관리
* 영화 CRUD 구현
* 리뷰 CRUD 구현
* 리뷰 등록 시 감성 분석 자동 실행
* 영화별 평균 감성 점수 계산
* Hugging Face 모델 ONNX 변환
* INT8 양자화 적용
* Docker 이미지 빌드 및 Docker Hub Push
* Render 백엔드 배포
* Streamlit Community Cloud 프론트엔드 배포
