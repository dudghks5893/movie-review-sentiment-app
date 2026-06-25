# FastAPI 백엔드를 실행하기 위한 Python 기반 Docker 이미지
FROM python:3.11-slim

# Python이 .pyc 캐시 파일을 만들지 않도록 설정
ENV PYTHONDONTWRITEBYTECODE=1

# 로그가 버퍼링되지 않고 바로 출력되도록 설정
ENV PYTHONUNBUFFERED=1

# Hugging Face 모델명을 환경변수로 관리
ENV SENTIMENT_MODEL_NAME=daekeun-ml/koelectra-small-v3-nsmc

# 컨테이너 내부 작업 디렉토리
WORKDIR /app

# 의존성 파일을 먼저 복사
# Docker 캐시를 활용하기 위해 requirements.txt를 먼저 복사한다.
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 백엔드 소스 코드 복사
COPY . .

# FastAPI 기본 포트
EXPOSE 8000

# 컨테이너 실행 시 FastAPI 서버 시작
# host를 0.0.0.0으로 설정해야 컨테이너 밖에서 접근할 수 있다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
