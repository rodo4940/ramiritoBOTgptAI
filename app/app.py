from flask import Flask, render_template, request
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader
import openai
import os
import time

# openai.api_key = 'tu_api_key_aqui'
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def read_data():
    # Cargar los documentos desde la carpeta "upload"
    reader = SimpleDirectoryReader(input_dir="upload", recursive=True)
    docs = reader.load_data()

    # Configuración del modelo sin `ServiceContext`
    llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.5,
        system_prompt=(
            "Eres un asistente diseñado para generar preguntas de opción múltiple o de completar espacios basadas exclusivamente en el contenido del documento subido. "
            "Tu tarea es analizar el texto del archivo y generar preguntas sobre el contenido que se encuentra dentro de él. "
            "Instrucciones: "
            "1. No hagas preguntas sobre el archivo en sí mismo, como la ubicación del archivo, número de páginas, o el tipo de archivo. "
            "2. Las preguntas deben basarse **únicamente** en el contenido del texto del archivo. "
            "3. Para preguntas de opción múltiple, asegúrate de que haya solo una respuesta correcta, con las opciones restantes siendo plausibles pero incorrectas. "
            "4. Para preguntas de completar, asegúrate de que el espacio vacío esté relacionado con una palabra o concepto clave del documento. "
            "5. No hagas suposiciones ni incluyas detalles no mencionados en el documento. "
            "6. Si la información en el documento no es suficiente para generar preguntas relevantes, responde educadamente: 'No puedo generar preguntas basadas en el contenido del archivo. Por favor, pregunte sobre su contenido.'"
            "Tu objetivo es generar preguntas claras, precisas y directamente relacionadas con el contenido del documento subido."
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
