// ✅ Obtener token y usuario desde localStorage
const token = localStorage.getItem('token');
const usuario = JSON.parse(localStorage.getItem('usuario'));

if (!token || !usuario) {
  alert("No estás autenticado.");
  window.location.href = "/auth/login";
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Usuario desde localStorage:", usuario);
  mostrarDatosUsuario(usuario);

  document.getElementById("cerrarSesionBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/auth/login";
  });

  cargarSalas();
});

const authHeaders = {
  Authorization: `Bearer ${token}`
};

const postHeaders = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
};

const API_URL = `${window.location.origin}`;

// ✅ Mostrar información del usuario visualmente
function mostrarDatosUsuario(usuario) {
  console.log("👤 Usuario decodificado:", usuario);

  const nombreMostrar = usuario.nombre && usuario.surname
    ? `${usuario.nombre} ${usuario.surname}`
    : usuario.username || "Usuario";

  document.getElementById("usuarioActivo").textContent = nombreMostrar;
  document.getElementById("user-avatar").textContent = nombreMostrar.charAt(0).toUpperCase();
  document.getElementById("user-name").textContent = nombreMostrar;
  document.getElementById("user-email").textContent = usuario.email || "No disponible";
  document.getElementById("user-member-since").textContent =
    `Miembro desde: ${formatDate(usuario.fecha_registro)}`;
  document.getElementById("user-last-access").textContent =
    `Último acceso: ${formatDate(new Date().toISOString())}`;
}

// ✅ Cargar salas
async function cargarSalas() {
  try {
    const [misRes, randomRes] = await Promise.all([
      fetch(`${API_URL}/salas/mias`, { headers: authHeaders }),
      fetch(`${API_URL}/salas/salasrandom`, { headers: authHeaders })
    ]);

    const misResData = await misRes.json();
    const randomResData = await randomRes.json();

    mostrarMisSalas(misResData.salas);
    mostrarSalasPopulares(randomResData.salas, misResData.salas);
  } catch (error) {
    console.error("❌ Error al cargar salas:", error);
  }
}

// ✅ Mostrar salas propias
function mostrarMisSalas(salas) {
  const contenedor = document.getElementById("mis-salas");
  contenedor.innerHTML = "";
  if (!salas || salas.length === 0) {
    contenedor.innerHTML = "<p>No tienes salas propias aún</p>";
    return;
  }
  salas.forEach(sala => {
    const div = document.createElement("div");
    div.className = "sala";
    div.innerHTML = `
      <strong>${sala.nombre}</strong>
      <p>${sala.descripcion || "Sin descripción"}</p>
      <p>Tiempo de vida: ${sala.tiempo_vida} horas</p>
      <button onclick="entrarSala('${sala.id}')">Entrar</button>
      ${sala.creador_id === usuario.id ? 
        `<button onclick="eliminarSala('${sala.id}')">Eliminar</button>` : 
        ''
      }
    `;
    contenedor.appendChild(div);
  });
}

// ✅ Mostrar salas populares
function mostrarSalasPopulares(salas, salasPropias) {
  const contenedor = document.getElementById("salas-random");
  contenedor.innerHTML = "";
  if (!salas || salas.length === 0) {
    contenedor.innerHTML = "<p>No hay salas populares disponibles</p>";
    return;
  }

  const salasFiltradas = salas.filter(sala => 
    !salasPropias.some(s => s.id === sala.id)
  );

  salasFiltradas.forEach(sala => {
    const div = document.createElement("div");
    div.className = "sala";
    div.innerHTML = `
      <strong>${sala.nombre}</strong>
      <p>${sala.descripcion || "Sin descripción"}</p>
      <p>${sala.es_publica === "1" ? "Pública" : "Privada"}</p>
      <button onclick="unirseSala('${sala.id}')">Unirse</button>
      <button onclick="verSala('${sala.id}')">Ver</button>
    `;
    contenedor.appendChild(div);
  });
}

// ✅ Entrar a una sala
function entrarSala(salaId) {
  window.location.href = `/static/chat.html?room_id=${salaId}`;
}

// ✅ Unirse a una sala
async function unirseSala(salaId) {
  try {
    const res = await fetch(`${API_URL}/salas/unirse`, {
      method: "POST",
      headers: postHeaders,
      body: JSON.stringify({ sala_id: salaId })
    });
    const data = await res.json();
    if (res.ok) {
      entrarSala(salaId);
      cargarSalas();
    } else {
      alert("Error al unirse: " + data.detail);
    }
  } catch (e) {
    console.error("❌ Error al unirse a sala:", e);
  }
}

// ✅ Ver detalles de una sala
function verSala(salaId) {
  window.location.href = `/salas/${salaId}`;
}

// ✅ Eliminar una sala propia
async function eliminarSala(salaId) {
  try {
    const res = await fetch(`${API_URL}/salas/expulsar`, {
      method: "POST",
      headers: postHeaders,
      body: JSON.stringify({ sala_id: salaId })
    });
    const data = await res.json();
    if (res.ok) {
      alert("Sala eliminada");
      cargarSalas();
    } else {
      alert("Error: " + data.detail);
    }
  } catch (e) {
    console.error("❌ Error al eliminar sala:", e);
  }
}

// ✅ Crear nueva sala
document.getElementById("btnCrearSala").addEventListener("click", async () => {
  const nombre = document.getElementById("nombreSala").value;
  const descripcion = document.getElementById("descripcionSala").value;

  if (!nombre.trim()) return alert("El nombre es obligatorio");

  try {
    const res = await fetch(`${API_URL}/salas/create`, {
      method: "POST",
      headers: postHeaders,
      body: JSON.stringify({ nombre, descripcion })
    });

    const data = await res.json();
    if (res.ok) {
      alert("Sala creada con éxito");
      cargarSalas();
    } else {
      alert("Error: " + data.detail);
    }
  } catch (e) {
    console.error("❌ Error al crear sala:", e);
  }
});

// ✅ Formateo de fechas
function formatDate(dateString) {
  try {
    if (!dateString) return "No disponible";
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    console.error("Error formateando fecha:", e);
    return dateString;
  }
}
