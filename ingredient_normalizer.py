import re
import unicodedata

import pandas as pd
from rapidfuzz import fuzz


class IngredientNormalizer:
    def __init__(
        self,
        dataset_path,
        threshold=90,
        short_threshold=95,
        ambiguity_margin=3,
        max_length_difference=7,
        noise_threshold=55,
        hangul_threshold=84
    ):
        self.alias_dict = {}
        self.alias_list = []
        self.threshold = threshold
        self.short_threshold = short_threshold
        self.ambiguity_margin = ambiguity_margin
        self.max_length_difference = max_length_difference
        self.noise_threshold = noise_threshold
        self.hangul_threshold = hangul_threshold
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

        input_numbers = self.extract_numbers(ingredient)
        best_by_standard = {}

        for alias in self.alias_list:
            if self.extract_numbers(alias) != input_numbers:
                continue

            compact_alias = re.sub(r"\s+", "", alias)
            if len(compact_alias) < 2:
                continue

            text_score = max(
                fuzz.ratio(ingredient, alias),
                fuzz.token_set_ratio(ingredient, alias),
                fuzz.WRatio(ingredient, alias)
            )
            hangul_score = fuzz.ratio(
                self.decompose_hangul(ingredient),
                self.decompose_hangul(alias)
            )
            score = max(text_score, hangul_score)
            standard_name = self.alias_dict[alias]
            current = best_by_standard.get(standard_name)

            if current is None or score > current["score"]:
                best_by_standard[standard_name] = {
                    "alias": alias,
                    "score": score,
                    "text_score": text_score,
                    "hangul_score": hangul_score
                }

        candidates = sorted(
            best_by_standard.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )

        if not candidates:
            return self.unclassified_result(
                ingredient_name,
                None,
                0,
                "숫자 정보가 일치하는 후보 성분이 없습니다."
            )

        best_standard, best_match = candidates[0]
        best_alias = best_match["alias"]
        best_score = best_match["score"]
        best_text_score = best_match["text_score"]
        best_hangul_score = best_match["hangul_score"]
        second_score = candidates[1][1]["score"] if len(candidates) > 1 else 0
        required_threshold = (
            self.short_threshold
            if len(ingredient.replace(" ", "")) <= 5
            else self.threshold
        )

        is_ambiguous = (
            len(candidates) > 1
            and best_score - second_score < self.ambiguity_margin
        )
        has_valid_length = (
            abs(len(ingredient) - len(best_alias))
            <= self.max_length_difference
        )
        passes_similarity = (
            best_text_score >= required_threshold
            or (
                self.has_hangul(ingredient)
                and best_hangul_score >= self.hangul_threshold
            )
        )

        if (
            passes_similarity
            and not is_ambiguous
            and has_valid_length
        ):
            return {
                "original_name": ingredient_name,
                "standard_name": best_standard,
                "match_type": "similarity",
                "similarity_score": best_score,
                "text_similarity_score": best_text_score,
                "hangul_similarity_score": best_hangul_score,
                "second_similarity_score": second_score,
                "required_threshold": required_threshold,
                "matched_alias": best_alias,
                "matched": True,
                "status": "MATCHED",
                "error_code": None,
                "message": "Similarity Match를 통해 성분명 정규화에 성공했습니다."
            }

        if is_ambiguous:
            message = "유사한 후보가 여러 개라 자동 분류하지 않았습니다."
        elif not has_valid_length:
            message = "입력값과 후보 성분명의 길이 차이가 커 자동 분류하지 않았습니다."
        else:
            message = "유사도 임계값을 충족하지 못한 미분류/신규 화학물질입니다."

        return self.unclassified_result(
            ingredient_name,
            best_alias,
            best_score,
            message,
            second_score,
            required_threshold
        )

    def extract_numbers(self, value):
        return tuple(re.findall(r"\d+", str(value)))

    def decompose_hangul(self, value):
        normalized = unicodedata.normalize("NFD", str(value).lower())
        return "".join(char for char in normalized if not char.isspace())

    def has_hangul(self, value):
        return bool(re.search(r"[가-힣]", str(value)))

    def unclassified_result(
        self,
        ingredient_name,
        best_alias,
        best_score,
        message,
        second_score=0,
        required_threshold=None
    ):
        return {
            "original_name": ingredient_name,
            "standard_name": None,
            "match_type": None,
            "similarity_score": best_score,
            "second_similarity_score": second_score,
            "required_threshold": required_threshold,
            "matched_alias": best_alias,
            "matched": False,
            "status": "UNCLASSIFIED_CHEMICAL",
            "error_code": "CHEM_001",
            "is_noise": best_alias is not None and best_score < self.noise_threshold,
            "message": message
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
            convert_list = [ingredient_list]
        else:
            convert_list = ingredient_list

        for ingredient in convert_list:
            ingredient = str(ingredient).strip(",. -_\n\r\t")
            if not ingredient:
                continue

            result = self.normalize_one(ingredient)

            if result.get("is_noise", False):
                continue

            results.append(result)

        return results
