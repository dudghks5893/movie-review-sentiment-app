from pathlib import Path
import shutil

import torch
from onnxruntime.quantization import QuantType, quantize_dynamic
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer


# ------------------------------------------------------------
# 설정
# ------------------------------------------------------------

MODEL_NAME = "daekeun-ml/koelectra-small-v3-nsmc"
MAX_LENGTH = 128

BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "model_artifacts"

ONNX_MODEL_PATH = ARTIFACT_DIR / "sentiment.onnx"
QUANTIZED_MODEL_PATH = ARTIFACT_DIR / "sentiment_int8.onnx"


class SentimentOnnxWrapper(torch.nn.Module):
    """
    Hugging Face 모델 출력 중 logits만 반환하도록 감싸는 래퍼 클래스.

    SequenceClassifierOutput 전체를 ONNX로 내보내지 않고,
    감성 분류에 필요한 logits만 명확하게 반환한다.
    """

    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        if token_type_ids is not None:
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
            )
        else:
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )

        return outputs.logits


def get_file_size_mb(path: Path) -> float:
    """
    파일 용량을 MB 단위로 반환한다.
    """

    return path.stat().st_size / (1024 * 1024)


def load_model_and_tokenizer():
    """
    Hugging Face tokenizer와 model을 로드한다.

    ONNX export 안정성을 위해 attention 구현을 eager 방식으로 지정한다.
    """

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    config = AutoConfig.from_pretrained(MODEL_NAME)

    # 일부 transformers 버전에서 SDPA attention이 기본으로 사용되면
    # ONNX export 중 scaled_dot_product_attention 오류가 발생할 수 있다.
    # eager 방식으로 고정해서 export 안정성을 높인다.
    try:
        config._attn_implementation = "eager"
    except Exception:
        pass

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        config=config,
    )
    model.eval()

    return tokenizer, model


def export_to_onnx():
    """
    Hugging Face PyTorch 모델을 ONNX 형식으로 변환한다.
    """

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[LOAD] {MODEL_NAME}")

    tokenizer, base_model = load_model_and_tokenizer()
    model = SentimentOnnxWrapper(base_model)
    model.eval()

    # FastAPI 런타임에서 사용할 tokenizer 파일 저장
    tokenizer.save_pretrained(ARTIFACT_DIR)

    sample_text = "배우들의 연기가 좋고 몰입감이 뛰어났습니다."

    encoded = tokenizer(
        sample_text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )

    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    input_names = ["input_ids", "attention_mask"]
    args = [input_ids, attention_mask]

    if "token_type_ids" in encoded:
        token_type_ids = encoded["token_type_ids"]
        input_names.append("token_type_ids")
        args.append(token_type_ids)

    print("[EXPORT] PyTorch -> ONNX")

    torch.onnx.export(
        model,
        tuple(args),
        f=str(ONNX_MODEL_PATH),
        input_names=input_names,
        output_names=["logits"],

        # scaled_dot_product_attention 지원을 위해 opset 14 사용
        opset_version=14,

        do_constant_folding=True,

        # legacy exporter 사용
        # PyTorch 최신 exporter에서 shape가 꼬이는 경우를 피한다.
        dynamo=False,

        # .onnx.data 분리 없이 단일 onnx 파일로 저장한다.
        external_data=False,
    )

    print(f"[OK] ONNX saved: {ONNX_MODEL_PATH}")
    print(f"[SIZE] ONNX FP32: {get_file_size_mb(ONNX_MODEL_PATH):.2f} MB")


def quantize_onnx():
    """
    ONNX 모델을 INT8 동적 양자화한다.

    양자화가 실패해도 FP32 ONNX 모델은 그대로 사용할 수 있도록 처리한다.
    """

    print("[QUANTIZE] ONNX FP32 -> ONNX INT8")

    try:
        quantize_dynamic(
            model_input=str(ONNX_MODEL_PATH),
            model_output=str(QUANTIZED_MODEL_PATH),
            weight_type=QuantType.QInt8,
            extra_options={"DisableShapeInference": True},
        )

        print(f"[OK] Quantized ONNX saved: {QUANTIZED_MODEL_PATH}")
        print(f"[SIZE] ONNX INT8: {get_file_size_mb(QUANTIZED_MODEL_PATH):.2f} MB")

    except Exception as error:
        print("[WARN] INT8 quantization failed.")
        print(f"[WARN] Reason: {error}")
        print("[WARN] FP32 ONNX model will be used instead.")

        # sentiment.py는 sentiment_int8.onnx가 있으면 INT8을 쓰고,
        # 없으면 sentiment.onnx를 사용한다.
        # 따라서 여기서는 실패해도 프로그램을 중단하지 않는다.
        if QUANTIZED_MODEL_PATH.exists():
            QUANTIZED_MODEL_PATH.unlink()


def main():
    """
    전체 변환 프로세스 실행 함수.
    """

    export_to_onnx()
    quantize_onnx()

    print("=== Export Completed ===")

    print("[FILES]")
    for path in sorted(ARTIFACT_DIR.iterdir()):
        if path.is_file():
            print(f"- {path.name}: {get_file_size_mb(path):.2f} MB")


if __name__ == "__main__":
    main()
