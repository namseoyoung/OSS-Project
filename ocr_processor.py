import cv2
import easyocr
import re

def get_clean_label_image(img_path):
    """
    OpenCV 이미지 전처리 파이프라인 함수
    - Grayscale 변환, Gaussian Blur 노이즈 제거, Adaptive Thresholding 이진화, Resize 확대 적용
    """
    img = cv2.imread(img_path)
    if img is None:
        print("Error: 전처리 대상 이미지를 로드할 수 없습니다.")
        return None
        
    # 1. Grayscale 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Gaussian Blur 알고리즘 적용 (카메라 고주파 노이즈 제거)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # 3. Adaptive Thresholding 적용 (크롭 이미지 전용 임계치 최적화)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 7, 2)
    
    # 4. 이미지 확대 (저해상도 텍스트 인식률 향상)
    upscaled = cv2.resize(thresh, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    return upscaled


def extract_text_from_label(processed_image):
    """
    OCR 엔진 연동 및 텍스트 데이터 정제/배열 변환 함수
    - EasyOCR 글자 추출, 정규표현식 특수문자 제거, 쉼표 기준 데이터 파싱
    """
    reader = easyocr.Reader(['ko', 'en'])
    
    # EasyOCR을 통한 텍스트 추출 (detail=0 설정으로 순수 문자열 배열 반환)
    text_list = reader.readtext(processed_image, detail=0)
    raw_string = " ".join(text_list)
    
    # 정규표현식 필터 적용 (한글, 영어, 숫자, 공백, 쉼표를 제외한 특수문자 제거)
    clean_string = re.sub(r'[^가-힣a-zA-Z0-9\s,]', '', raw_string)
    
    # 연속된 공백을 단일 공백으로 치환
    clean_string = re.sub(r'\s+', ' ', clean_string).strip()
    
    # 쉼표 및 줄바꿈 기준으로 토큰화
    ingredients_array = [target.strip() for target in clean_string.split(',') if target.strip()]
    
    return raw_string, clean_string, ingredients_array


# ==========================================
# 모듈 테스트 및 콘솔 출력 실행 영역
# ==========================================
if __name__ == "__main__":
    # 입력 이미지 경로 설정 (라벨 크롭 이미지)
    my_image = "cropped_label.jpg" 
    
    cleaned_img = get_clean_label_image(my_image)
    
    if cleaned_img is not None:
        raw_str, clean_str, final_array = extract_text_from_label(cleaned_img)
        
        print("\n=========================================================")
        print("CHEMICAL LABEL RECOGNITION MODULE INTEGRATION REPORT")
        print("=========================================================")
        
        print("\n[1] Filtered OCR String (Regex Cleansed)")
        print(clean_str[:300] + "...")
        
        print("\n---------------------------------------------------------")
        print("[2] Final Ingredients Parsed Array (Output)")
        print(f"Total Detected Ingredients: {len(final_array)}\n")
        for idx, ingredient in enumerate(final_array[:20], 1):
            print(f"  [{idx}] {ingredient}")
        if len(final_array) > 20:
            print(f"  ... and {len(final_array) - 20} more ingredients.")
            
        print("=========================================================")
