# H1B Visa Approval Prediction Project

This project provides a comprehensive solution for predicting H1B visa approval outcomes using machine learning. It includes both the model development process (Notebook.ipynb) and a production-ready web application (visapred.py) built with Streamlit.

## Table of Contents

- [Background](#background)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Model Details](#model-details)
- [API](#api)
- [Contributing](#contributing)
- [License](#license)

## Background

The H1B visa program allows US employers to temporarily employ foreign workers in specialty occupations. This project addresses the challenge of predicting whether an H1B visa application will be approved based on key application characteristics. The solution:

- Processes historical H1B application data (2011-2016) with over 3 million records
- Implements a complete machine learning pipeline from data cleaning to model deployment
- Provides both analytical tools (Jupyter notebook) and a user-friendly interface (Streamlit app)

Key challenges addressed:
- Significant class imbalance (87% approval rate)
- High-cardinality categorical features (employers, job titles)
- Geographic patterns in approval rates

## Repository Structure

```
pratikkanade-ml_project_h1b_visa_approval_predictions/
├── README.md                   # Project documentation
├── Notebook.ipynb              # Jupyter notebook with complete ML pipeline
└── visapred.py                 # Streamlit web application for predictions
```

Additional required files (not in repo but needed for execution):
- `h1b_2011_2016.csv` - Original dataset (3M+ records)
- `h1b_prediction_model_rf2.pk` - Serialized trained model
- `step1_tab.csv` - Reference data for categories
- `background2.jpg` - Background image for web app

## Installation

To run this project, you'll need Python 3.7+ and the following dependencies:

```bash
# Clone the repository
git clone https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions.git
cd ML_project_h1b_visa_approval_predictions

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install requirements
pip install numpy pandas scikit-learn xgboost imbalanced-learn streamlit pickle-mixin
```

For Jupyter notebook functionality:
```bash
pip install jupyter notebook
```

## Usage

### Running the Streamlit Web Application

```bash
streamlit run visapred.py
```

The application will launch in your default browser at `http://localhost:8501`.

### Using the Jupyter Notebook

```bash
jupyter notebook
```

Then open `Notebook.ipynb` to explore:
- Data cleaning and preprocessing
- Feature engineering
- Model training and evaluation
- Model serialization

### Making Predictions Programmatically

After training and saving the model, you can load and use it:

```python
import pickle
import numpy as np

# Load the trained model
model = pickle.load(open('h1b_prediction_model_rf2.pk', 'rb'))

# Example prediction
# Format: [EMPLOYER_NAME, SOC_NAME, JOB_TITLE, PREVAILING_WAGE, STATE, CITY]
sample_input = np.array([[65, 48, 122, 120000, 20, 43]])  # Encoded indices

prediction = model.predict(sample_input)
probability = model.predict_proba(sample_input)

print(f"Approval Probability: {probability[0][1]*100:.2f}%")
```

## Model Details

### Performance Metrics

| Model       | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------------|----------|-----------|--------|----------|---------|
| KNN         | 90.68%   | 0.92      | 0.98   | 0.95     | 0.70    |
| Decision Tree | 88.42% | 0.93      | 0.95   | 0.94     | 0.70    |
| Random Forest | 90.08% | 0.92      | 0.97   | 0.95     | 0.79    |
| XGBoost     | 91.59%   | 0.92      | 1.00   | 0.96     | 0.83    |

### Feature Importance

The most important features for prediction are:
1. Employer name
2. Job title
3. Prevailing wage
4. Geographic location (state/city)
5. Standard Occupational Classification (SOC) name

## API

The Streamlit application provides a simple API-like interface through its web form. For programmatic access, you can wrap the prediction functionality in a Flask/FastAPI service:

```python
from fastapi import FastAPI
import pickle
import numpy as np

app = FastAPI()
model = pickle.load(open('h1b_prediction_model_rf2.pk', 'rb'))

@app.post("/predict")
async def predict(employer: int, soc: int, job_title: int, 
                 wage: float, state: int, city: int):
    input_data = np.array([[employer, soc, job_title, wage, state, city]])
    proba = model.predict_proba(input_data)[0][1]
    return {"approval_probability": float(proba)}
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Areas for potential contributions:
- Additional data preprocessing improvements
- Model optimization and tuning
- Enhanced visualization in the Streamlit app
- Dockerization of the application

## License

MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.