# Update the import at the top of the file
from flask import Flask, request, jsonify
import pdfplumber
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from groq import Groq
from pyngrok import ngrok
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# Add root endpoint
@app.route('/')
def home():
    return jsonify({
        "status": "API is running",
        "endpoints": {
            "POST /extract_text": "Extract text from PDF",
            "POST /clean_split_text": "Clean and split text into chunks",
            "POST /create_faiss_index": "Create FAISS index from chunks",
            "POST /generate_answers": "Generate answers from index",
            "POST /generate_summary": "Generate summary from answers",
            "POST /financial_report_pipeline": "Complete pipeline for financial analysis"
        }
    })

# Initialize Groq API
client = Groq(api_key="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")

# Updated system prompt for structured responses
SYSTEM_PROMPT = """You are a financial analyst AI. When answering questions about financial reports:
1. Keep answers concise and structured
2. Use bullet points where appropriate
3. Focus on key metrics and numbers
4. Format numbers consistently
5. Highlight year-over-year changes
6. Maximum response length: 3-4 bullet points"""

# Predefined Financial Questions
predefined_questions = [
    "What is the total revenue?",
    "What are the major expenses mentioned in the report?",
    "What is the net profit or loss for the year?",
    "What are the key financial risks mentioned?",
    "What growth strategies are outlined in the report?",
    "What are the major investments or capital expenditures?",
    "What is the company's debt or liability status?",
    "What is the cash flow status (operating, investing, financing)?",
    "What are the key highlights from the balance sheet?",
    "What is the company's outlook for the next financial year?"
]

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    pdf_file = request.files['file']
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return jsonify({"extracted_text": text.strip()})
    except Exception as e:
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

@app.route('/clean_split_text', methods=['POST'])
def clean_split_text():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        return jsonify({"chunks": chunks})
    except Exception as e:
        return jsonify({"error": f"Error splitting text: {str(e)}"}), 500

# Initialize global variable at the top level
faiss_index = None

@app.route('/create_faiss_index', methods=['POST'])
def create_faiss_index():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    chunks = data.get('chunks', [])
    if not chunks:
        return jsonify({"error": "No chunks provided"}), 400
    
    try:
        # Import FAISS explicitly
        import faiss
        
        # Basic embeddings configuration
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Create the index with explicit FAISS initialization
        global faiss_index
        faiss_index = FAISS.from_texts(
            texts=chunks,
            embedding=embeddings,
            normalize_L2=True  # Enable L2 normalization for better matching
        )
        
        return jsonify({
            "status": "FAISS index created successfully",
            "chunks_processed": len(chunks)
        })
    except ImportError as e:
        print(f"FAISS import error: {str(e)}")
        return jsonify({"error": "FAISS not properly installed. Please install faiss-cpu."}), 500
    except Exception as e:
        print(f"Error creating FAISS index: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_answers', methods=['POST'])
def generate_answers():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    questions = data.get('questions', predefined_questions)
    
    global faiss_index
    if faiss_index is None:
        return jsonify({"error": "No FAISS index available. Please create an index first using /create_faiss_index"}), 400
    
    try:
        answers = {}
        for question in questions:
            relevant_chunks = faiss_index.similarity_search(question, k=3)
            combined_text = "\n".join([chunk.page_content for chunk in relevant_chunks])

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Based on this text, {question}\n\nText:\n{combined_text}"}
                ]
            )
            answers[question] = response.choices[0].message.content.strip()

        return jsonify({"answers": answers})
    except Exception as e:
        return jsonify({"error": f"Error generating answers: {str(e)}"}), 500

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    answers = data.get('answers', {})
    if not answers:
        return jsonify({"error": "No answers provided"}), 400
    
    try:
        combined_answers = "\n".join([f"{q} ➡️ {a}" for q, a in answers.items()])
        summary_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": 
                 "Summarize the following answers into a structured financial summary. "
                 "Organize the content under these sections:\n"
                 "1. Key Trends\n"
                 "2. Liquidity & Cash Flow Health\n"
                 "3. Risk Indicators\n"
                 "4. Recommendations for Financial Stability\n"},
                {"role": "user", "content": combined_answers}
            ]
        )
        return jsonify({"summary": summary_response.choices[0].message.content.strip()})
    except Exception as e:
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500

@app.route('/financial_report_pipeline', methods=['POST'])
def financial_report_pipeline():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    pdf_file = request.files['file']
    
    try:
        # Extract text
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        if not text:
            return jsonify({"error": "No text extracted from PDF"}), 400

        # Process text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        # Create FAISS index
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        index = FAISS.from_texts(chunks, embeddings)
        
        # Generate answers with structured format
        answers = {}
        for question in predefined_questions:
            relevant_chunks = index.similarity_search(question, k=3)
            combined_text = "\n".join([chunk.page_content for chunk in relevant_chunks])

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Based on this text, {question}\n\nText:\n{combined_text}"}
                ]
            )
            answers[question] = response.choices[0].message.content.strip()

        # Generate final summary
        combined_answers = "\n".join([f"{q} ➡️ {a}" for q, a in answers.items()])
        summary_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": 
                 "Summarize the following answers into a structured financial summary. "
                 "Organize the content under these sections:\n"
                 "1. Key Trends\n"
                 "2. Liquidity & Cash Flow Health\n"
                 "3. Risk Indicators\n"
                 "4. Recommendations for Financial Stability\n"},
                {"role": "user", "content": combined_answers}
            ]
        )
        final_summary = summary_response.choices[0].message.content.strip()

        return jsonify({
            "qa_results": answers,
            "final_summary": final_summary
        })
    
    except Exception as e:
        return jsonify({"error": f"Error in pipeline: {str(e)}"}), 500

if __name__ == '__main__':
    ngrok.set_auth_token("2qKgNOz815jWWDAJD3WJga2VROT_sFasJqFrEu5MKBTVnvfn")
    ngrok_url = ngrok.connect(5000).public_url
    print(f"Public URL: {ngrok_url}")
    app.run(port=5000)