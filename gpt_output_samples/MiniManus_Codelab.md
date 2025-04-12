
summary: AI Research Assistant
id: mini-manus
categories: Data Engineering, AI, Python, Machine Learning
status: Published
authors: Pratik Kanade
feedback link: https://github.com/BigDataSystemsTeam5/MiniManus/issues

# MiniManus - Codelab
**ID:** mini-manus

## **Introduction**
### **What You’ll Build**
In this Codelab, you will learn how to set up and deploy **MiniManus**, an AI-powered research assistant that helps researchers analyze and manage large datasets. The system leverages **FastAPI** for backend API services, **Streamlit** for frontend interactions, and **LangChain** for data-driven AI model operations.

### **What You’ll Learn**
- How to integrate **FastAPI** with **Streamlit**.
- How to build AI models for data analysis.
- How to process and transform data using **LangChain**.
- How to deploy the system using **Docker** and **AWS**.
- How to create a user interface for seamless interaction.

### **Prerequisites**
- Basic understanding of Python.
- Familiarity with **FastAPI** and **Streamlit**.
- Knowledge of Docker and AWS setup.

---

## **Step 1: Clone the Repository**
First, clone the repository containing the project files.

```sh
git clone https://github.com/BigDataSystemsTeam5/MiniManus.git
cd MiniManus
```

---

## **Step 2: Setup the Environment**
Create a Python virtual environment and install dependencies.

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
pip install -r requirements.txt
```

Create a **.env** file with your environment variables:

```sh
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
PINECONE_API_KEY=your_pinecone_api_key
```

---

## **Step 3: Backend Development (FastAPI)**
We developed a **FastAPI backend** with multiple endpoints for handling data processing and AI model interactions.

### **Key Backend Features:**
- **Data Processing**: Upload and process large datasets.
- **AI Model Integration**: Use LangChain to process data using AI models.
- **Data Transformation**: Transform and enrich data.
- **Model Query API**: Interact with AI models to extract insights from data.

### **Start the FastAPI Backend:**
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Once running, visit `http://127.0.0.1:8000/docs` to explore API endpoints.

---

## **Step 4: Frontend Development (Streamlit)**
The **Streamlit UI** provides an interactive way to:
- Upload and preprocess datasets.
- Choose AI models for data analysis.
- Visualize data transformations and results.
- Interact with model-generated insights.

### **Start the Streamlit Frontend:**
```sh
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501/`.

---

## **Step 5: AI Model Integration with LangChain**
We integrated **LangChain** to manage and query data through AI models. This module handles:
- **Data Transformation**: Use LangChain to process and analyze data.
- **Model Interaction**: Send queries to AI models and retrieve insights.
- **Pinecone Integration**: Retrieve data from Pinecone database for model input.

### **Example LangChain Model Code:**
```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain

llm = OpenAI(temperature=0.7)
chain = LLMChain(llm=llm)

def generate_summary(data):
    return chain.run(data)
```

---

## **Step 6: Data Storage and Caching**
We use **Pinecone** for vector-based storage and **Redis** for caching intermediate results, enhancing performance.

### **Start Redis Server:**
```sh
redis-server
```

### **Pinecone Integration:**
Store and query embeddings for large datasets in Pinecone.

```python
import pinecone

pinecone.init(api_key='your_api_key', environment='your_env')
index = pinecone.Index('your_index')

# Query Pinecone
query = "Retrieve top 3 similar datasets"
result = index.query(query)
```

---

## **Step 7: Deployment with Docker Compose**
To deploy the entire system, use **Docker Compose**:

### **Docker Setup:**
1. Create a `Dockerfile` for the FastAPI backend and Streamlit frontend.
2. Define a `docker-compose.yml` to run both services along with Redis and Pinecone.

### **Build & Run Containers:**
```sh
docker-compose up --build
```

The application will be accessible at:
- **Streamlit UI:** `http://localhost:8501`
- **FastAPI Backend:** `http://localhost:8000/docs`

To stop the containers:
```sh
docker-compose down
```

---

## **Step 8: Key Takeaways**
✅ **FastAPI & Streamlit** integration for building user-friendly applications.

✅ **LangChain** for AI-powered data transformations and insights.

✅ **Pinecone** and **Redis** for efficient data storage and caching.

✅ **Docker-based deployment** for scalable infrastructure.

---

## **Conclusion**
By completing this Codelab, you have successfully built **MiniManus**, an AI-powered research assistant for managing and analyzing large datasets. You can extend this project with additional features, models, and deployment strategies for enhanced functionality.

---

## **Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://www.langchain.com/docs/)
- [Pinecone Documentation](https://www.pinecone.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
