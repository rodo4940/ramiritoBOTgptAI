from flask import Flask, render_template, request
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader
import openai
import re
import os
import time

# Configuración de OpenAI
openai.api_key = os.getenv("OPEN_AI_API_KEY")

# Crear la instancia de la aplicación Flask
app = Flask(__name__)

# Función para cargar los documentos y crear el motor de chat
def read_data():
    reader = SimpleDirectoryReader(input_dir="upload", recursive=True)
    docs = reader.load_data()

    # Configuración del modelo OpenAI
    llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.5,
        system_prompt = (
            "Eres un asistente diseñado para generar preguntas de opción múltiple o de completar espacios basadas exclusivamente en el contenido del documento subido. "
            "Genera preguntas claras, precisas y directamente relacionadas con el contenido. "
            "Instrucciones: "
            "1. No hagas preguntas sobre el archivo (ej. ubicación, número de páginas, tipo de archivo). "
            "2. Si la pregunta no tiene relación directa con el contenido del documento, responde con el mensaje: 'Esta pregunta no está relacionada con el documento proporcionado.' "
            "3. Las preguntas deben basarse únicamente en el contenido del documento. "
            "4. Para preguntas de opción múltiple, una opción debe ser correcta y las otras plausibles pero incorrectas. "
            "5. Para preguntas de completar, los espacios vacíos deben estar relacionados con palabras o conceptos clave. "
            "6. Si se pide retroalimentación, proporciona una respuesta basada en el documento. "
            "7. Las preguntas deben adaptarse al nivel de dificultad especificado (fácil, intermedio, difícil)."
        )
    )

    # Crear el índice y el motor de chat
    index = VectorStoreIndex.from_documents(docs, llm=llm)
    return index.as_chat_engine(chat_mode="condense_question", verbose=True)

# Función para manejar la carga de embeddings con reintentos en caso de error
def safe_get_embeddings(*args, **kwargs):
    attempts = 0
    max_attempts = 5  # Limitar los intentos
    while attempts < max_attempts:
        try:
            return openai.Embedding.create(*args, **kwargs)
        except Exception as e:
            if "Rate limit" in str(e) or "quota" in str(e):
                print("Rate limit exceeded. Retrying in 60 seconds...")
                time.sleep(60)  # Esperar antes de reintentar
            else:
                print(f"Error: {e}. Exiting.")
                break
        attempts += 1
    return None  # Devolver None si no se pudo obtener el embedding

# Función para formatear la respuesta de chat, con mejor manejo de preguntas y respuestas
def format_response(response_text):
    formatted_text = ""
    question_pattern = r"([A-Za-z0-9\s,;:¿?]+[?])"
    answer_pattern = r"([A-D]\)\s.*)|(\d+\)\s.*)"

    # Palabras que deseas resaltar en color rojo
    feedback_keywords = ['Feedback', 'Retroalimentación']

    for line in response_text.split("\n"):
        # Resaltar las palabras claves "Feedback" o "retroalimentación"
        for keyword in feedback_keywords:
            if keyword.lower() in line.lower():
                line = line.replace(keyword, f"<span class='text-red-500'>{keyword}</span>")

        question_match = re.match(question_pattern, line.strip())
        answer_match = re.match(answer_pattern, line.strip())

        if question_match:
            formatted_text += f"<p><strong>{question_match.group(0).strip()}</strong></p>\n"
        elif answer_match:
            formatted_text += f"<p class='ml-6'>{answer_match.group(0).strip()}</p>\n"
        elif line.strip():
            formatted_text += f"<p>{line.strip()}</p>\n"
    
    return formatted_text



# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para subir el archivo PDF
@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' not in request.files:
        return render_template('index.html', upload_error="No file uploaded.")
    
    pdf_file = request.files['pdf_file']
    
    if not pdf_file.filename.endswith('.pdf'):
        return render_template('index.html', upload_error="Invalid file format. Please upload a PDF.")
    
    upload_folder = 'upload'
    os.makedirs(upload_folder, exist_ok=True)
    pdf_path = os.path.join(upload_folder, pdf_file.filename)
    pdf_file.save(pdf_path)
    print(f"Uploaded PDF path: {pdf_path}")
    
    # Crear el motor de chat después de cargar el archivo
    chat_engine = read_data()
    return render_template('chat.html', upload_success=True)

# Ruta para manejar el chat
@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.form['prompt']
    if not prompt:
        return render_template('chat.html', response="No prompt provided.")
    
    chat_engine = read_data()  # Cargar el chat engine nuevamente para cada solicitud
    try:
        response = chat_engine.chat(prompt)
        formatted_response = format_response(response.response)
        return render_template('chat.html', prompt=prompt, response=formatted_response)
    except Exception as e:
        print(f"Error occurred: {e}")
        return render_template('chat.html', prompt=prompt, response="An error occurred. Please try again later.")

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
