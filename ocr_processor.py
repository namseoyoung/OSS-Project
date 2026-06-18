import cv2
import easyocr
import requests
import base64
import re
import os
import json

ROBOFLOW_API_KEY = "apicode"
ROBOFLOW_MODEL_ID = "oss-project-labeling/2"
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}"

reader = easyocr.Reader(['ko', 'en'])

STOPWORDS = [
    '사용방법', '주의사항', '내용량', '제조원', '제조국', '고객센터',
    '품목', '용도', '전화', '주소', '보관방법', '경고', '주의',
    'www', 'http', '표준사용량', '품명', '신고번호', '문의'
]

def detect_ingredient_label(img_path, confidence=40, overlap=30):
    if not os.path.exists(img_path):
        print(f"[오류] 이미지 파일이 존재하지 않습니다: {img_path}")
        return None, None

    with open(img_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    params = {
        "confidence": confidence,
        "overlap": overlap
    }

    try:
        response = requests.post(
            ROBOFLOW_URL,
            params=params,
            data=image_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    except Exception as e:
        print(f"[오류] Roboflow API 요청 중 예외가 발생했습니다: {e}")
        return None, None

    if response.status_code != 200:
        print(f"[오류] Roboflow API 호출 실패: {response.status_code}")
        print(response.text)
        return None, None

    result = response.json()
    predictions = result.get("predictions", [])

    if not predictions:
        print("[경고] 성분표 영역을 탐지하지 못했습니다.")
        return None, result

    best_prediction = max(predictions, key=lambda x: x.get("confidence", 0))
    return best_prediction, result

def crop_from_prediction(img_path, prediction, padding=10):
    img = cv2.imread(img_path)

    if img is None:
        print("[오류] 원본 이미지를 불러올 수 없습니다.")
        return None, None

    h, w = img.shape[:2]

    x_center = int(prediction["x"])
    y_center = int(prediction["y"])
    box_w = int(prediction["width"])
    box_h = int(prediction["height"])

    x1 = max(0, x_center - box_w // 2 - padding)
    y1 = max(0, y_center - box_h // 2 - padding)
    x2 = min(w, x_center + box_w // 2 + padding)
    y2 = min(h, y_center + box_h // 2 + padding)

    cropped_img = img[y1:y2, x1:x2]

    if cropped_img is None or cropped_img.size == 0:
        print("[오류] 크롭된 이미지가 비어 있습니다.")
        return None, None

    return cropped_img, (x1, y1, x2, y2)

def preprocess_label_image(cropped_img, blur_kernel=(3, 3), block_size=11, c=2, scale=2.0):
    if cropped_img is None:
        return None

    if block_size % 2 == 0:
        block_size += 1

    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, blur_kernel, 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c
    )

    upscaled = cv2.resize(
        thresh,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )

    return upscaled

def run_easyocr(image):
    if image is None:
        return []

    try:
        return reader.readtext(image, detail=0)
    except Exception as e:
        print(f"[오류] OCR 실행 중 예외가 발생했습니다: {e}")
        return []

def clean_ocr_result(text_list):
    raw_string = "\n".join(text_list)

    clean_string = re.sub(r'[^가-힣a-zA-Z0-9\s,/\-\.\(\)%·:]', '', raw_string)
    clean_string = re.sub(r'[ \t]+', ' ', clean_string)
    clean_string = re.sub(r'\n+', '\n', clean_string).strip()

    tokens = re.split(r'[,/\n;·]+', clean_string)
    tokens = [t.strip() for t in tokens if t.strip()]

    filtered_tokens = []
    for token in tokens:
        if len(token) < 2:
            continue
        if any(stopword in token for stopword in STOPWORDS):
            continue
        filtered_tokens.append(token)

    return raw_string, clean_string, filtered_tokens

def save_image(output_path, image):
    if image is None:
        return None

    try:
        cv2.imwrite(output_path, image)
        return output_path
    except Exception as e:
        print(f"[오류] 이미지 저장에 실패했습니다: {e}")
        return None

def detect_crop_ocr_pipeline(
    img_path,
    confidence=40,
    overlap=30,
    padding=10,
    blur_kernel=(3, 3),
    block_size=11,
    c=2,
    scale=2.0,
    save_outputs=True
):
    result_data = {
        "image_path": img_path,
        "detection_success": False,
        "bbox": None,
        "prediction_confidence": None,
        "cropped_path": None,
        "preprocessed_path": None,
        "original_ocr": {
            "raw_text": "",
            "clean_text": "",
            "ingredient_candidates": []
        },
        "processed_ocr": {
            "raw_text": "",
            "clean_text": "",
            "ingredient_candidates": []
        },
        "message": ""
    }

    prediction, _ = detect_ingredient_label(
        img_path,
        confidence=confidence,
        overlap=overlap
    )

    if prediction is None:
        result_data["message"] = "성분표 영역 탐지 실패"
        return result_data

    cropped_img, bbox = crop_from_prediction(img_path, prediction, padding=padding)

    if cropped_img is None:
        result_data["message"] = "성분표 이미지 크롭 실패"
        return result_data

    result_data["detection_success"] = True
    result_data["bbox"] = bbox
    result_data["prediction_confidence"] = prediction.get("confidence", None)

    base_name = os.path.splitext(os.path.basename(img_path))[0]
    cropped_path = f"{base_name}_cropped_label.jpg"
    preprocessed_path = f"{base_name}_preprocessed_label.jpg"
    json_path = f"{base_name}_ocr_result.json"

    original_text_list = run_easyocr(cropped_img)
    original_raw, original_clean, original_tokens = clean_ocr_result(original_text_list)

    result_data["original_ocr"]["raw_text"] = original_raw
    result_data["original_ocr"]["clean_text"] = original_clean
    result_data["original_ocr"]["ingredient_candidates"] = original_tokens

    processed_img = preprocess_label_image(
        cropped_img,
        blur_kernel=blur_kernel,
        block_size=block_size,
        c=c,
        scale=scale
    )

    if processed_img is None:
        result_data["message"] = "전처리 실패"
        return result_data

    processed_text_list = run_easyocr(processed_img)
    processed_raw, processed_clean, processed_tokens = clean_ocr_result(processed_text_list)

    result_data["processed_ocr"]["raw_text"] = processed_raw
    result_data["processed_ocr"]["clean_text"] = processed_clean
    result_data["processed_ocr"]["ingredient_candidates"] = processed_tokens

    if save_outputs:
        result_data["cropped_path"] = save_image(cropped_path, cropped_img)
        result_data["preprocessed_path"] = save_image(preprocessed_path, processed_img)

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[오류] JSON 저장에 실패했습니다: {e}")

    result_data["message"] = "성공"
    return result_data

def print_result_report(result):
    print("\n=========================================================")
    print("생활화학제품 성분표 탐지 + OCR 통합 결과")
    print("=========================================================")

    print(f"\n[1] 입력 이미지: {result['image_path']}")
    print(f"[2] 탐지 성공 여부: {result['detection_success']}")
    print(f"[3] 바운딩 박스 좌표: {result['bbox']}")
    print(f"[4] 탐지 신뢰도: {result['prediction_confidence']}")
    print(f"[5] 크롭 이미지 저장 경로: {result['cropped_path']}")
    print(f"[6] 전처리 이미지 저장 경로: {result['preprocessed_path']}")
    print(f"[7] 처리 결과 메시지: {result['message']}")

    print("\n---------------------------------------------------------")
    print("[8] 원본 크롭 OCR 정제 결과 미리보기")
    if result["original_ocr"]["clean_text"]:
        print(result["original_ocr"]["clean_text"][:500])
    else:
        print("OCR 텍스트가 없습니다.")

    print("\n---------------------------------------------------------")
    print("[9] 원본 크롭 OCR 성분 후보")
    original_candidates = result["original_ocr"]["ingredient_candidates"]
    print(f"총 후보 개수: {len(original_candidates)}")
    for idx, token in enumerate(original_candidates[:20], 1):
        print(f"  [{idx}] {token}")
    if len(original_candidates) > 20:
        print(f"  ... 그 외 {len(original_candidates) - 20}개")

    print("\n---------------------------------------------------------")
    print("[10] 전처리 후 OCR 정제 결과 미리보기")
    if result["processed_ocr"]["clean_text"]:
        print(result["processed_ocr"]["clean_text"][:500])
    else:
        print("OCR 텍스트가 없습니다.")

    print("\n---------------------------------------------------------")
    print("[11] 전처리 후 OCR 성분 후보")
    processed_candidates = result["processed_ocr"]["ingredient_candidates"]
    print(f"총 후보 개수: {len(processed_candidates)}")
    for idx, token in enumerate(processed_candidates[:20], 1):
        print(f"  [{idx}] {token}")
    if len(processed_candidates) > 20:
        print(f"  ... 그 외 {len(processed_candidates) - 20}개")

    print("=========================================================")

if __name__ == "__main__":
    test_image = "bleach_101.jpg"
    result = detect_crop_ocr_pipeline(
        img_path=test_image,
        confidence=40,
        overlap=30,
        padding=10,
        blur_kernel=(3, 3),
        block_size=11,
        c=2,
        scale=2.0,
        save_outputs=True
    )

    print_result_report(result)
