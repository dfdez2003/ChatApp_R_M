// Espera que cargue el DOM
document.addEventListener("DOMContentLoaded", () => {   //  - Espera a que toda la página HTML esté cargada antes de ejecutar el código.
    const form = document.getElementById("formRegistro");   //  Obtienen referencias al formulario y al div de mensajes usando sus IDs.
    const mensajeDiv = document.getElementById("mensaje");
  
    form.addEventListener("submit", async (e) => {  // Escucha si el usuario intenta hacer un formulario 
      e.preventDefault();                              // Evita que se envia normal, por uqe recargaria la pag
        
      // Captura los datos del formulario           // creamos el obj
      const data = {
        nombre: form.nombre.value,
        surname: form.surname.value,
        username: form.username.value,
        email: form.email.value,
        password: form.password.value
      };
  
      try {
        // Nos movemos a el server de regiter y hacemos el post 
        const res = await fetch("http://localhost:8000/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });
  
        const result = await res.json();            // Envia la respuesta como jb
  
        if (res.ok) {           // Manejar la respuestas del servidor 
          mensajeDiv.textContent = "✅ Registro exitoso. ¡Ahora inicia sesión!";
          mensajeDiv.className = "success";
          form.reset();
        } else {
          mensajeDiv.textContent = result.detail || "❌ Error al registrar.";
          mensajeDiv.className = "error";
        }
      } catch (err) {   // errores de conexión al servidor 
        mensajeDiv.textContent = "❌ Error de conexión con el servidor.";
        mensajeDiv.className = "error";
      }
    });
  });
  