const showFormBtn = document.getElementById("showFormBtn");
const formContainer = document.getElementById("formContainer");
const h1 = document.querySelector("h1");
const emoji = document.querySelector(".emoji");

showFormBtn.addEventListener("click", (event) => {
    // Ocultar el botón con animación
    showFormBtn.classList.add("animate-hideButton");
    
    // Animación para mover el título y emoji juntos y reducir su tamaño
    h1.classList.add("animate-moveUpResize");
    
    // Animación para mover el emoji desde arriba y rotar
    emoji.classList.add("animate-moveDownRotate");

    // Mostrar el formulario con animación
    formContainer.classList.remove("hidden");
    formContainer.classList.add("animate-showForm");

    // Efecto de partículas (emoji) expandido con colores aleatorios
    generateParticles(event);
});
let showEmoji = true; // Puedes cambiarlo a `false` si prefieres círculos en lugar de emoji

function generateParticles(event) {
    const numParticles = 200; // Aumentar el número de partículas para mayor cobertura
    const spreadRange = 1500; // Aumentar el rango de dispersión para cubrir más espacio
    for (let i = 0; i < numParticles; i++) {
        const particle = document.createElement('span');
        particle.classList.add('particle');

        // Si showEmoji es verdadero, mostramos un emoji
        if (showEmoji) {
            particle.textContent = "🤖";  // Emoji de partícula
        } else {
            // Si no es emoji, mostramos un círculo redondeado
            particle.style.backgroundColor = getRandomColor();  // Color aleatorio para el círculo
            particle.style.width = '15px';  // Tamaño del círculo
            particle.style.height = '15px';  // Tamaño del círculo
            particle.style.borderRadius = '50%';  // Esto hace que el elemento sea redondo
        }

        // Asignación de una posición aleatoria en el rango
        const x = Math.random() * spreadRange - spreadRange / 2;
        const y = Math.random() * spreadRange - spreadRange / 2;

        particle.style.setProperty('--x', `${x}px`);
        particle.style.setProperty('--y', `${y}px`);

        // Coloca la partícula en la posición del evento
        particle.style.left = `${event.clientX - 10}px`;
        particle.style.top = `${event.clientY - 10}px`;

        document.body.appendChild(particle);

        // Elimina la partícula después de la animación
        setTimeout(() => {
            particle.remove();
        }, 2000); // La partícula desaparece después de 2 segundos
    }
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

