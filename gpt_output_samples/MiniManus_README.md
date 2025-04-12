
# MiniManus – An AI-Powered Research Assistant

MiniManus is an AI-powered research assistant designed to help researchers manage, analyze, and interact with large datasets. It integrates data processing, AI models, and user-friendly interfaces to streamline the research process and assist researchers in generating insights.

---

## Features

- **AI Research Assistance**: Use AI models to assist with data analysis, report generation, and research insights.
- **Data Ingestion and Processing**: Ingest and preprocess data using automated pipelines.
- **User Interface**: A simple frontend for interaction with the system via Streamlit.
- **Modular System**: Extensible architecture for adding new features or AI models.

---

## Project Structure

```
MiniManus/
│
├── data_processing/       # Modules for data ingestion and processing
├── frontend/             # User interface components
├── mini_manus_ai/        # Core AI models and algorithms
├── prototyping/         # Experimental features and prototypes
├── prototyping_outputs/  # Outputs from prototyping experiments
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Installation

### 1. Clone the Repository

Clone the MiniManus repository to your local machine:

```bash
git clone https://github.com/BigDataSystemsTeam5/MiniManus.git
cd MiniManus
```

### 2. Install Dependencies

Install the required Python packages listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Data Processing

The `data_processing` module handles data ingestion and preprocessing. To process data:

```bash
python data_processing/process_data.py
```

Ensure the data files are placed in the correct directory as specified in the script.

### 2. AI Model Integration

Train or fine-tune models using the `mini_manus_ai` module:

```bash
python mini_manus_ai/train_model.py
```

Follow the instructions in the script for dataset preparation and model parameters.

### 3. Running the Frontend

The `frontend` directory uses Streamlit to provide a user interface for the application. To run the frontend:

```bash
streamlit run frontend/app.py
```

Access the application at `http://localhost:8501` in your browser.

---

## Contributing

We welcome contributions to MiniManus! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request.

---

## License

MiniManus is open-source software licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contact

For questions or feedback, please open an issue in the repository or contact the maintainers via the repository's issue tracker.

---

By using MiniManus, you can streamline your research workflow with AI-powered insights and data processing tools.
