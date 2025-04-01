# Financial Report Analysis and Compliance Assessment Tool

## Overview
This application automates financial report analysis and compliance assessments using AI and NLP techniques. It extracts data from uploaded PDFs, answers predefined financial questions, evaluates regulatory compliance, and generates structured financial summaries.

---

## 💡 **Features**
- **Automated Text Extraction:** Extracts text from PDF files for further processing.
- **Financial Analysis & QA:** Generates AI-driven answers to financial and compliance questions.
- **Compliance Assessment:** Validates financial documents against regulatory requirements.
- **Summarization:** Provides structured financial summaries with key insights.
- **Intelligent Search:** Leverages FAISS for semantic search within documents.

---

## 🛠️ **Tech Stack**
- **Backend:** Flask (Python Framework)
- **NLP & AI Models:** Llama3, Sentence-Transformers, LangChain
- **Vector Search:** FAISS
- **PDF Processing:** pdfplumber
- **Embedding Models:** Hugging Face
- **APIs & Integrations:** Groq API, Ngrok

---

## 🚀 **Installation Guide**
1. Clone the repository:
   ```bash
   git clone https://github.com/username/financial-analysis-tool.git
   cd financial-analysis-tool
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables (API keys, credentials, etc.).
5. Run the application:
   ```bash
   python app.py
   ```
6. Access the tool in your browser at `http://localhost:5000`

---

## 🎮 **Usage Guide**
1. Upload a PDF via `/extract_text` endpoint.
2. Split extracted text using `/clean_split_text`.
3. Create vector index with `/create_faiss_index`.
4. Generate AI responses using `/generate_answers`.
5. Summarize results with `/generate_summary`.
6. Run compliance checks using `/compliance_assessment`.

---

## ✅ **API Endpoints**
- **/extract_text**: Uploads PDF and extracts text.
- **/clean_split_text**: Splits extracted text into chunks.
- **/create_faiss_index**: Builds a vector index.
- **/generate_answers**: Provides AI-driven answers to questions.
- **/generate_summary**: Generates a financial summary.
- **/compliance_assessment**: Performs compliance assessment.

---

## 🔍 **Sample Request & Response**
```json
POST /extract_text
{
  "file": "sample.pdf"
}

Response:
{
  "extracted_text": "Company XYZ's financial report for Q4..."
}
```

---

## 🎉 **Benefits**
- Automates manual tasks for financial analysts and auditors.
- Ensures regulatory compliance with minimal effort.
- Provides rapid insights and actionable recommendations.
- Scalable and adaptable for various financial documents.


