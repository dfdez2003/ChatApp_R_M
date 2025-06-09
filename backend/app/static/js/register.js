document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");

  if (!form) {
    console.error("No se encontró el formulario.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();  // 🛑 Esto detiene el submit tradicional
    console.log("Formulario capturado correctamente");

    const nombre = document.getElementById("nombre").value;
    const surname = document.getElementById("surname").value;
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ nombre, surname, username, email, password })
      });

      const data = await response.json();
      if (response.ok) {
         // Mostrar mensaje y redirigir después de 2 segundos
         // alert("¡Registro exitoso! Serás redirigido al login...");
         console.log("Respuesta del servidor:", data);
         setTimeout(()=> {
          window.location.href = "/auth/login"; // ruta relativa 
         },2000);
      } else {
        alert("Error: " + data.detail || "Error en el registro");
      }
    } catch (error) {
      console.error("Error al registrar:", error);
      alert("Error de conexión con el servidor");
    }
  });
});
