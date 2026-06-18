import cv2
import easyocr
import requests
import base64
import re
import os
import json
import numpy as np

ROBOFLOW_API_KEY = "api code"
ROBOFLOW_MODEL_ID = "oss-project-labeling/2"
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}"

reader = None


def get_ocr_reader():
    global reader

    if reader is None:
        reader = easyocr.Reader(['ko', 'en'])

    return reader

STOPWORDS = [
    '사용방법', '주의사항', '내용량', '제조원', '제조국', '고객센터',
    '품목', '용도', '전화', '주소', '보관방법', '경고', '주의',
    'www', 'http', '표준사용량', '품명', '신고번호', '문의'
]

def parse_input_image(img_input):
    """경로, 바이트, Base64 등 다양한 웹 입력 포맷을 OpenCV 이미지와 Base64 스트링으로 통합 파싱"""
    image_bytes = None
    img_cv = None

    if isinstance(img_input, str):
        if os.path.exists(img_input):
            with open(img_input, "rb") as f:
                image_bytes = f.read()
            img_cv = cv2.imread(img_input)
        else:
            if "," in img_input:
                img_input = img_input.split(",")[1]
            image_bytes = base64.b64decode(img_input)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    elif isinstance(img_input, bytes):
        image_bytes = img_input
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
    elif hasattr(img_input, 'read'):
        image_bytes = img_input.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image_bytes is None or img_cv is None:
        return None, None

    image_b64_string = base64.b64encode(image_bytes).decode("utf-8")
    return image_b64_string, img_cv


def detect_ingredient_label_v2(image_b64_string, confidence=30, overlap=30):
    if not image_b64_string:
        print("[오류] 유효한 이미지 데이터가 없습니다.")
        return None, None

    params = {"confidence": confidence, "overlap": overlap}

    try:
        response = requests.post(
            ROBOFLOW_URL,
            params=params,
            data=image_b64_string,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    except Exception as e:
        print(f"[오류] Roboflow API 요청 실패: {e}")
        return None, None

    if response.status_code != 200:
        print(f"[오류] Roboflow API 응답 실패: {response.status_code}")
        return None, None

    result = response.json()
    predictions = result.get("predictions", [])

    if not predictions:
        print("[경고] 성분표 영역을 탐지하지 못했습니다.")
        return None, result

    best_prediction = max(predictions, key=lambda x: x.get("confidence", 0))
    return best_prediction, result


def crop_from_prediction_v2(img_cv, prediction, padding=10):
    if img_cv is None:
        return None, None

    h, w = img_cv.shape[:2]
    x_center = int(prediction["x"])
    y_center = int(prediction["y"])
    box_w = int(prediction["width"])
    box_h = int(prediction["height"])

    x1 = max(0, x_center - box_w // 2 - padding)
    y1 = max(0, y_center - box_h // 2 - padding)
    x2 = min(w, x_center + box_w // 2 + padding)
    y2 = min(h, y_center + box_h // 2 + padding)

    cropped_img = img_cv[y1:y2, x1:x2]
    if cropped_img is None or cropped_img.size == 0:
        return None, None

    return cropped_img, (x1, y1, x2, y2)


def preprocess_label_image(cropped_img, blur_kernel=(3, 3), block_size=31, c=3, scale=4.0):
    if cropped_img is None:
        return None

    if block_size < 3:
        block_size = 3
    if block_size % 2 == 0:
        block_size += 1

    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, blur_kernel, 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
    )
    upscaled = cv2.resize(
        thresh, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
    )
    return upscaled


def run_easyocr(image):
    if image is None:
        return []
    try:
        return get_ocr_reader().readtext(image, detail=0)
    except Exception as e:
        print(f"[오류] OCR 실행 중 예외 발생: {e}")
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
        token = re.sub(r'^[가-힣\s]+[:：]', '', token).strip() # 주성분: 등 접두사 제거
        token = re.sub(r'\([^)]*\)', '', token).strip()       # 성분명 뒤의 괄호 설명 제거
        
        if len(token) < 2:
            continue
            
        # 순수 숫자, 단위(ml, g), 기호 등으로만 이루어진 바코드/용량 쓰레기값 필터링
        if re.match(r'^[0-9\s\.\-\(\)%mlg]+$', token):
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
        print(f"[오류] 이미지 저장 실패: {e}")
        return None


def detect_crop_ocr_pipeline(
    img_input,
    confidence=30,
    overlap=30,
    padding=10,
    blur_kernel=(3, 3),
    block_size=31,
    c=3,
    scale=4.0,
    save_outputs=True
):
    result_data = {
        "image_path": str(img_input)[:60] + "..." if not os.path.exists(str(img_input)) else img_input,
        "detection_success": False,
        "bbox": None,
        "prediction_confidence": None,
        "cropped_path": None,
        "preprocessed_path": None,
        "original_ocr": {"raw_text": "", "clean_text": "", "ingredient_candidates": []},
        "processed_ocr": {"raw_text": "", "clean_text": "", "ingredient_candidates": []},
        "message": ""
    }

    image_b64, img_cv = parse_input_image(img_input)
    if image_b64 is None or img_cv is None:
        result_data["message"] = "입력 이미지 파싱 실패"
        return result_data

    prediction, raw_response = detect_ingredient_label_v2(image_b64, confidence=confidence, overlap=overlap)
    if prediction is None:
        result_data["message"] = "성분표 영역 탐지 실패"
        return result_data

    cropped_img, bbox = crop_from_prediction_v2(img_cv, prediction, padding=padding)
    if cropped_img is None:
        result_data["message"] = "성분표 이미지 크롭 실패"
        return result_data

    result_data["detection_success"] = True
    result_data["bbox"] = bbox
    result_data["prediction_confidence"] = prediction.get("confidence", None)

    base_name = "web_uploaded" if not isinstance(img_input, str) or not os.path.exists(img_input) else os.path.splitext(os.path.basename(img_input))[0]
    cropped_path = f"{base_name}_cropped_label.jpg"
    preprocessed_path = f"{base_name}_preprocessed_label.jpg"
    json_path = f"{base_name}_ocr_result.json"

    original_text_list = run_easyocr(cropped_img)
    original_raw, original_clean, original_tokens = clean_ocr_result(original_text_list)
    result_data["original_ocr"]["raw_text"] = original_raw
    result_data["original_ocr"]["clean_text"] = original_clean
    result_data["original_ocr"]["ingredient_candidates"] = original_tokens

    processed_img = preprocess_label_image(cropped_img, blur_kernel=blur_kernel, block_size=block_size, c=c, scale=scale)
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
            print(f"[오류] JSON 저장 실패: {e}")

    result_data["message"] = "성공"
    return result_data
