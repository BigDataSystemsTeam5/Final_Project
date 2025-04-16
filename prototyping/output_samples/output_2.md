# H1B Visa Approval Prediction System

This project implements a machine learning pipeline to predict H1B visa approval outcomes based on historical application data from 2011-2016. The system includes both a Jupyter notebook for model development and a Streamlit web application for interactive predictions.

## Table of Contents

- [Security](#security)
- [Background](#background)
- [Repository Structure](#repository-structure)
- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Contributing](#contributing)
- [License](#license)

## Security

### Data Privacy Considerations
- The application uses historical H1B visa data which may contain sensitive employer and applicant information
- All personally identifiable information has been removed from the training dataset
- The web application does not store any user input data after making predictions
- For production deployment, consider implementing:
  - User authentication
  - Input validation
  - HTTPS encryption
  - Rate limiting

## Background

### Problem Statement
The H1B visa process is complex and unpredictable, with approval rates varying significantly based on factors like employer, job title, and location. This project aims to:
- Analyze historical H1B visa application data (2011-2016)
- Identify key factors influencing approval decisions
- Build predictive models to estimate approval probability
- Provide an interactive tool for applicants and employers to assess likely outcomes

### Data Source
The system uses publicly available H1B visa application data from the US Department of Labor containing:
- 3,002,458 initial records
- 11 features including case status, employer info, job details, and location data
- Applications from 2011-2016

### Technical Approach
The solution implements:
- Comprehensive data cleaning and feature engineering
- Advanced categorical feature handling
- Class imbalance correction using SMOTE
- Multiple machine learning models (XGBoost, Random Forest, Decision Tree, KNN)
- Model evaluation with comprehensive metrics
- Web application deployment via Streamlit

## Repository Structure

```
pratikkanade-ml_project_h1b_visa_approval_predictions/
├── README.md                   # Project documentation
├── Notebook.ipynb              # Jupyter notebook with complete ML pipeline
├── visapred.py                 # Streamlit web application
├── h1b_prediction_model_rf2.pk # Pre-trained Random Forest model
├── step1_tab.csv               # Processed data for web app dropdowns
└── background2.jpg             # Background image for web app
```

Key files:
- `Notebook.ipynb`: Contains the complete data science workflow from data loading to model evaluation
- `visapred.py`: Implements the interactive web application for making predictions
- Model files: Serialized trained models for prediction

## Install

### Prerequisites
- Python 3.7+
- pip package manager

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions.git
   cd ML_project_h1b_visa_approval_predictions
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

   If requirements.txt is not available, install these packages:
   ```bash
   pip install numpy pandas scikit-learn xgboost imbalanced-learn streamlit pickle-mixin
   ```

4. Download the data file `h1b_2011_2016.csv` (not included in repository) and place it in the project directory

## Usage

### Running the Jupyter Notebook
1. Start Jupyter:
   ```bash
   jupyter notebook
   ```
2. Open `Notebook.ipynb`
3. Run cells sequentially to:
   - Load and preprocess data
   - Train machine learning models
   - Evaluate model performance
   - Save trained models

### Running the Web Application
1. Start the Streamlit app:
   ```bash
   streamlit run visapred.py
   ```
2. The application will open in your default browser
3. Fill in the form fields:
   - Select company name from dropdown
   - Choose SOC (Standard Occupational Classification) name
   - Enter job title
   - Input salary amount
   - Select state and city
4. Click "Predict" to see the approval probability

### Example Prediction
Input:
- Company: INFOSYS LIMITED
- SOC: COMPUTER SYSTEMS ANALYSTS
- Job Title: TECHNOLOGY LEAD
- Salary: $120,000
- State: TEXAS
- City: DALLAS

Output:
"Visa application has 72.45% probability of being APPROVED"

## API

### Prediction Function
The core prediction functionality can be integrated into other systems through the following functions in `visapred.py`:

```python
def predict_note_authentication(company_name, soc_name, job_title, salary, city, state):
    """
    Returns binary prediction (0 for denial, 1 for approval)
    
    Parameters:
    - company_name: Encoded employer name index
    - soc_name: Encoded SOC name index
    - job_title: Encoded job title index
    - salary: Prevailing wage amount
    - city: Encoded city index
    - state: Encoded state index
    
    Returns: 0 or 1
    """
    # Implementation details...

def predict_probability(company_name, soc_name, job_title, salary, city, state):
    """
    Returns probability distribution for both classes
    
    Parameters: Same as above
    Returns: Array of probabilities [denial_prob, approval_prob]
    """
    # Implementation details...
```

### Data Requirements
To use the API:
1. Input values must be converted to the encoded indices used during training
2. Reference the dictionaries in `visapred.py` for proper encoding:
   - `employer_dict`
   - `soc_dict`
   - `jobtitle_dict`
   - `state_dict`
   - `city_dict`

## Contributing

We welcome contributions to improve this project:

1. **Bug Reports**: Open an issue describing the problem with reproduction steps
2. **Feature Requests**: Suggest enhancements via issues
3. **Code Contributions**:
   - Fork the repository
   - Create a feature branch
   - Submit a pull request with:
     - Clear description of changes
     - Updated tests if applicable
     - Documentation updates

### Areas for Improvement
- Additional feature engineering
- Hyperparameter optimization
- Enhanced web interface
- Better handling of new/unseen categories
- Temporal validation across years

## License

MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)