
function formatearSegundos(segundos) {
  if (segundos === null || segundos === undefined) return "Permanente";
  const min = Math.floor(segundos / 60);
  const seg = segundos % 60;
  return `${min} min ${seg} seg`;
}

function iniciarCuentaRegresiva(segundosIniciales, elementoDestino) {
  let tiempoRestante = segundosIniciales;

  function actualizar() {
    if (tiempoRestante <= 0) {
      elementoDestino.textContent = "Expirada";
      clearInterval(timerInterval);
    } else {
      elementoDestino.textContent = formatearSegundos(tiempoRestante);
      tiempoRestante--;
    }
  }

  actualizar(); // mostrar inmediatamente
  const timerInterval = setInterval(actualizar, 1000);
}


document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    const salaId = params.get('id');
  
    if (!salaId) {
      alert('No se especificó el ID de la sala');
      window.location.href = '/salas/';
      return;
    }
  
    const token = sessionStorage.getItem('token');
    if (!token) {
      alert('No estás autenticado');
      window.location.href = '/auth/login';
      return;
    }
  
    try {
      console.log("🔎 Buscando sala con ID:", salaId);
      const response = await fetch(`/salas/detalles/${salaId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
  
      if (!response.ok) {
        throw new Error("No se pudo obtener la sala");
      }
  
      const sala = await response.json();
      console.log("📦 Datos de la sala:", sala);
  
      document.getElementById('sala-nombre').textContent = sala.nombre;
      document.getElementById('sala-descripcion').textContent = sala.descripcion || 'Sin descripción';
      document.getElementById('sala-tipo').textContent = sala.es_publica ? 'Pública' : 'Privada';
      document.getElementById('sala-tipo').className = `sala-badge ${sala.es_publica ? 'public' : 'private'}`;
      // document.getElementById("sala-tiempo-vida").textContent = formatearSegundos(sala.tiempo_restante);
      const tiempoEl = document.getElementById("sala-tiempo-vida");
      //iniciarCuentaRegresiva(sala.tiempo_restante, tiempoEl);
      if (sala.tiempo_restante === null || sala.tiempo_restante === -1 || sala.tiempo_restante === undefined) {
        tiempoEl.textContent = "Permanente";
      } else {
        iniciarCuentaRegresiva(sala.tiempo_restante, tiempoEl);
      }
      
      const fecha = new Date(sala.fecha_creacion);
      document.getElementById('sala-fecha').textContent = fecha.toLocaleDateString('es-ES', {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
  
      // const tiempoVida = sala.tiempo_vida ? `${sala.tiempo_vida} horas` : 'Indefinido';
      // document.getElementById('sala-tiempo-vida').textContent = tiempoVida;
  
      document.getElementById('sala-estado').textContent = 'Activa';
  
      document.getElementById('sala-avatar').textContent = sala.nombre.charAt(0).toUpperCase();
  
      // Obtener nombre del creador si está embebido o como texto plano
      document.getElementById('sala-creador').textContent = sala.creador_nombre || sala.creador_id;
  
      document.getElementById('btn-unirse').onclick = async () => {
        try {
          const unirseResponse = await fetch('/salas/unirse', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ sala_id: salaId })
          });
  
          const resultado = await unirseResponse.json();
          if (unirseResponse.ok) {
            console.log("✅ Unión a sala exitosa");
            window.location.href = `/static/chat.html?room_id=${salaId}`;
          } else {
            alert(resultado.detail || 'Error al unirse a la sala');
          }
        } catch (e) {
          console.error("❌ Error al unirse:", e);
          alert("Error al unirse a la sala");
        }
      };
  
    } catch (error) {
      console.error("❌ Error al cargar detalles de la sala:", error);
      alert("Error al cargar los datos de la sala");
    }
  });
  