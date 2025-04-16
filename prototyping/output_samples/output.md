# H1B Visa Approval Prediction Project

This project implements a machine learning system to predict the approval probability of H1B visa applications in the United States. The system analyzes various factors including employer details, job classification, geographic location, and salary information to provide insights into visa approval patterns.

## Table of Contents

- [Background](#background)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Model Details](#model-details)
- [Data Processing](#data-processing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Background

The H1B visa program allows US employers to temporarily employ foreign workers in specialty occupations. This project addresses the challenge of predicting visa approval outcomes by analyzing historical application data from 2011-2016 (3,002,458 applications). The system helps:

- Visa applicants understand their approval likelihood
- Employers assess petition success rates
- Policymakers identify patterns in approval decisions

The project demonstrates that visa approvals are not random but follow predictable patterns based on specific features like employer reputation, job classification, and geographic location.

## Repository Structure

```
pratikkanade-ml_project_h1b_visa_approval_predictions/
├── README.md               # Project documentation
├── Notebook.ipynb          # Jupyter notebook with EDA and model development
└── visapred.py             # Streamlit web application for predictions
```

Key files:
- `Notebook.ipynb`: Contains the complete machine learning workflow including data cleaning, feature engineering, model training, and evaluation
- `visapred.py`: Implements the production web interface using Streamlit

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions.git
cd ML_project_h1b_visa_approval_predictions
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

Required dependencies include:
- Python 3.7+
- pandas
- numpy
- scikit-learn
- xgboost
- imbalanced-learn
- streamlit
- pickle

## Usage

### Running the Web Application

1. Ensure all dependencies are installed
2. Download the model file (`h1b_prediction_model_rf2.pk`) and data file (`step1_tab.csv`)
3. Run the Streamlit app:
```bash
streamlit run visapred.py
```

The web interface provides:
- Dropdown selectors for employer, job classification, and location
- Numeric input for prevailing wage
- Dynamic city selection filtered by state
- Prediction button that displays approval probability

### Using the Model Directly

Load the pre-trained model in Python:
```python
import pickle

with open('h1b_prediction_model_rf2.pk', 'rb') as f:
    model = pickle.load(f)

# Sample prediction
prediction = model.predict([[65, 48, 122, 120000, 20, 43]])  # employer, soc, job, wage, city, state codes
```

## Model Details

### Algorithms Evaluated
1. **XGBoost** (Best performer)
   - Accuracy: 91.59%
   - ROC AUC: 0.83
   - Recall: 1.00
   - F1-score: 0.96

2. **Random Forest**
   - Accuracy: 90.08%
   - ROC AUC: 0.79
   - Selected for deployment due to balance of performance and interpretability

3. **Decision Tree**
   - Accuracy: 88.42%

4. **K-Nearest Neighbors**
   - Accuracy: 90.68%

### Feature Engineering
Key preprocessing steps:
- Target variable: Binary `ACCEPT_REJECT` (1 for CERTIFIED, 0 otherwise)
- Categorical feature encoding:
  - Employer name, SOC name, job title converted to category codes
  - Reduced cardinality by grouping infrequent categories
- Selected features:
  - EMPLOYER_NAME
  - SOC_NAME
  - JOB_TITLE
  - PREVAILING_WAGE
  - STATE
  - CITY

### Class Imbalance Handling
Original class distribution:
- Approved: 2,512,114 (87.8%)
- Rejected: 365,651 (12.2%)

Used SMOTE oversampling to balance classes during training.

## Data Processing

### Original Dataset
- 3,002,458 H1B applications (2011-2016)
- 11 initial features including:
  - CASE_STATUS (target)
  - EMPLOYER_NAME
  - SOC_NAME
  - JOB_TITLE
  - PREVAILING_WAGE
  - WORKSITE (split into CITY and STATE)

### Cleaning Steps
1. Removed rows with missing values
2. Split WORKSITE into CITY and STATE columns
3. Standardized text formatting (uppercase, punctuation removal)
4. Reduced categorical cardinality:
   - SOC_NAME: Kept categories with >500 occurrences
   - JOB_TITLE: Kept categories with >1000 occurrences
   - EMPLOYER_NAME: Kept categories with >600 occurrences

## Deployment

The application is deployed on AWS EC2 using:
- Streamlit for the web interface
- Nginx as reverse proxy
- Systemd for process management

Key deployment files (not in repo):
- `h1b_prediction_model_rf2.pk`: Serialized model
- `step1_tab.csv`: Processed training data
- `background2.jpg`: Application background image

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Areas for contribution:
- Adding more recent data
- Implementing additional model explanation features
- Improving the UI/UX
- Adding automated testing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)