import os
from typing import Dict

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# 한국어 영화 리뷰 감성 분석용 경량 모델
# Hugging Face 모델 카드 기준 NSMC 영화 리뷰 감성 이진 분류 모델이다.
MODEL_NAME = os.getenv("SENTIMENT_MODEL_NAME", "daekeun-ml/koelectra-small-v3-nsmc")

# 모델은 첫 요청 시 1회만 로드하고 이후 재사용한다.
_tokenizer = None
_model = None


def load_model():
    """
    Hugging Face tokenizer와 model을 로드한다.

    서버 시작 시 바로 로드하지 않고,
    첫 감성 분석 요청이 들어왔을 때만 로드한다.
    이렇게 하면 FastAPI 서버 시작 속도를 줄일 수 있다.
    """

    global _tokenizer, _model

    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.eval()

    return _tokenizer, _model


def fallback_sentiment(text: str) -> Dict[str, float | str]:
    """
    Hugging Face 모델 로드 실패 시 사용할 예비 감성 분석 함수.

    배포 환경에서 모델 다운로드가 실패해도 API 전체가 멈추지 않도록 한다.
    """

    positive_words = [
        "좋", "재밌", "훌륭", "몰입", "추천", "감동", "완성도", "인상적", "최고",
        "흥미", "만족", "명작", "강렬", "세련", "뛰어났", "재미"
    ]

    negative_words = [
        "별로", "지루", "실망", "아쉽", "부족", "최악", "억지", "답답", "아깝",
        "불편", "어색", "산만", "기대보다", "허접"
    ]

    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)

    if positive_count > negative_count:
        return {
            "sentiment_label": "positive",
            "sentiment_score": 0.75,
            "model_name": "fallback-keyword",
        }

    if negative_count > positive_count:
        return {
            "sentiment_label": "negative",
            "sentiment_score": -0.75,
            "model_name": "fallback-keyword",
        }

    return {
        "sentiment_label": "neutral",
        "sentiment_score": 0.0,
        "model_name": "fallback-keyword",
    }


def analyze_sentiment(text: str) -> Dict[str, float | str]:
    """
    리뷰 내용을 입력받아 감성 분석 결과를 반환한다.

    이 모델은 이진 분류 모델이므로 class index 0은 부정,
    class index 1은 긍정으로 해석한다.

    반환 예시:
    {
        "sentiment_label": "positive",
        "sentiment_score": 0.9619,
        "model_name": "daekeun-ml/koelectra-small-v3-nsmc"
    }
    """

    clean_text = text.strip()

    if not clean_text:
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "model_name": MODEL_NAME,
        }

    try:
        tokenizer, model = load_model()

        # 입력 문장을 모델 입력 형식으로 변환한다.
        inputs = tokenizer(
            clean_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128,
        )

        # 추론 시에는 gradient 계산이 필요 없으므로 no_grad를 사용한다.
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)[0]

        # 가장 확률이 높은 class index를 선택한다.
        predicted_index = int(torch.argmax(probabilities).item())
        confidence = float(probabilities[predicted_index].item())

        # 모델 카드 기준 class index 0 = Neg, class index 1 = Pos로 해석한다.
        if predicted_index == 1:
            return {
                "sentiment_label": "positive",
                "sentiment_score": round(confidence, 4),
                "model_name": MODEL_NAME,
            }

        return {
            "sentiment_label": "negative",
            "sentiment_score": round(-confidence, 4),
            "model_name": MODEL_NAME,
        }

    except Exception:
        # 모델 다운로드, 로드, 추론 중 오류 발생 시 예비 분석기로 대체한다.
        return fallback_sentiment(clean_text)
