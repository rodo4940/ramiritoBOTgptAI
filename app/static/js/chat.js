// Función para actualizar la entrada en el formulario izquierdo
function updateInput() {
    const questionType = document.querySelector('input[name="questionType"]:checked').value;
    const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
    const count = document.getElementById('questionCount').value;

    const inputField = document.getElementById('prompt');
    inputField.value = `Generar ${count} preguntas de ${questionType} de nivel ${difficulty}`;

    // Actualizamos el input en la parte inferior del chat
    const inputFieldBottom = document.getElementById('promptBottom');
    inputFieldBottom.value = inputField.value;
}

// Función para enviar el formulario desde el botón debajo del chatbox
function submitForm() {
    const form = document.getElementById('chatForm');
    form.submit();  // Enviar el formulario
}

// Función para actualizar el formulario izquierdo al modificar el input en la parte inferior
function syncWithBottomInput() {
    const bottomInput = document.getElementById('promptBottom').value;
    const count = bottomInput.match(/\d+/);  // Buscar número de preguntas
    const questionType = bottomInput.includes("opción múltiple") ? "opción múltiple" : "para completar";
    const difficulty = bottomInput.includes("fácil") ? "fácil" : bottomInput.includes("intermedio") ? "intermedio" : "difícil";

    // Sincronizamos los valores del formulario
    if (count) {
        document.getElementById('questionCount').value = count[0];  // Actualizamos el número de preguntas
        document.getElementById('countDisplay').textContent = count[0];  // Actualizamos la visualización del número de preguntas
    }

    // Actualizamos el tipo de pregunta
    const questionTypeRadio = document.querySelector(`input[name="questionType"][value="${questionType}"]`);
    if (questionTypeRadio) {
        questionTypeRadio.checked = true;
    }

    // Actualizamos el nivel de dificultad
    const difficultyRadio = document.querySelector(`input[name="difficulty"][value="${difficulty}"]`);
    if (difficultyRadio) {
        difficultyRadio.checked = true;
    }

    updateInput();  // Actualizamos el input principal en el formulario
}