# ChemiCheck: OCR-Based Risk Information Service for Consumer Chemical Products

ChemiCheck is an OCR-based web service that analyzes product label images, extracts ingredient information, and provides user-friendly risk information for consumer chemical products. The service is designed to help users understand complex chemical ingredient labels by converting them into product-level risk grades, ingredient-level risk results, descriptions, and safety precautions.

The system consists of a FastAPI backend and a React + Vite frontend. The backend performs OCR processing, ingredient normalization, risk analysis, and risk explanation generation. The frontend provides an interface for image upload and displays the final risk analysis results in a readable format.

## Project Overview

Consumer chemical product labels often contain many ingredients that are difficult for general users to interpret. ChemiCheck addresses this problem by automatically extracting ingredients from product labels and matching them with a risk database.

The main workflow is as follows:

1. The user uploads a product label image.
2. The OCR module extracts text from the label image.
3. The ingredient normalization module converts OCR results into standard ingredient names.
4. The risk analysis module matches ingredients with the risk database.
5. The risk explanation module generates user-friendly descriptions and warnings.
6. The frontend displays the overall product risk level and ingredient-level safety information.

## Main Features

- Product label image upload
- OCR-based ingredient text extraction
- Ingredient name normalization using an alias database
- Ingredient-level risk classification
- Product-level final risk grade calculation
- User-friendly risk descriptions and warnings
- Separate display of unregistered or uncertain ingredients
- Accessibility-oriented large text mode
- FastAPI backend and React frontend integration

## Repository Structure

```text
OSS-Project/
  main.py                         FastAPI application entry point
  ocr_processor.py                OCR processing and image preprocessing module
  ingredient_normalizer.py        Ingredient normalization module
  risk_analyzer.py                Ingredient and product risk analysis module
  risk_explanation.py             Risk explanation and warning generation module
  ingredient_alias.csv            Ingredient alias database
  ingredient_risk.csv             Ingredient risk database
  requirements.txt                Python backend dependencies
  README.md                       Project documentation
  LICENSE                         MIT License
  chemicheck-frontend/            React + Vite frontend application
    src/
      components/                 React UI components
      lib/                        Frontend data processing logic
      data/                       Frontend sample/catalog data
      App.jsx                     Main frontend application
      App.css                     UI styles
```

## System Architecture

```text
Label Image
   ↓
OCR Processing
   ↓
Ingredient Candidate Extraction
   ↓
Ingredient Name Normalization
   ↓
Risk Database Matching
   ↓
Risk Explanation Generation
   ↓
Frontend Result Display
```

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pandas
- OpenCV
- EasyOCR
- RapidFuzz

### Frontend

- React
- Vite
- JavaScript
- CSS

### Data

- CSV-based ingredient alias database
- CSV-based ingredient risk database

## Getting Started

### Prerequisites

Before running this project, install the following tools:

- Python 3.10 or later recommended
- Node.js 18 or later recommended
- npm
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd OSS-Project
```

If the project folder has already been downloaded, move directly into the project directory:

```bash
cd OSS-Project
```

### 2. Backend Setup

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

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

Install backend dependencies:

```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

Move to the frontend directory:

```bash
cd chemicheck-frontend
```

Install frontend dependencies:

```bash
npm install
```

## Running the Service

ChemiCheck requires both the backend server and the frontend development server to run.

### 1. Run the Backend Server

Open a terminal in the `OSS-Project` directory and run:

```bash
uvicorn main:app --reload
```

The backend server will usually run at:

```text
http://127.0.0.1:8000
```

The FastAPI documentation page is available at:

```text
http://127.0.0.1:8000/docs
```

### 2. Run the Frontend Server

Open another terminal and move to the frontend directory:

```bash
cd chemicheck-frontend
```

Run the development server:

```bash
npm run dev
```

The frontend will usually run at:

```text
http://localhost:5173
```

## Usage

### Web Service Usage

1. Run the backend server.
2. Run the frontend development server.
3. Open `http://localhost:5173` in a browser.
4. Upload a product label image.
5. Wait for OCR and risk analysis to complete.
6. Check the overall product risk level.
7. Review ingredient-level risk information and warnings.
8. Check the additional confirmation list for unregistered or uncertain ingredients.

## API Usage Examples

### Analyze Ingredients Directly

If ingredient names are already available, use the `/api/analyze-ingredients` endpoint.

Request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze-ingredients" \
  -H "Content-Type: application/json" \
  -d "{\"ingredients\": [\"정제수\", \"에탄올\", \"향료\"]}"
```

Response example:

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

The actual response depends on the data registered in `ingredient_alias.csv` and `ingredient_risk.csv`.

### Analyze a Product Label Image

Use the `/api/analyze-label` endpoint to analyze a label image.

Request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze-label" \
  -F "image=@sample_label.jpg"
```

The response includes OCR results, normalized ingredient results, risk analysis results, and risk explanation results.

## Example Results

### Successful Analysis Example

When a clear label image is uploaded, the service performs the following process:

1. OCR extracts ingredient text from the label image.
2. Extracted ingredient names are normalized using the alias database.
3. Registered ingredients are matched with the risk database.
4. The product-level risk grade is displayed at the top of the result screen.
5. Ingredient-level cards show risk grades, recognized names, warnings, and descriptions.

Example output:

```text
Overall Risk Level: Medium

Ingredient Results
- Ethanol
  - Risk Level: Medium
  - Recognized Name: 에탄올
  - Warning: Use in a well-ventilated area and avoid direct contact with eyes or skin.

- Fragrance
  - Risk Level: Medium
  - Recognized Name: 향료
  - Warning: Users sensitive to fragrance ingredients should check the ingredient list before use.
```

### Unregistered Ingredient Example

If an ingredient is not registered in the database or the OCR result is uncertain, the service does not assign an arbitrary risk level. Instead, it displays the ingredient in a separate confirmation section.

Example output:

```text
Ingredients Requiring Additional Confirmation
These ingredients were not included in risk calculation because they may be OCR errors or unregistered database entries.

Cyclopentasiloxane  Carbomer  Allantoin
```

### Failure or Limitation Example

The service may produce incomplete results in the following cases:

- The label image is blurry.
- The label has strong light reflection or shadows.
- The text is too small or densely arranged.
- The product container is curved and the text is distorted.
- OCR fails to recognize commas, line breaks, or separators.
- The ingredient is not registered in the risk database.

In these cases, some ingredients may be missed or incorrectly grouped. The service handles uncertain ingredients by separating them into the additional confirmation list.

## Module Description

### OCR Processing Module

`ocr_processor.py` detects and processes the label image area. It uses OpenCV for image preprocessing and EasyOCR for text extraction. The OCR result is cleaned and converted into ingredient candidates.

### Ingredient Normalization Module

`ingredient_normalizer.py` converts OCR-extracted ingredient names into standard ingredient names. It uses exact matching and similarity-based matching with the ingredient alias database.

### Risk Analysis Module

`risk_analyzer.py` matches normalized ingredients with the risk database. It calculates ingredient-level risk scores and determines the final product risk level.

### Risk Explanation Module

`risk_explanation.py` generates user-friendly risk descriptions and warnings based on the risk analysis results. It uses `description`, `warning`, `basis`, and `risk_level` fields from the risk database. If detailed information is missing, the module generates fallback descriptions and default warnings based on the risk level.

### Frontend UI

The React frontend displays the analysis results in a user-friendly interface. The overall product risk level is shown in the summary area, while matched ingredients are shown as individual cards. Unregistered or uncertain ingredients are displayed separately as items requiring additional confirmation. The UI also includes a large text mode to improve readability and accessibility.

## Dataset and Database

### Ingredient Alias Database

`ingredient_alias.csv` stores standard ingredient names and their aliases. This database helps correct different ingredient expressions and OCR recognition variations.

Example:

```text
category,standard_name,aliases
Solvent,Ethanol,Ethyl alcohol
Acid,Citric acid,Citric acid
```

### Ingredient Risk Database

`ingredient_risk.csv` stores risk information for each ingredient.

Main fields:

- `standard_name`: Standard ingredient name
- `category`: Ingredient category
- `risk_level`: Risk grade
- `basis`: Reason for risk classification
- `warning`: User safety warning
- `description`: User-friendly ingredient description

This database is used by both the risk analysis module and the risk explanation module.

## Testing and Verification

### Backend Syntax Check

```bash
python -m py_compile main.py
```

### Frontend Lint Check

```bash
cd chemicheck-frontend
npm run lint
```

### Frontend Build Check

```bash
npm run build
```

## Known Limitations

- OCR accuracy depends heavily on image quality.
- Blurry, tilted, reflective, or shadowed label images may reduce recognition accuracy.
- Small and dense ingredient text may not be fully extracted.
- If OCR misses commas or line breaks, ingredient separation may be inaccurate.
- The risk database does not include every possible ingredient.
- Unregistered ingredients cannot be assigned reliable risk levels.
- Current risk analysis does not fully reflect ingredient concentration, exposure time, usage amount, or user environment.
- Interactions between multiple ingredients are only limitedly considered.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

The MIT License allows use, copying, modification, merging, publishing, distribution, sublicensing, and selling copies of the software, provided that the copyright notice and license notice are included.

## Contributing

Contributions are welcome. To contribute to this project, follow the steps below.

1. Open an issue describing the bug, improvement, or new feature.
2. Create a new branch.

```bash
git checkout -b feature/your-feature-name
```

3. Make changes to the code, data, or documentation.
4. Run the appropriate checks.

```bash
python -m py_compile main.py
cd chemicheck-frontend
npm run lint
```

5. Commit your changes.

```bash
git add .
git commit -m "Describe your change"
```

6. Open a Pull Request with a clear description of the changes and test results.

## Contribution Guidelines

- When updating the alias database, check both the standard ingredient name and possible alternative expressions.
- When updating the risk database, provide clear evidence for the risk level, description, and warning.
- When modifying OCR post-processing logic, test both clear and low-quality label images.
- When modifying the UI, ensure that risk information is not exaggerated or hidden from users.

## Acknowledgement

This project uses open-source libraries including FastAPI, EasyOCR, OpenCV, Pandas, RapidFuzz, React, and Vite. The object detection process for ingredient label area recognition was supported by a Roboflow-based workflow.
