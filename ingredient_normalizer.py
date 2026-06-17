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
        ingredient = ingredient_name.strip().lower()

        if ingredient in self.alias_dict:
            return {
                "original_name": ingredient_name,
                "standard_name": self.alias_dict[ingredient],
                "match_type": "exact",
                "similarity_score": 100,
                "matched_alias": ingredient,
                "matched": True
            }

        return None

    def similarity_match(self, ingredient_name):
        ingredient = ingredient_name.strip().lower()

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
                "matched": True
            }

        return {
            "original_name": ingredient_name,
            "standard_name": None,
            "match_type": None,
            "similarity_score": best_score,
            "matched_alias": best_alias,
            "matched": False
        }

    def normalize_one(self, ingredient_name):
        exact_result = self.exact_match(ingredient_name)

        if exact_result is not None:
            return exact_result

        return self.similarity_match(ingredient_name)

    def normalize_ingredients(self, ingredient_list):
        results = []

        for ingredient in ingredient_list:
            result = self.normalize_one(ingredient)
            results.append(result)

        return results