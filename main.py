from ingredient_normalizer import IngredientNormalizer
from risk_analyzer import RiskAnalyzer


def main():
    print("프로그램 실행 시작")

    normalizer = IngredientNormalizer(
        "ingredient_alias.csv",
        threshold=85
    )

    risk_analyzer = RiskAnalyzer(
        "ingredient_risk.csv"
    )

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


if __name__ == "__main__":
    main()