# Dataset Information

This document describes the dataset files used in the **ChemiCheck** project.

ChemiCheck is an OCR and AI-based system for analyzing ingredient labels of consumer chemical products and providing risk information in an easy-to-understand way.

## 1. Dataset Overview

The dataset consists of product label images and CSV files used for OCR result recording, ingredient name normalization, and ingredient risk classification.

The dataset is used for the following purposes:

* Collecting product label images of consumer chemical products
* Extracting ingredient text from label images using OCR
* Comparing OCR results before and after image preprocessing
* Normalizing ingredient names using an alias dictionary
* Classifying ingredient risk levels by product category
* Providing user-friendly explanations and caution messages

## 2. Image Dataset

Product label images are stored separately in Google Drive due to GitHub file size limitations.

### Current Status

At the current stage, only original product label images have been collected.

Cropped ingredient images and preprocessed images will be added later for OCR accuracy improvement.

### Google Drive Storage

```text
Google Drive link: https://drive.google.com/drive/folders/1sshBGB2QMv2jRkR-0KTU7LpQv0LEgDya?usp=drive_link
```

### Current Folder Structure

```text
label_image_dataset/
└── original_images/
```

### Planned Folder Structure

```text
label_image_dataset/
├── original_images/
├── cropped_ingredient_images/
└── preprocessed_images/
```

### Folder Description

| Folder Name               | Description                                                                             |
| ------------------------- | --------------------------------------------------------------------------------------- |
| original_images           | Original product label images taken by the team                                         |
| cropped_ingredient_images | Cropped images containing only the ingredient label area                                |
| preprocessed_images       | Images processed for OCR improvement, such as grayscale, resized, or thresholded images |

## 3. Image File Naming Rule

Image files are named using the following format:

```text
ProductID_ProductCategory_ProductName_ImageType_ViewNumber.jpg
```

### Example

```text
P001_laundry_detergent_Tech_original_front_01.jpg
P002_air_freshener_original_front_01.jpg
P003_bathroom_cleaner_original_front_01.jpg
```

### Naming Elements

| Element         | Description                                                                        |
| --------------- | ---------------------------------------------------------------------------------- |
| ProductID       | Unique product ID, such as P001, P002, P003                                        |
| ProductCategory | Product category written in English, such as laundry_detergent or bathroom_cleaner |
| ProductName     | Short product name or brand name                                                   |
| ImageType       | Image type, such as original, crop, or preprocessed                                |
| ViewNumber      | Image view or sequence number, such as front_01 or angle45_01                      |

## 4. CSV Files

The following CSV files are managed in the GitHub repository.

```text
data/
├── dataset_info.md
├── image_labeling.csv
├── ingredient_alias.csv
└── risk_classification_db.csv
```

## 5. image_labeling.csv

This file records product label image information and OCR results.

### Purpose

The purpose of this file is to compare OCR results before and after preprocessing and to record the actual ingredient names written on the product label.

### Columns

| Column Name                     | Description                              |
| ------------------------------- | ---------------------------------------- |
| image_file_name                 | Product label image file name            |
| actual_ingredients              | Manually checked actual ingredient names |
| ocr_result_before_preprocessing | OCR result before image preprocessing    |
| ocr_result_after_preprocessing  | OCR result after image preprocessing     |

### Example

```csv
image_file_name,actual_ingredients,ocr_result_before_preprocessing,ocr_result_after_preprocessing
P001_laundry_detergent_original_front_01.jpg,"citric acid, limonene","citnc acid, limonen","citric acid, limonene"
```

## 6. ingredient_alias.csv

This file manages ingredient name normalization.

### Purpose

The purpose of this file is to match synonyms, alternative names, spelling variations, and possible OCR errors to a single standard ingredient name.

For example, the same ingredient may appear in different forms depending on the product label or OCR result. This file helps normalize those names.

### Columns

| Column Name              | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| standard_ingredient_name | Standard ingredient name used in the system                   |
| alias_name               | Synonym, alternative notation, or possible OCR misrecognition |

### Example

```csv
standard_ingredient_name,alias_name
citric acid,citric acid
citric acid,구연산
limonene,리모넨
limonene,리모넌
```

## 7. risk_classification_db.csv

This file contains the ingredient risk classification database.

### Purpose

The purpose of this file is to classify each standard ingredient by product category and provide risk information in a user-friendly way.

This file is used to generate the final risk analysis result shown to users.

### Columns

| Column Name               | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| standard_ingredient_name  | Standard ingredient name                                     |
| product_category          | Product category where the ingredient is used                |
| final_risk_level          | Final risk level                                             |
| user_friendly_description | Easy explanation for general users                           |
| user_caution              | Safety caution for users                                     |
| risk_reason               | Reason why the ingredient was classified into the risk level |

### Example

```csv
standard_ingredient_name,product_category,final_risk_level,user_friendly_description,user_caution,risk_reason
citric acid,multi_purpose_cleaner,Low,"Citric acid is commonly used as a cleaning aid and pH adjuster.","Avoid direct contact with eyes.","Generally low risk when used in household cleaning products."
```

## 8. Dataset Workflow

The dataset is used in the following workflow:

```text
Original label image
→ Ingredient area cropping
→ Image preprocessing
→ OCR text extraction
→ Ingredient extraction
→ Ingredient name normalization
→ Risk classification
→ User-friendly explanation
```

## 9. Current Progress

Current dataset progress:

* Original product label images have been collected.
* CSV files for OCR labeling, ingredient aliases, and risk classification have been created.
* Cropped ingredient images will be added later.
* Preprocessed images will be generated after applying OpenCV-based preprocessing.
* OCR results will be recorded in `image_labeling.csv`.

## 10. Notes

The original image files are not uploaded directly to GitHub because of file size limitations.

Instead, the actual image dataset is stored in Google Drive, and GitHub is used to manage dataset documentation and CSV files.

This structure allows the team to manage large image files separately while tracking changes in CSV files through GitHub.
