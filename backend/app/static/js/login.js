document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();  // Evita el envío tradicional del formulario
        e.stopPropagation(); // Detiene propagación innecesaria

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!username || !password) {
            alert("Por favor completa todos los campos.");
            return;
        }

        try {
            const response = await fetch(`${window.location.origin}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Error al iniciar sesión");
            }

            const data = await response.json();
            console.log("✅ Login exitoso:", data);
            // ✅ Guardar token y usuario
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("usuario", JSON.stringify(data.usuario));

            // Esperar un poco para asegurar escritura antes de redirigir
            await new Promise(resolve => setTimeout(resolve, 100));

            // ✅ Redirigir al panel de salas
            window.location.href = `${window.location.origin}/salas/`;

        } catch (error) {
            console.error("Error en login:", error);
            alert(error.message);
        }
    });
});
