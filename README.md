# ChemiCheck

ChemiCheck는 생활화학제품 라벨 이미지를 분석하여 제품에 포함된 성분을 추출하고, 성분별 위험도와 주의사항을 사용자에게 제공하는 OCR 기반 웹 서비스입니다. 사용자는 제품 라벨 이미지를 업로드하기만 하면 OCR, 성분 정규화, 위험도 분석, 위험도 설명 생성 과정을 거쳐 제품의 종합 위험도와 성분별 안전 정보를 확인할 수 있습니다.

이 프로젝트는 복잡한 화학 성분표를 일반 사용자도 이해하기 쉬운 위험도 등급과 생활 안전 안내로 변환하는 것을 목표로 합니다.

## 주요 기능

- 제품 라벨 이미지 업로드 기능을 제공함.
- OCR을 통해 라벨 이미지에서 성분 영역과 텍스트를 추출함.
- 성분명 alias 사전을 활용하여 OCR 결과를 표준 성분명으로 정규화함.
- 위험도 데이터베이스를 기반으로 성분별 위험도를 분석함.
- 제품 전체의 종합 위험도 등급을 산출함.
- 성분별 설명, 주의사항, 위험도 등급을 사용자 화면에 표시함.
- DB에 등록되지 않았거나 OCR 인식이 불확실한 성분은 추가 확인 필요 성분으로 분리하여 표시함.
- React 기반 프론트엔드와 FastAPI 기반 백엔드를 연동하여 동작함.

## 프로젝트 구조

```text
OSS-Project/
  main.py                         FastAPI 서버 진입점
  ocr_processor.py                라벨 이미지 OCR 및 전처리 모듈
  ingredient_normalizer.py        성분명 alias 기반 정규화 모듈
  risk_analyzer.py                성분별 위험도 및 제품 위험도 분석 모듈
  risk_explanation.py             위험도 설명 및 주의사항 생성 모듈
  ingredient_alias.csv            성분명 alias 데이터베이스
  ingredient_risk.csv             성분 위험도, 설명, 주의사항 데이터베이스
  requirements.txt                백엔드 Python 의존성 목록
  chemicheck-frontend/            React + Vite 프론트엔드
```

## 기술 스택

### Backend

- Python
- FastAPI
- Pandas
- OpenCV
- EasyOCR
- RapidFuzz
- Uvicorn

### Frontend

- React
- Vite
- JavaScript
- CSS

### Data

- CSV 기반 성분 alias 데이터베이스
- CSV 기반 위험도 데이터베이스

## 설정 및 설치 방법

### 1. 프로젝트 다운로드

```bash
git clone <repository-url>
cd OSS-Project
```

이미 프로젝트 폴더를 받은 경우에는 `OSS-Project` 폴더로 이동합니다.

```bash
cd OSS-Project
```

### 2. 백엔드 실행 환경 설정

Python 가상환경을 생성합니다.

```bash
python -m venv .venv
```

가상환경을 활성화합니다.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.\.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source .venv/bin/activate
```

필요한 Python 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

### 3. 프론트엔드 실행 환경 설정

프론트엔드 폴더로 이동합니다.

```bash
cd chemicheck-frontend
```

Node.js 패키지를 설치합니다.

```bash
npm install
```

## 실행 방법

ChemiCheck는 백엔드 서버와 프론트엔드 개발 서버를 각각 실행해야 합니다.

### 1. 백엔드 서버 실행

`OSS-Project` 폴더에서 다음 명령어를 실행합니다.

```bash
uvicorn main:app --reload
```

정상적으로 실행되면 일반적으로 다음 주소에서 API 서버가 실행됩니다.

```text
http://127.0.0.1:8000
```

API 문서는 다음 주소에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

### 2. 프론트엔드 서버 실행

새 터미널을 열고 `chemicheck-frontend` 폴더에서 다음 명령어를 실행합니다.

```bash
npm run dev
```

정상적으로 실행되면 일반적으로 다음 주소에서 웹 화면을 확인할 수 있습니다.

```text
http://localhost:5173
```

## 사용법

### 1. 웹 화면에서 사용하는 방법

1. 백엔드 서버를 실행함.
2. 프론트엔드 서버를 실행함.
3. 브라우저에서 `http://localhost:5173`에 접속함.
4. 제품 라벨 이미지를 업로드함.
5. OCR 분석이 완료될 때까지 기다림.
6. 제품 종합 위험도와 성분별 분석 결과를 확인함.
7. DB에 등록되지 않은 성분은 추가 확인이 필요한 성분 목록에서 확인함.

### 2. API로 성분 리스트를 직접 분석하는 방법

이미 추출된 성분 리스트가 있는 경우 `/api/analyze-ingredients` API를 사용할 수 있습니다.

요청 예시:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze-ingredients" \
  -H "Content-Type: application/json" \
  -d "{\"ingredients\": [\"정제수\", \"에탄올\", \"향료\"]}"
```

응답 예시:

```json
{
  "normalized_results": [],
  "risk_analysis": {
    "final_score": 3.0,
    "final_risk_level": "Low",
    "ingredient_count": 3,
    "matched_risk_count": 1,
    "ingredient_results": []
  },
  "risk_explanation": {
    "final_risk_level": "Low",
    "final_risk_label": "낮음",
    "ingredient_explanations": []
  }
}
```

실제 응답 내용은 `ingredient_alias.csv`와 `ingredient_risk.csv`에 등록된 성분 정보에 따라 달라질 수 있습니다.

### 3. 이미지 라벨 분석 API 사용 방법

제품 라벨 이미지는 `/api/analyze-label` API로 분석할 수 있습니다.

요청 예시:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze-label" \
  -F "image=@sample_label.jpg"
```

응답에는 OCR 결과, 정규화 결과, 위험도 분석 결과, 위험도 설명 결과가 포함됩니다.

## 실행 결과 예시

### 정상 분석 예시

선명한 제품 라벨 이미지를 업로드하면 다음과 같은 흐름으로 결과가 출력됩니다.

1. OCR이 라벨 이미지에서 성분 텍스트를 추출함.
2. 추출된 성분명이 alias 사전을 통해 표준 성분명으로 변환됨.
3. 위험도 DB와 매칭된 성분에 대해 위험도 등급이 산출됨.
4. 제품 전체의 종합 위험도가 화면 상단에 표시됨.
5. 성분별 카드에 위험도 등급, 인식 표기, 주의사항, 설명 문구가 표시됨.

화면 출력 예시:

```text
종합 위험도: 보통

성분별 결과
- 에탄올
  - 위험도: 보통
  - 인식 표기: 에탄올
  - 주의사항: 사용량을 지키고 환기하며, 피부나 눈에 직접 닿지 않도록 주의하세요.

- 향료
  - 위험도: 보통
  - 인식 표기: 향료
  - 주의사항: 민감한 사용자는 사용 전 성분을 확인하세요.
```

### 추가 확인 필요 성분 예시

OCR 결과가 부정확하거나 위험도 DB에 등록되지 않은 성분은 임의로 위험도를 판단하지 않고 별도 목록으로 표시합니다.

화면 출력 예시:

```text
추가 확인이 필요한 성분
OCR 인식 결과 또는 DB 미등록 성분으로, 위험도 산정에는 포함하지 않았습니다.

사이클로펜타실록세인  카보머  알란토인
```

### 잘 되지 않는 경우 예시

다음과 같은 경우에는 OCR 인식률이 낮아질 수 있습니다.

- 라벨 이미지가 흐릿한 경우
- 빛 반사나 그림자가 있는 경우
- 글자가 매우 작거나 여러 줄로 촘촘히 배치된 경우
- 제품 용기가 휘어져 글자가 왜곡된 경우
- 쉼표나 줄바꿈이 OCR에서 누락된 경우

이 경우 일부 성분이 누락되거나 여러 성분이 하나로 붙어서 인식될 수 있습니다. 시스템은 이러한 성분을 추가 확인 필요 성분으로 분리하여 표시합니다.

## 주요 모듈 설명

### OCR 처리 모듈

`ocr_processor.py`는 제품 라벨 이미지에서 성분 영역을 탐지하고 OCR을 수행합니다. OpenCV를 이용해 이미지를 전처리하고, EasyOCR을 통해 텍스트를 추출합니다.

### 성분 정규화 모듈

`ingredient_normalizer.py`는 OCR로 추출된 성분명을 표준 성분명으로 변환합니다. 정확히 일치하는 alias를 우선 확인하고, 필요한 경우 유사도 기반 매칭을 수행합니다.

### 위험도 분석 모듈

`risk_analyzer.py`는 정규화된 성분명을 위험도 DB와 비교하여 성분별 위험도 등급을 산출합니다. 성분별 점수를 기반으로 제품 전체의 최종 위험도 등급도 계산합니다.

### 위험도 설명 생성 모듈

`risk_explanation.py`는 위험도 분석 결과를 바탕으로 사용자 친화적인 설명과 주의사항을 생성합니다. DB에 저장된 `description`, `warning`, `basis` 정보를 우선 활용하고, 정보가 부족한 경우 위험도 등급에 따른 기본 안내 문구를 제공합니다.

### 프론트엔드 UI

`chemicheck-frontend`는 분석 결과를 사용자가 이해하기 쉬운 화면으로 제공합니다. 종합 위험도는 상단 요약 영역에 표시하고, 성분별 분석 결과는 카드 형태로 표시합니다. 미등록 성분은 큰 카드로 표시하지 않고 하단의 추가 확인 필요 성분 목록으로 정리하여 보여줍니다.

## 데이터베이스 설명

### ingredient_alias.csv

성분명의 다양한 표기, 별칭, OCR 오인식 가능 표현을 표준 성분명과 연결하는 데이터입니다.

예시:

```text
표준 성분명, alias
에탄올, 에칠알코올
구연산, 시트릭애씨드
```

### ingredient_risk.csv

성분별 위험도, 분류 근거, 사용자 설명, 주의사항 정보를 저장하는 데이터입니다.

주요 컬럼:

- `standard_name`: 표준 성분명
- `category`: 성분 카테고리
- `risk_level`: 위험도 등급
- `basis`: 위험도 분류 근거
- `warning`: 사용자 주의사항
- `description`: 사용자 친화적 설명

## 테스트 및 검증

### 백엔드 문법 확인

```bash
python -m py_compile main.py
```

### 프론트엔드 린트 확인

```bash
cd chemicheck-frontend
npm run lint
```

### 프론트엔드 빌드 확인

```bash
npm run build
```

## 기술적 한계

- OCR 인식 성능은 이미지 품질에 영향을 받습니다.
- 흐릿한 라벨, 빛 반사, 그림자, 기울어진 사진에서는 성분 추출 정확도가 낮아질 수 있습니다.
- OCR이 쉼표나 줄바꿈을 인식하지 못하면 성분 단위 분리가 부정확할 수 있습니다.
- 위험도 DB에 등록되지 않은 성분은 위험도 등급과 주의사항을 제공하기 어렵습니다.
- 실제 제품의 성분 함량, 사용량, 노출 시간, 사용 환경은 현재 위험도 산정에 충분히 반영되지 않습니다.
- 여러 성분의 상호작용이나 혼합 위험성은 제한적으로만 고려됩니다.

## 라이선스

이 프로젝트는 학습 및 연구 목적의 오픈소스 프로젝트로 작성되었습니다. 별도의 라이선스 파일이 없는 경우, 코드와 데이터의 사용 범위는 프로젝트 제출 및 수업 평가 목적에 한정됩니다.

외부 공개 또는 재사용을 계획하는 경우에는 MIT License, Apache License 2.0 등 명시적인 오픈소스 라이선스를 추가하는 것을 권장합니다.

## 기여하는 방법

프로젝트 개선에 기여하려면 다음 절차를 따릅니다.

1. 이슈를 등록하여 개선 사항이나 오류를 설명합니다.
2. 새로운 브랜치를 생성합니다.

```bash
git checkout -b feature/your-feature-name
```

3. 기능을 수정하거나 버그를 해결합니다.
4. 백엔드 문법 검사와 프론트엔드 린트를 실행합니다.

```bash
python -m py_compile main.py
cd chemicheck-frontend
npm run lint
```

5. 변경 내용을 커밋합니다.

```bash
git add .
git commit -m "Describe your change"
```

6. Pull Request를 생성하고 변경 목적, 수정 내용, 테스트 결과를 작성합니다.

## 기여 시 권장 사항

- 성분 DB를 수정할 때는 표준 성분명과 alias를 함께 확인합니다.
- 위험도 DB를 수정할 때는 위험도 등급, 설명, 주의사항의 근거를 명확히 작성합니다.
- OCR 후처리 로직을 수정할 때는 선명한 이미지와 흐릿한 이미지 모두에서 테스트합니다.
- UI를 수정할 때는 위험도 정보가 사용자에게 과장되거나 누락되어 보이지 않도록 주의합니다.

## 문의

프로젝트 관련 문의나 개선 사항은 이슈 또는 Pull Request를 통해 남길 수 있습니다.
