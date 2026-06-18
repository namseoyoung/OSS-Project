import pandas as pd


class RiskExplanationEngine:
    def __init__(self, risk_db_path):
        self.explanation_db = {}
        self.load_explanation_db(risk_db_path)

    def find_column(self, df, keyword, exclude=None):
        exclude = exclude or []

        for col in df.columns:
            col_text = str(col)

            if keyword in col_text:
                if all(ex not in col_text for ex in exclude):
                    return col

        return None

    def normalize_key(self, value):
        return str(value or "").strip().lower()

    def clean_text(self, value):
        text = str(value or "").strip()
        return "" if text.lower() == "nan" else text

    def load_explanation_db(self, risk_db_path):
        df = pd.read_csv(risk_db_path)

        standard_col = self.find_column(df, "standard_name")
        category_col = self.find_column(df, "category")
        risk_level_col = self.find_column(df, "risk_level")
        basis_col = self.find_column(df, "basis")
        warning_col = self.find_column(df, "warning", exclude=["초본"])
        description_col = self.find_column(df, "description")

        if standard_col is None:
            raise ValueError("standard_name 컬럼을 찾을 수 없습니다.")

        for _, row in df.iterrows():
            standard_name = self.normalize_key(row[standard_col])

            if not standard_name or standard_name == "nan":
                continue

            self.explanation_db[standard_name] = {
                "standard_name": self.clean_text(row[standard_col]),
                "category": self.clean_text(row[category_col]) if category_col else "",
                "risk_level": self.clean_text(row[risk_level_col]) if risk_level_col else "Unknown",
                "basis": self.clean_text(row[basis_col]) if basis_col else "",
                "warning": self.clean_text(row[warning_col]) if warning_col else "",
                "description": self.clean_text(row[description_col]) if description_col else "",
            }

    def get_risk_label_ko(self, risk_level):
        normalized = self.normalize_key(risk_level)

        labels = {
            "low": "낮음",
            "medium": "보통",
            "high": "높음",
            "unknown": "확인 필요",
        }

        return labels.get(normalized, "확인 필요")

    def get_default_warning(self, risk_level):
        normalized = self.normalize_key(risk_level)

        if normalized == "high":
            return "사용 전 환기, 보호장비 착용, 혼합 금지 조건을 반드시 확인하세요."

        if normalized == "medium":
            return "사용량을 지키고 환기하며, 피부나 눈에 직접 닿지 않도록 주의하세요."

        if normalized == "low":
            return "일반적인 사용 조건에서는 우려가 낮지만 제품 표시사항을 지켜 사용하세요."

        return "성분 정보가 부족하므로 제품 표시사항과 안전 정보를 추가로 확인하세요."

    def build_template_sentence(self, ingredient_info):
        standard_name = ingredient_info["standard_name"]
        category = ingredient_info.get("category", "")
        risk_level = ingredient_info.get("risk_level", "Unknown")
        risk_label = self.get_risk_label_ko(risk_level)
        basis = ingredient_info.get("basis", "")

        sentence = f"{standard_name}은(는) 위험도 '{risk_label}' 등급으로 분류됩니다."

        if category:
            sentence += f" 이 성분은 {category}에 해당합니다."

        if basis:
            sentence += f" 분류 근거는 {basis}입니다."

        return sentence

    def explain_ingredient(self, ingredient_result):
        original_name = ingredient_result.get("original_name")
        standard_name = ingredient_result.get("standard_name")
        lookup_name = self.normalize_key(standard_name or original_name)
        matched = self.explanation_db.get(lookup_name)

        if matched is None:
            risk_level = ingredient_result.get("risk_level", "Unknown")
            fallback_name = standard_name or original_name or "알 수 없는 성분"

            matched = {
                "standard_name": fallback_name,
                "category": ingredient_result.get("category", ""),
                "risk_level": risk_level,
                "basis": ingredient_result.get("basis", ""),
                "warning": ingredient_result.get("warning", ""),
                "description": ingredient_result.get("description", ""),
            }

        risk_level = ingredient_result.get("risk_level") or matched.get("risk_level", "Unknown")
        warning = ingredient_result.get("warning") or matched.get("warning") or self.get_default_warning(risk_level)
        description = ingredient_result.get("description") or matched.get("description")

        if not description:
            description = self.build_template_sentence({**matched, "risk_level": risk_level})

        return {
            "original_name": original_name,
            "standard_name": matched["standard_name"],
            "category": ingredient_result.get("category") or matched.get("category", ""),
            "risk_level": risk_level,
            "risk_label": self.get_risk_label_ko(risk_level),
            "basis": ingredient_result.get("basis") or matched.get("basis", ""),
            "description": description,
            "warning": warning,
            "template_type": "csv_matched" if lookup_name in self.explanation_db else "fallback",
        }

    def explain_product(self, product_risk):
        ingredient_results = product_risk.get("ingredient_results", [])
        explanations = [
            self.explain_ingredient(item)
            for item in ingredient_results
        ]

        return {
            "final_risk_level": product_risk.get("final_risk_level", "Unknown"),
            "final_risk_label": self.get_risk_label_ko(product_risk.get("final_risk_level", "Unknown")),
            "ingredient_count": product_risk.get("ingredient_count", len(explanations)),
            "matched_risk_count": product_risk.get("matched_risk_count", 0),
            "ingredient_explanations": explanations,
        }
