# Proyecto Chat para Generación de Preguntas

## Descripción

Este proyecto es una aplicación web que genera preguntas personalizadas basadas en el tipo de pregunta, el nivel de dificultad y el número de preguntas. El usuario elige estos parámetros y el servidor genera las preguntas sin recargar la página, utilizando AJAX.

## Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML, TailwindCSS, JavaScript
- **AJAX**: Para enviar los datos sin recargar la página
- **Plantillas**: Jinja2 para la generación dinámica del HTML

## Estructura de Archivos


## Flujo de Trabajo

1. **Formulario de Configuración**: El usuario selecciona el tipo de pregunta, el nivel de dificultad y el número de preguntas (1-20).
2. **Generación de Preguntas**: Los datos se envían al servidor mediante AJAX, el cual genera las preguntas y las devuelve en formato JSON.
3. **Mostrar Resultados**: Las preguntas generadas se muestran sin recargar la página.
4. **Interacción**: El usuario puede seguir interactuando con el chat, realizando nuevas solicitudes.

## Archivos Clave

- **app.py**: Configuración y rutas del servidor Flask.
- **/static/js/chat.js**: Lógica JavaScript para manejar las interacciones y AJAX.
- **/templates/chat.html**: Plantilla del chat con el formulario y resultados.

