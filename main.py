from ingredient_normalizer import IngredientNormalizer
from risk_analyzer import RiskAnalyzer
from risk_explanation import RiskExplanationEngine

import os
import re
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


ALIAS_DB_PATH = "ingredient_alias.csv"
RISK_DB_PATH = "ingredient_risk.csv"

app = FastAPI(
    title="ChemiCheck API",
    description="생활화학제품 성분 정규화, 위험도 분석, 위험도 설명 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

normalizer = IngredientNormalizer(ALIAS_DB_PATH, threshold=75)
risk_analyzer = RiskAnalyzer(RISK_DB_PATH)
risk_explainer = RiskExplanationEngine(RISK_DB_PATH)

OCR_NOISE_WORDS = [
    "사용물질",
    "주요물질",
    "주요 물질",
    "성분",
    "전성분",
    "함유성분",
    "사용방법",
    "주의사항",
    "품명",
    "품번",
    "용량",
    "제조원",
    "판매원",
    "고객센터",
    "안전기준",
    "신고번호",
    "주소",
    "사업자",
    "대표자",
    "문의",
    "홈페이지",
    "전화",
    "팩스",
    "인터내셔널",
]

OCR_ADDRESS_WORDS = [
    "서울특별시",
    "경기",
    "경기도",
    "화성시",
    "처신면",
    "전곡산단",
    "인천광역시",
    "부산광역시",
    "대구광역시",
    "광주광역시",
    "대전광역시",
    "울산광역시",
    "세종특별자치시",
    "산단",
]

INGREDIENT_HINT_WORDS = [
    "산",
    "나트륨",
    "칼륨",
    "암모늄",
    "염",
    "알코올",
    "에탄올",
    "향료",
    "오일",
    "글리콜",
    "클로라이드",
    "설페이트",
    "벤질",
    "리모넨",
    "리날로올",
    "계면활성제",
    "추출물",
    "정제수",
]


def normalize_ocr_text(value):
    return re.sub(r"[\s,./·ㆍ:;|+\-_\[\](){}]", "", str(value or "").lower())


def strip_ocr_noise(value):
    text = str(value or "").strip()
    text = re.sub(r"\d{2,4}[-\s]\d{3,4}[-\s]?\d{0,4}", " ", text)

    for word in OCR_NOISE_WORDS:
        text = text.replace(word, " ")

    text = re.sub(r"\s+", " ", text).strip(" :;,/·ㆍ")
    return text


def is_noise_candidate(value):
    text = str(value or "").strip()
    compact = re.sub(r"\s+", "", text)

    if not compact:
        return True

    if re.search(r"\d{2,4}[-\s]\d{3,4}[-\s]?\d{0,4}", text):
        return True

    if re.search(r"\d+\s*(층|호|길|로|번길|번지)", text):
        return True

    if any(word in text for word in OCR_ADDRESS_WORDS):
        return True

    digit_count = len(re.findall(r"\d", text))
    letter_count = len(re.findall(r"[가-힣a-zA-Z]", text))

    return digit_count >= 3 and digit_count >= letter_count


def is_likely_ingredient_candidate(value):
    text = str(value or "").strip()

    if is_noise_candidate(text):
        return False

    if extract_alias_candidates(text):
        return True

    return any(word in text for word in INGREDIENT_HINT_WORDS)


def extract_alias_candidates(text):
    normalized_text = normalize_ocr_text(text)
    found = []

    if not normalized_text:
        return found

    for alias in normalizer.alias_list:
        alias_text = str(alias or "").strip()

        if len(alias_text) < 2:
            continue

        normalized_alias = normalize_ocr_text(alias_text)

        if normalized_alias and normalized_alias in normalized_text:
            standard_name = normalizer.alias_dict.get(alias_text.lower(), alias_text)

            if standard_name not in found:
                found.append(standard_name)

    return found


def build_ingredient_candidates(ocr_candidates, raw_text, clean_text):
    candidates = []

    def add_candidate(value):
        value = str(value or "").strip()

        if value and value not in candidates:
            candidates.append(value)

    for source_text in [raw_text, clean_text, *ocr_candidates]:
        for alias_candidate in extract_alias_candidates(source_text):
            add_candidate(alias_candidate)

    for candidate in ocr_candidates:
        cleaned = strip_ocr_noise(candidate)

        if not cleaned:
            continue

        if len(cleaned) > 30:
            continue

        if not is_likely_ingredient_candidate(cleaned):
            continue

        add_candidate(cleaned)

    return candidates


def build_no_candidate_detail(ocr_result, ocr_candidates):
    message = str(ocr_result.get("message") or "").strip()

    if message and message != "성공":
        return message

    if ocr_candidates:
        sample_candidates = ", ".join(ocr_candidates[:3])
        return (
            "OCR은 완료됐지만 성분 후보를 찾지 못했습니다. "
            "라벨의 성분 영역을 더 크게 촬영하거나 성분 DB/alias를 확인해 주세요. "
            f"OCR 후보 예: {sample_candidates}"
        )

    return "OCR은 완료됐지만 읽어낸 텍스트에서 성분 후보를 찾지 못했습니다."


def dedupe_normalized_results(normalized_results):
    deduped = []
    seen = set()

    for item in normalized_results:
        if item.get("matched") and item.get("standard_name"):
            key = ("matched", str(item["standard_name"]).strip().lower())
        else:
            key = ("unmatched", str(item.get("original_name", "")).strip().lower())

        if key in seen:
            continue

        seen.add(key)
        deduped.append(item)

    return deduped


class AnalyzeIngredientsRequest(BaseModel):
    ingredients: list[str] = Field(
        ...,
        description="OCR/성분 추출 모듈에서 넘겨받은 성분명 리스트"
    )


class RiskExplanationRequest(BaseModel):
    final_risk_level: str = "Unknown"
    ingredient_count: int | None = None
    matched_risk_count: int | None = None
    ingredient_results: list[dict] = Field(
        default_factory=list,
        description="RiskAnalyzer가 반환한 ingredient_results 리스트"
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "chemicheck-api",
    }


@app.post("/api/analyze-ingredients")
def analyze_ingredients(request: AnalyzeIngredientsRequest):
    if not request.ingredients:
        raise HTTPException(
            status_code=400,
            detail="ingredients 배열이 비어 있습니다."
        )

    normalized_results = normalizer.normalize_ingredients(
        request.ingredients
    )

    product_risk = risk_analyzer.analyze_product(
        normalized_results
    )

    risk_explanation = risk_explainer.explain_product(
        product_risk
    )

    return {
        "normalized_results": normalized_results,
        "risk_analysis": product_risk,
        "risk_explanation": risk_explanation,
    }


@app.post("/api/analyze-label")
async def analyze_label_image(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="이미지 파일만 업로드할 수 있습니다."
        )

    suffix = os.path.splitext(image.filename or "")[1] or ".jpg"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            temp_file.write(await image.read())

        try:
            from ocr_processor import detect_crop_ocr_pipeline

            ocr_result = detect_crop_ocr_pipeline(
                img_input=temp_path,
                confidence=30,
                overlap=30,
                padding=10,
                save_outputs=False
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"OCR 처리 중 오류가 발생했습니다: {exc}"
            ) from exc

        original_ocr = ocr_result.get("original_ocr", {})
        processed_ocr = ocr_result.get("processed_ocr", {})
        raw_text = processed_ocr.get("raw_text") or original_ocr.get("raw_text", "")
        clean_text = processed_ocr.get("clean_text") or original_ocr.get("clean_text", "")
        ocr_candidates = []

        for candidate in (
            processed_ocr.get("ingredient_candidates", [])
            + original_ocr.get("ingredient_candidates", [])
        ):
            if candidate not in ocr_candidates:
                ocr_candidates.append(candidate)

        ingredients = build_ingredient_candidates(
            ocr_candidates,
            raw_text,
            clean_text
        )

        if not ingredients:
            raise HTTPException(
                status_code=422,
                detail=build_no_candidate_detail(ocr_result, ocr_candidates)
            )

        normalized_results = dedupe_normalized_results(
            normalizer.normalize_ingredients(
                ingredients
            )
        )

        product_risk = risk_analyzer.analyze_product(
            normalized_results
        )

        risk_explanation = risk_explainer.explain_product(
            product_risk
        )

        return {
            "ocr": {
                "raw_text": raw_text,
                "clean_text": clean_text,
                "ingredients": ingredients,
                "detection_success": ocr_result.get("detection_success"),
                "bbox": ocr_result.get("bbox"),
                "prediction_confidence": ocr_result.get("prediction_confidence"),
            },
            "normalized_results": normalized_results,
            "risk_analysis": product_risk,
            "risk_explanation": risk_explanation,
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/risk-explanations")
def create_risk_explanations(request: RiskExplanationRequest):
    product_risk = {
        "final_risk_level": request.final_risk_level,
        "ingredient_count": request.ingredient_count or len(request.ingredient_results),
        "matched_risk_count": request.matched_risk_count or 0,
        "ingredient_results": request.ingredient_results,
    }

    return risk_explainer.explain_product(product_risk)


def demo():
    print("프로그램 실행 시작")

    ocr_ingredients = [
        "차아염소산나트륨늄",
        "향료",
        "Unknown Chemical"
    ]

    normalized_results = normalizer.normalize_ingredients(
        ocr_ingredients
    )

    product_risk = risk_analyzer.analyze_product(
        normalized_results
    )

    print("\n=== 성분 정규화 결과 ===")
    for item in normalized_results:
        print(item)

    print("\n=== 성분별 위험도 분석 결과 ===")
    for item in product_risk["ingredient_results"]:
        print(f"입력 성분명: {item['original_name']}")
        print(f"표준 성분명: {item['standard_name']}")
        print(f"위험도 DB 매칭 여부: {item['risk_found']}")
        print(f"성분 위험 점수: {item['risk_score']}")
        print(f"성분 위험 등급: {item['risk_level']}")
        print("-" * 30)

    print("\n=== 제품 최종 위험도 ===")
    print(f"최종 점수: {product_risk['final_score']}")
    print(f"최종 위험 등급: {product_risk['final_risk_level']}")
    print(f"전체 성분 수: {product_risk['ingredient_count']}")
    print(f"위험도 DB 매칭 성분 수: {product_risk['matched_risk_count']}")

    risk_explanation = risk_explainer.explain_product(product_risk)

    print("\n=== 위험도 설명 결과 ===")
    for item in risk_explanation["ingredient_explanations"]:
        print(f"성분명: {item['standard_name']}")
        print(f"위험도: {item['risk_label']}")
        print(f"설명: {item['description']}")
        print(f"주의사항: {item['warning']}")
        print("-" * 30)


if __name__ == "__main__":
    demo()
