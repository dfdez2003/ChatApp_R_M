document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const loginData = {
        username,
        password
    };

    try {
        const response = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem("access_token", data.access_token);  // Guardamos el token
            alert("Inicio de sesión exitoso");
            window.location.href = "home.html";  // Redirigir a la página de inicio
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error al iniciar sesión:", error);
    }
});
