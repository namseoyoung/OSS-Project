import pandas as pd
from rapidfuzz import fuzz


class IngredientNormalizer:
    def __init__(self, dataset_path, threshold=85):
        self.alias_dict = {}
        self.alias_list = []
        self.threshold = threshold
        self.load_dataset(dataset_path)

    def load_dataset(self, dataset_path):
        df = pd.read_csv(dataset_path)

        for _, row in df.iterrows():
            standard_value = row["standard_name"]

            if pd.isna(standard_value):
                continue

            standard_name = str(standard_value).strip().lower()

            if standard_name == "" or standard_name == "nan":
                continue

            self.alias_dict[standard_name] = standard_name
            self.alias_list.append(standard_name)

            aliases_value = row["aliases"]

            if pd.isna(aliases_value):
                aliases = []
            else:
                aliases = str(aliases_value).split(",")

            for alias in aliases:
                alias = alias.strip().lower()

                if alias and alias != "nan":
                    self.alias_dict[alias] = standard_name
                    self.alias_list.append(alias)

    def exact_match(self, ingredient_name):
        ingredient = str(ingredient_name).strip().lower()

        if ingredient in self.alias_dict:
            return {
                "original_name": ingredient_name,
                "standard_name": self.alias_dict[ingredient],
                "match_type": "exact",
                "similarity_score": 100,
                "matched_alias": ingredient,
                "matched": True,
                "status": "MATCHED",
                "error_code": None,
                "message": "Exact Match를 통해 성분명 정규화에 성공했습니다."
            }

        return None

    def similarity_match(self, ingredient_name):
        ingredient = str(ingredient_name).strip().lower()

        best_alias = None
        best_score = 0

        for alias in self.alias_list:
            score = fuzz.ratio(ingredient, alias)

            if score > best_score:
                best_score = score
                best_alias = alias

        if best_score >= self.threshold:
            return {
                "original_name": ingredient_name,
                "standard_name": self.alias_dict[best_alias],
                "match_type": "similarity",
                "similarity_score": best_score,
                "matched_alias": best_alias,
                "matched": True,
                "status": "MATCHED",
                "error_code": None,
                "message": "Similarity Match를 통해 성분명 정규화에 성공했습니다."
            }

        return {
            "original_name": ingredient_name,
            "standard_name": None,
            "match_type": None,
            "similarity_score": best_score,
            "matched_alias": best_alias,
            "matched": False,
            "status": "UNCLASSIFIED_CHEMICAL",
            "error_code": "CHEM_001",
            "message": "Exact Match와 Similarity Match 모두 실패한 미분류/신규 화학물질입니다."
        }

    def normalize_one(self, ingredient_name):
        if ingredient_name is None:
            return {
                "original_name": ingredient_name,
                "standard_name": None,
                "match_type": None,
                "similarity_score": 0,
                "matched_alias": None,
                "matched": False,
                "status": "INVALID_INPUT",
                "error_code": "CHEM_000",
                "message": "입력 성분명이 None입니다."
            }

        ingredient_text = str(ingredient_name).strip()

        if ingredient_text == "":
            return {
                "original_name": ingredient_name,
                "standard_name": None,
                "match_type": None,
                "similarity_score": 0,
                "matched_alias": None,
                "matched": False,
                "status": "INVALID_INPUT",
                "error_code": "CHEM_000",
                "message": "입력 성분명이 비어 있습니다."
            }

        exact_result = self.exact_match(ingredient_text)

        if exact_result is not None:
            return exact_result

        return self.similarity_match(ingredient_text)

    def normalize_ingredients(self, ingredient_list):
        results = []

        if ingredient_list is None:
            return results

        if isinstance(ingredient_list, str):
            ingredient_list = [ingredient_list]

        for ingredient in ingredient_list:
            result = self.normalize_one(ingredient)
            results.append(result)

        return results
