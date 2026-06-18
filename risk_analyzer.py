import pandas as pd


class RiskAnalyzer:
    def __init__(self, risk_db_path):
        self.risk_db = {}
        self.load_risk_db(risk_db_path)

    def find_column(self, df, keyword, exclude=None):
        exclude = exclude or []

        for col in df.columns:
            col_text = str(col)

            if keyword in col_text:
                if all(ex not in col_text for ex in exclude):
                    return col

        return None

    def risk_level_to_scores(self, risk_level):
        risk_level = str(risk_level).strip().lower()

        if risk_level == "low":
            return 1, 1, 1

        if risk_level == "medium":
            return 3, 3, 3

        if risk_level == "high":
            return 5, 5, 5

        return 0, 0, 0

    def load_risk_db(self, risk_db_path):
        df = pd.read_csv(risk_db_path)

        standard_col = self.find_column(df, "standard_name")
        category_col = self.find_column(df, "category")
        risk_level_col = self.find_column(df, "risk_level")
        basis_col = self.find_column(df, "basis")
        warning_col = self.find_column(df, "warning", exclude=["초본"])
        description_col = self.find_column(df, "description")

        if standard_col is None:
            raise ValueError("standard_name 컬럼을 찾을 수 없습니다.")

        if risk_level_col is None:
            raise ValueError("risk_level 컬럼을 찾을 수 없습니다.")

        for _, row in df.iterrows():
            standard_name = str(row[standard_col]).strip().lower()

            if standard_name == "" or standard_name == "nan":
                continue

            risk_level = str(row[risk_level_col]).strip()

            toxicity, irritation, environment = self.risk_level_to_scores(
                risk_level
            )

            self.risk_db[standard_name] = {
                "category": str(row[category_col]).strip() if category_col else "",
                "risk_level": risk_level,
                "basis": str(row[basis_col]).strip() if basis_col else "",
                "warning": str(row[warning_col]).strip() if warning_col else "",
                "description": str(row[description_col]).strip() if description_col else "",
                "toxicity_score": toxicity,
                "irritation_score": irritation,
                "environment_score": environment
            }

    def analyze_ingredient(self, normalized_item):
        if not isinstance(normalized_item, dict):
            return self.unclassified_result(
                normalized_item,
                None,
                "INVALID_NORMALIZED_ITEM"
            )

        if not normalized_item.get("matched", False):
            return self.unclassified_result(
                normalized_item.get("original_name"),
                None,
                normalized_item.get(
                    "error_code",
                    "UNCLASSIFIED_INGREDIENT"
                ),
                normalized_item
            )

        standard_value = normalized_item.get("standard_name")

        if standard_value is None:
            return self.unclassified_result(
                normalized_item.get("original_name"),
                None,
                "MISSING_STANDARD_NAME"
            )

        standard_name = str(standard_value).strip().lower()

        if not standard_name:
            return self.unclassified_result(
                normalized_item.get("original_name"),
                None,
                "MISSING_STANDARD_NAME"
            )

        if standard_name not in self.risk_db:
            return self.unclassified_result(
                normalized_item.get("original_name"),
                standard_name,
                "RISK_DB_NOT_FOUND"
            )

        risk_info = self.risk_db[standard_name]

        risk_score = (
            risk_info["toxicity_score"]
            + risk_info["irritation_score"]
            + risk_info["environment_score"]
        )

        return {
            "original_name": normalized_item["original_name"],
            "standard_name": standard_name,
            "risk_found": True,
            "category": risk_info["category"],
            "risk_level": risk_info["risk_level"],
            "toxicity_score": risk_info["toxicity_score"],
            "irritation_score": risk_info["irritation_score"],
            "environment_score": risk_info["environment_score"],
            "risk_score": risk_score,
            "basis": risk_info["basis"],
            "warning": risk_info["warning"],
            "description": risk_info["description"]
        }

    def unclassified_result(
        self,
        original_name,
        standard_name,
        error_code,
        normalized_item=None
    ):
        result = {
            "original_name": original_name,
            "standard_name": standard_name,
            "risk_found": False,
            "risk_score": 0,
            "risk_level": "Unknown",
            "category": "",
            "basis": "",
            "warning": "",
            "description": "",
            "error_code": error_code
        }

        if isinstance(normalized_item, dict):
            result["similarity_score"] = normalized_item.get(
                "similarity_score",
                0
            )
            result["is_noise"] = normalized_item.get("is_noise", False)

        return result

    def analyze_product(self, normalized_results):
        ingredient_results = []
        total_score = 0
        found_count = 0
        high_count = 0

        for item in normalized_results:
            analyzed = self.analyze_ingredient(item)
            ingredient_results.append(analyzed)

            if analyzed["risk_found"]:
                total_score += analyzed["risk_score"]
                found_count += 1

                if analyzed["risk_level"].lower() == "high":
                    high_count += 1

        if found_count == 0:
            final_score = 0
            final_level = "Unknown"
        else:
            final_score = round(total_score / found_count, 2)
            final_level = self.get_product_risk_level(final_score, high_count)

        return {
            "final_score": final_score,
            "final_risk_level": final_level,
            "ingredient_count": len(normalized_results),
            "matched_risk_count": found_count,
            "ingredient_results": ingredient_results
        }

    def get_product_risk_level(self, final_score, high_count):
        if high_count >= 2:
            return "High"

        if final_score <= 5:
            return "Low"
        elif final_score <= 10:
            return "Medium"
        else:
            return "High"
