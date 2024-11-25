from flask import Flask, render_template, request
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader
import openai
import pypdf
import os
import time

# openai.api_key = 'tu_api_key_aqui'
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def read_data():
    # Cargar los documentos desde la carpeta "upload"
    reader = SimpleDirectoryReader(input_dir="upload", recursive=True)
    docs = reader.load_data()

    # Configuración del modelo sin `ServiceContext`
    # llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the docs and can provide helpful summaries")
    llm = OpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
    system_prompt=(
        "You are a document analysis and quiz generation assistant. Your task is to analyze the uploaded document and generate questions or respond strictly based on its content. "
        "Instructions: "
        "1. Generate questions in one of the following formats based on the document: "
        "- Multiple-choice (options A to D): Ensure there is only one correct answer and the other options are plausible but incorrect. "
        "- Fill-in-the-blank: Use specific information from the document for this format. "
        "2. Respond strictly based on the content of the uploaded document. Do not answer any question that is unrelated to the document or provide information not present in it. "
        "3. If a user asks a question outside the scope of the document, respond politely: 'I can only answer questions based on the uploaded document. Please ask about its content.' "
        "4. For multiple-choice questions: "
        "- Present the question, options (A, B, C, D), and indicate the correct answer. "
        "- Ensure that the options are challenging but fair, based only on the content of the document. "
        "5. For fill-in-the-blank questions: "
        "- Clearly identify the part of the document being referenced. "
        "- Ensure the blank corresponds to a key concept, fact, or term from the document. "
        "Additional Rules: "
        "Always clarify which section or part of the document your response references. "
        "Do not include unrelated information, even if prompted. "
        "Use professional, concise language, and organize your responses clearly. "
        "Your primary goal is to help users understand the content of the uploaded document and create engaging, accurate exercises based on it. Ensure that all questions are relevant, accurate, and aligned with the document's subject matter."
    )
)

    # Crear el índice
    index = VectorStoreIndex.from_documents(docs, llm=llm)
    chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
    
    return chat_engine

def safe_get_embeddings(*args, **kwargs):
    while True:
        try:
            # Intentar hacer la solicitud a OpenAI
            return openai.Embedding.create(*args, **kwargs)
        except Exception as e:  # Capturamos cualquier excepción
            error_message = str(e)
            if "Rate limit" in error_message or "quota" in error_message:
                print(f"Rate limit exceeded or quota exceeded. Retrying in 60 seconds...")
                time.sleep(60)  # Esperar 60 segundos antes de reintentar
            else:
                print(f"Error: {error_message}. Exiting.")
                break  # Si no es un error de cuota, salimos del bucle

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file.filename.endswith('.pdf'):

            upload_folder = 'upload'
            os.makedirs(upload_folder, exist_ok=True)
            pdf_path = os.path.join(upload_folder, pdf_file.filename)
            pdf_file.save(pdf_path)
            print(f"Uploaded PDF path: {pdf_path}")

            return render_template('chat.html', upload_success=True)
        else:
            return render_template('index.html', upload_error="Invalid file format. Please upload a PDF.")
    else:
        return render_template('index.html', upload_error="No file uploaded.")

@app.route('/chat', methods=['POST'])
def chat():
    chat_engine = read_data()
    if request.method == 'POST':
        prompt = request.form['prompt']
        try:
            response = chat_engine.chat(prompt)
            return render_template('chat.html', prompt=prompt, response=response.response)
        except Exception as e:
            print(f"Error occurred: {e}")
            return render_template('chat.html', prompt=prompt, response="An error occurred, please try again later.")
    
if __name__ == '__main__':
    app.run(debug=True)
