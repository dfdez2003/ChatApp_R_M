function startChat(roomId) {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("No estás autenticado. Inicia sesión.");
    window.location.href = "/auth/login";
    return;
  }

  const ws = new WebSocket(`ws://${location.host}/ws/${roomId}?token=${token}`);

  ws.onopen = () => {
    console.log(`✅ Conectado a sala ${roomId}`);
  };

  ws.onmessage = (event) => {
    const chatbox = document.getElementById("chatbox");
    const message = document.createElement("p");
    message.textContent = event.data;
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
      ws.send(text);
      input.value = "";
    }
  };
}
