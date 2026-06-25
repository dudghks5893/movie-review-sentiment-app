# FastAPI 백엔드를 실행하기 위한 Python 기반 Docker 이미지
FROM python:3.12-slim

# Python 캐시 파일 생성을 방지한다.
ENV PYTHONDONTWRITEBYTECODE=1

# 로그가 즉시 출력되도록 설정한다.
ENV PYTHONUNBUFFERED=1

# Hugging Face 감성 분석 모델명
ENV SENTIMENT_MODEL_NAME=daekeun-ml/koelectra-small-v3-nsmc

# 컨테이너 내부 작업 디렉토리
WORKDIR /app

# 의존성 파일을 먼저 복사해서 Docker 캐시를 활용한다.
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 백엔드 소스 코드 복사
COPY . .

# 로컬 기본 포트
EXPOSE 8000

# Render에서는 PORT 환경변수를 사용하고,
# 로컬 Docker 실행에서는 PORT가 없으면 8000번 포트를 사용한다.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
