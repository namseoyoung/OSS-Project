# ChemiCheck Frontend

생활화학제품 라벨 이미지와 OCR 추출 텍스트를 바탕으로 성분을 정규화하고, 위험도와 쉬운 사용 지침을 보여주는 React + Vite 웹서비스입니다.

## 주요 기능

- 라벨 이미지 업로드 및 OCR 텍스트 직접 입력 화면
- 생활화학제품 제품군 선택
- 성분명 별칭 기반 정규화
- Low, Medium, High 위험도 분류
- 성분별 우려 항목, 안전 사용법, 민감 계층 안내
- 고령층과 정보 접근성이 낮은 사용자를 위한 큰 글씨 모드

## 폴더 구조

```text
src/
  assets/                 화면에 사용하는 이미지 리소스
  components/             화면 단위 React 컴포넌트
  data/                   성분 카탈로그와 예시 라벨 데이터
  lib/                    라벨 분석 및 요약 생성 로직
  App.jsx                 전체 화면 조합
  App.css                 서비스 UI 스타일
  main.jsx                React 진입점
```

## 실행 방법

```bash
npm install
npm run dev
```

개발 서버가 실행되면 터미널에 표시되는 주소를 브라우저에서 열면 됩니다. 일반적으로 `http://localhost:5173/` 입니다.

## 배포용 빌드

```bash
npm run build
npm run preview
```
