let ws = null;

async function startChat(roomId) {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario"));

  if (!token || !usuario) {
    alert("No estás autenticado. Inicia sesión.");
    window.location.href = "/auth/login";
    return;
  }

  const API_URL = `${window.location.origin}`;

  // Mostrar datos del usuario en la cabecera
  document.getElementById("user-name").textContent =
    usuario.username || "Usuario";
  document.getElementById("user-avatar").textContent =
    usuario.username?.charAt(0).toUpperCase() || "U";

  // ✅ 1. Cargar historial de mensajes antes de conectar al WebSocket
  try {
    const res = await fetch(`${API_URL}/mensajes/${roomId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const historial = await res.json();

    if (Array.isArray(historial)) {
      const chatbox = document.getElementById("chatbox");
      historial.forEach(data => {
        const message = document.createElement("p");
        message.innerHTML = `<strong>${data.username}:</strong> ${data.contenido}`;
        chatbox.appendChild(message);
      });
      chatbox.scrollTop = chatbox.scrollHeight;
    }
  } catch (e) {
    console.error("❌ Error al cargar historial:", e);
  }

  // ✅ 2. Establecer conexión WebSocket
  const ws = new WebSocket(`ws://${location.host}/ws/${roomId}?token=${token}`);

  ws.onopen = () => {
    console.log(`✅ Conectado a sala ${roomId} como ${usuario.username}`);
  };

  ws.onmessage = (event) => {
    const chatbox = document.getElementById("chatbox");
    const data = JSON.parse(event.data);
    console.log("📩 Mensaje recibido:", data);

    const message = document.createElement("p");
    message.innerHTML = `<strong>${data.username}:</strong> ${data.contenido}`;
    chatbox.appendChild(message);
    chatbox.scrollTop = chatbox.scrollHeight;
  };

  ws.onclose = () => {
    console.log("❌ Conexión cerrada");
  };

  window.sendMessage = () => {
    const input = document.getElementById("messageInput");
    const text = input.value.trim();

    if (text !== "") {
      const mensaje = {
        contenido: text,
        sala_id: roomId
      };
      console.log("📤 Enviando mensaje:", mensaje);
      ws.send(JSON.stringify(mensaje));
      input.value = "";
    }
  };
}
