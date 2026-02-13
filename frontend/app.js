async function testHealth() {
    const statusElement = document.getElementById("health");

    try {
        const response = await fetch("/health");
        const data = await response.json();

        statusElement.textContent = "Backend: " + data.status;
        statusElement.style.color = "green";

    } catch (error) {
        statusElement.textContent = "Backend: erreur (serveur non démarré)";
        statusElement.style.color = "red";
    }
}

document.addEventListener("DOMContentLoaded", testHealth);
