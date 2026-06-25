import os
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer


# ------------------------------------------------------------
# 설정
# ------------------------------------------------------------

MODEL_NAME = os.getenv("SENTIMENT_MODEL_NAME", "daekeun-ml/koelectra-small-v3-nsmc")

BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "model_artifacts"

# INT8 양자화 모델을 우선 사용하고, 없으면 FP32 ONNX 모델을 사용한다.
QUANTIZED_MODEL_PATH = ARTIFACT_DIR / "sentiment_int8.onnx"
FP32_MODEL_PATH = ARTIFACT_DIR / "sentiment.onnx"

_tokenizer = None
_session = None
_loaded_model_type = None


def get_model_path_and_type() -> Tuple[Path, str]:
    """
    사용할 ONNX 모델 경로와 모델 타입을 반환한다.

    1순위: INT8 양자화 모델
    2순위: FP32 ONNX 모델
    """

    if QUANTIZED_MODEL_PATH.exists():
        return QUANTIZED_MODEL_PATH, "onnx-int8"

    if FP32_MODEL_PATH.exists():
        return FP32_MODEL_PATH, "onnx-fp32"

    raise FileNotFoundError(
        "ONNX model file not found. Run `python backend/export_onnx.py` first."
    )


def load_onnx_runtime():
    """
    tokenizer와 ONNX Runtime 세션을 로드한다.

    최초 요청 시 1회만 로드하고 이후에는 재사용한다.
    """

    global _tokenizer, _session, _loaded_model_type

    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(ARTIFACT_DIR)

    if _session is None:
        model_path, model_type = get_model_path_and_type()

        _session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )
        _loaded_model_type = model_type

    return _tokenizer, _session, _loaded_model_type


def fallback_sentiment(text: str) -> Dict[str, float | str]:
    """
    ONNX 모델 로드 실패 시 사용할 예비 감성 분석 함수.

    모델 파일 누락 또는 런타임 오류가 발생해도 API 전체가 중단되지 않도록 한다.
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


def softmax(logits: np.ndarray) -> np.ndarray:
    """
    logits 값을 확률값으로 변환한다.
    """

    logits = logits - np.max(logits, axis=1, keepdims=True)
    exp_values = np.exp(logits)
    return exp_values / np.sum(exp_values, axis=1, keepdims=True)


def analyze_sentiment(text: str) -> Dict[str, float | str]:
    """
    리뷰 내용을 입력받아 ONNX Runtime으로 감성 분석을 수행한다.

    class index 0: negative
    class index 1: positive
    """

    clean_text = text.strip()

    if not clean_text:
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "model_name": "onnx-runtime",
        }

    try:
        tokenizer, session, model_type = load_onnx_runtime()

        encoded = tokenizer(
            clean_text,
            return_tensors="np",
            truncation=True,
            padding="max_length",
            max_length=128,
        )

        required_input_names = [input_meta.name for input_meta in session.get_inputs()]

        ort_inputs = {
            name: encoded[name].astype(np.int64)
            for name in required_input_names
            if name in encoded
        }

        outputs = session.run(None, ort_inputs)
        logits = outputs[0]
        probabilities = softmax(logits)[0]

        predicted_index = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_index])

        if predicted_index == 1:
            return {
                "sentiment_label": "positive",
                "sentiment_score": round(confidence, 4),
                "model_name": model_type,
            }

        return {
            "sentiment_label": "negative",
            "sentiment_score": round(-confidence, 4),
            "model_name": model_type,
        }

    except Exception:
        return fallback_sentiment(clean_text)
