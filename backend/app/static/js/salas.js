// ✅ Obtener token y usuario desde sessionStorage
const token = sessionStorage.getItem('token');
const usuario = JSON.parse(sessionStorage.getItem('usuario'));

if (!token || !usuario) {
  alert("No estás autenticado .");
  window.location.href = "/auth/login";
}



document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Usuario desde sessionStorage:", usuario);
  mostrarDatosUsuario(usuario);

  document.getElementById("cerrarSesionBtn").addEventListener("click", () => {
    sessionStorage.clear();
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

  // Mini info en la barra superior
  const miniInfo = document.getElementById("usuarioActivo");
  miniInfo.innerHTML = `
    <div class="user-avatar-mini">${nombreMostrar.charAt(0).toUpperCase()}</div>
    <span>${nombreMostrar}</span>
  `;

  // Información completa en el sidebar
  document.getElementById("user-avatar").textContent = nombreMostrar.charAt(0).toUpperCase();
  document.getElementById("user-name").textContent = nombreMostrar;
  document.getElementById("user-email").textContent = usuario.email || "No disponible";

  // Formatear fechas con hora local
  const fechaRegistro = formatDate(usuario.fecha_registro);
  const ultimoAcceso = formatDate(new Date().toISOString());

  document.getElementById("user-member-since").innerHTML = `
    <span>Miembro desde</span>
    <strong>${fechaRegistro}</strong>
  `;
  
  document.getElementById("user-last-access").innerHTML = `
    <span>Último acceso</span>
    <strong>${ultimoAcceso}</strong>
  `;
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
function formatearSegundos(segundos) {
  if (segundos === null || segundos === undefined) return "Permanente";
  const min = Math.floor(segundos / 60);
  const seg = segundos % 60;
  return `${min} min ${seg} seg`;
}

// ✅ Mostrar salas propias
function mostrarMisSalas(salas) {
  const contenedor = document.getElementById("mis-salas");
  contenedor.innerHTML = "";

  if (!salas || salas.length === 0) {
    contenedor.innerHTML = `
      <div class="no-salas">
        <p>No tienes salas propias aún</p>
        <p>¡Crea una nueva sala o únete a una existente!</p>
      </div>
    `;
    return;
  }

  salas.forEach(sala => {
    const div = document.createElement("div");
    div.className = "sala";

    const tiempoId = `tiempo-mis-${sala.id}`;
    const esCreador = sala.creador_id === usuario.id;

    div.innerHTML = `
      <strong>${sala.nombre}</strong>
      <p>${sala.descripcion || "Sin descripción"}</p>

      <div class="sala-meta">
        <span>${esCreador ? "Creador" : "Miembro"}</span>
        <span>Tiempo restante: <span id="${tiempoId}">Cargando...</span></span>
        ${sala.es_publica ? '<span>Pública</span>' : '<span>Privada</span>'}
      </div>

      <div class="sala-acciones">
        <button class="btn-entrar" onclick="entrarSala('${sala.id}')">
          Entrar al chat
        </button>
        ${esCreador ? 
          `<button class="btn-eliminar" onclick="eliminarSala('${sala.id}')">
            Eliminar sala
          </button>` : 
          ''
        }
      </div>
    `;

    contenedor.appendChild(div);

    // Iniciar cuenta regresiva
    const tiempoEl = document.getElementById(tiempoId);
    iniciarCuentaRegresivaElemento(sala.tiempo_restante, tiempoEl);
    if (sala.tiempo_restante < 60 && sala.tiempo_restante > 0) {
      const alerta = document.createElement("div");
      alerta.textContent = "⚠️ Sala expirando pronto";
      alerta.style.color = "orange";
      alerta.style.fontWeight = "bold";
      alerta.style.marginTop = "4px";
      div.appendChild(alerta);
    }
    
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

    const tiempoId = `tiempo-popular-${sala.id}`;

    div.innerHTML = `
      <strong>${sala.nombre}</strong>
      <p>${sala.descripcion || "Sin descripción"}</p>
      <p>${sala.es_publica === "1" ? "Pública" : "Privada"}</p>
      <p>Tiempo restante: <span id="${tiempoId}">Cargando...</span></p>

      <button onclick="unirseSala('${sala.id}')">Unirse</button>
      <button onclick="window.location.href='/static/datosala.html?id=${sala.id}'" class="btn-ver">Ver detalles</button>
    `;

    contenedor.appendChild(div);

    // Iniciar cuenta regresiva
    const tiempoEl = document.getElementById(tiempoId);
    iniciarCuentaRegresivaElemento(sala.tiempo_restante, tiempoEl);
  });
}


// ✅ Entrar a una sala
function entrarSala(salaId) {
  window.location.href = `/static/chat.html?room_id=${salaId}`;
}

// ✅ Unirse a una sala
async function unirseSala(salaId) {
  let password = null;
  // vemos si es privada
  const salaRes = await fetch(`${API_URL}/salas/detalles/${salaId}`, { headers: authHeaders });
  const sala = await salaRes.json();
  if (!sala.es_publica) {
    password = prompt("Esta sala es privada. Ingresa la contraseña:");
    if (!password) return alert("No se proporcionó una contraseña.");
  }
  try {
    const res = await fetch(`${API_URL}/salas/unirse`, {
      method: "POST",
      headers: postHeaders,
      body: JSON.stringify({ sala_id: salaId, password })
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
  const url = `${API_URL}/salas/eliminar`;
  console.log("🛰️ Enviando solicitud a:", url); // 🛑 Depuración
  try {
    const res = await fetch(url, {
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
  const password = document.getElementById("passwordSala").value.trim();
  const tiempo_vida = document.getElementById("tiempo_vida").value;

  if (!nombre.trim()) return alert("El nombre es obligatorio");
  try {
    const body = {
      nombre,
      descripcion,
      password,
      tiempo_vida
    };
    const res = await fetch(`${API_URL}/salas/create`, {
      method: "POST",
      headers: postHeaders,
      body: JSON.stringify(body)
    });
    

    const data = await res.json();
    if (res.ok) {
      // alert("Sala creada con éxito");
      cargarSalas();
      // Limpieza del formulario
      document.getElementById("nombreSala").value = "";
      document.getElementById("descripcionSala").value = "";
      document.getElementById("passwordSala").value = "";
      document.getElementById("tiempo_vida").value = "";
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



function iniciarCuentaRegresivaElemento(segundos, elemento) {
  function formatearSegundos(segundos) {
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segundosRestantes = segundos % 60;
    return `${horas}h ${minutos}m ${segundosRestantes}s`;
  }

  if (segundos === null || segundos === -1 || segundos === undefined) {
    elemento.textContent = "Permanente";
    return;
  }

  elemento.textContent = formatearSegundos(segundos);

  const intervalo = setInterval(() => {
    segundos--;
    if (segundos <= 0) {
      clearInterval(intervalo);
      elemento.textContent = "Expirada";
    } else {
      elemento.textContent = formatearSegundos(segundos);
    }
  }, 1000);
}
