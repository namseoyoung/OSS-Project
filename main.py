from ingredient_normalizer import IngredientNormalizer
from risk_analyzer import RiskAnalyzer
from risk_explanation import RiskExplanationEngine

from fastapi import FastAPI, HTTPException
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

normalizer = IngredientNormalizer(ALIAS_DB_PATH, threshold=85)
risk_analyzer = RiskAnalyzer(RISK_DB_PATH)
risk_explainer = RiskExplanationEngine(RISK_DB_PATH)


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
