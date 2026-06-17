import pandas as pd


class RiskAnalyzer:
    def __init__(self, risk_db_path):
        self.risk_db = {}
        self.load_risk_db(risk_db_path)

    def load_risk_db(self, risk_db_path):
        df = pd.read_csv(risk_db_path)

        for _, row in df.iterrows():
            standard_name = str(row["standard_name"]).strip().lower()

            self.risk_db[standard_name] = {
                "toxicity_score": int(row["toxicity_score"]),
                "irritation_score": int(row["irritation_score"]),
                "environment_score": int(row["environment_score"])
            }

    def analyze_ingredient(self, normalized_item):
        if not isinstance(normalized_item, dict):
            return self.unclassified_result(
                normalized_item,
                None,
                "INVALID_NORMALIZED_ITEM"
            )

        if not normalized_item.get("matched", False):
            return {
                "original_name": normalized_item.get("original_name"),
                "standard_name": None,
                "risk_found": False,
                "risk_score": 0,
                "risk_level": "Unknown",
                "error_code": normalized_item.get(
                    "error_code",
                    "UNCLASSIFIED_INGREDIENT"
                )
            }

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
            return {
                "original_name": normalized_item.get("original_name"),
                "standard_name": standard_name,
                "risk_found": False,
                "risk_score": 0,
                "risk_level": "Unknown",
                "error_code": "RISK_DB_NOT_FOUND"
            }

        risk_info = self.risk_db[standard_name]

        risk_score = (
            risk_info["toxicity_score"]
            + risk_info["irritation_score"]
            + risk_info["environment_score"]
        )

        risk_level = self.get_ingredient_risk_level(risk_score)

        return {
            "original_name": normalized_item["original_name"],
            "standard_name": standard_name,
            "risk_found": True,
            "toxicity_score": risk_info["toxicity_score"],
            "irritation_score": risk_info["irritation_score"],
            "environment_score": risk_info["environment_score"],
            "risk_score": risk_score,
            "risk_level": risk_level
        }

    def unclassified_result(self, original_name, standard_name, error_code):
        return {
            "original_name": original_name,
            "standard_name": standard_name,
            "risk_found": False,
            "risk_score": 0,
            "risk_level": "Unknown",
            "error_code": error_code
        }

    def get_ingredient_risk_level(self, risk_score):
        if risk_score <= 5:
            return "Low"
        elif risk_score <= 10:
            return "Medium"
        else:
            return "High"

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

                if analyzed["risk_level"] == "High":
                    high_count += 1

        if found_count == 0:
            final_score = 0
            final_level = "Unknown"
        else:
            average_score = total_score / found_count
            final_score = round(average_score, 2)
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
