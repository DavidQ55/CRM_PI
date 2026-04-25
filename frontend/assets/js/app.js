let chartInstance = null;
let topChartInstance = null;
let editId = null;
const API = "";

function showScreen(screenId, clickedButton = null) {
  const user = localStorage.getItem("crm_user");

  if (!user && screenId !== "login" && screenId !== "signup") {
    alert("Debes iniciar sesión primero");
    screenId = "login";
  }

  document.querySelectorAll(".screen").forEach(screen => {
    screen.classList.remove("active");
  });

  const target = document.getElementById(screenId);
  if (target) {
    target.classList.add("active");
  }

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.remove("active");
  });

  if (clickedButton) {
    clickedButton.classList.add("active");
  }

  if (screenId === "list") loadClients();
  if (screenId === "dashboard") updateDashboard();
}

function checkLogin() {
  const user = localStorage.getItem("crm_user");

  if (!user) {
    showScreen("login");
  } else {
    const firstNavButton = document.querySelectorAll(".nav-btn")[0];
    showScreen("dashboard", firstNavButton);
  }
}

async function loginUser() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();

  if (!email || !password) {
    alert("Ingrese correo y contraseña");
    return;
  }

  try {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email,
        password
      })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Error al iniciar sesión");
    }

    localStorage.setItem("crm_user", JSON.stringify(data.user));
    alert("Bienvenido " + data.user.name);

    document.getElementById("loginEmail").value = "";
    document.getElementById("loginPassword").value = "";

    const firstNavButton = document.querySelectorAll(".nav-btn")[0];
    showScreen("dashboard", firstNavButton);
  } catch (error) {
    alert(error.message);
  }
}

async function registerUser() {
  const name = document.getElementById("userName").value.trim();
  const email = document.getElementById("userEmail").value.trim();
  const password = document.getElementById("userPassword").value.trim();

  if (!name || !email || !password) {
    alert("Todos los campos son obligatorios");
    return;
  }

  try {
    const res = await fetch(`${API}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name,
        email,
        password
      })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Error registrando usuario");
    }

    alert("Registro exitoso");

    document.getElementById("userName").value = "";
    document.getElementById("userEmail").value = "";
    document.getElementById("userPassword").value = "";

    showScreen("login");
  } catch (error) {
    alert(error.message);
  }
}

async function saveClient() {
  const user = localStorage.getItem("crm_user");
  if (!user) {
    alert("Debes iniciar sesión primero");
    showScreen("login");
    return;
  }

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const segment = document.getElementById("segment").value;
  const notes = document.getElementById("notes").value.trim();

  if (!name || !email || !phone) {
    alert("Todos los campos son obligatorios");
    return;
  }

  const data = { name, email, phone, segment, notes };

  try {
    let response;

    if (editId) {
      response = await fetch(`${API}/clients/${editId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
    } else {
      response = await fetch(`${API}/clients`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
    }

    const responseData = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(responseData.detail || "No se pudo guardar el cliente");
    }

    alert(editId ? "Cliente actualizado correctamente" : "Cliente registrado correctamente");

    editId = null;
    clearForm();
    document.getElementById("formTitle").textContent = "Registrar cliente";

    await loadClients();
    await updateDashboard();

    const listButton = document.querySelectorAll(".nav-btn")[2];
    showScreen("list", listButton);
  } catch (error) {
    console.error(error);
    alert(error.message || "Ocurrió un error al guardar el cliente");
  }
}

function editClient(id, name, email, phone, segment, notes) {
  const user = localStorage.getItem("crm_user");
  if (!user) {
    alert("Debes iniciar sesión primero");
    showScreen("login");
    return;
  }

  document.getElementById("name").value = name;
  document.getElementById("email").value = email;
  document.getElementById("phone").value = phone;
  document.getElementById("segment").value = segment;
  document.getElementById("notes").value = notes || "";

  document.getElementById("formTitle").textContent = "Editar cliente";
  editId = id;

  const registerButton = document.querySelectorAll(".nav-btn")[1];
  showScreen("register", registerButton);
}

async function deleteClient(id) {
  const user = localStorage.getItem("crm_user");
  if (!user) {
    alert("Debes iniciar sesión primero");
    showScreen("login");
    return;
  }

  if (!confirm("¿Seguro que deseas eliminar este cliente?")) return;

  try {
    const response = await fetch(`${API}/clients/${id}`, {
      method: "DELETE"
    });

    const responseData = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(responseData.detail || "No se pudo eliminar el cliente");
    }

    alert("Cliente eliminado correctamente");
    await loadClients();
    await updateDashboard();
  } catch (error) {
    console.error(error);
    alert(error.message || "Ocurrió un error al eliminar el cliente");
  }
}

function clearForm() {
  document.getElementById("name").value = "";
  document.getElementById("email").value = "";
  document.getElementById("phone").value = "";
  document.getElementById("segment").value = "General";
  document.getElementById("notes").value = "";

  editId = null;
  document.getElementById("formTitle").textContent = "Registrar cliente";
}

function clearFilters() {
  const searchInput = document.getElementById("search");
  const segmentInput = document.getElementById("filterSegment");

  if (searchInput) searchInput.value = "";
  if (segmentInput) segmentInput.value = "";

  loadClients();
}

async function changeSegment(id, newSegment) {
  const user = localStorage.getItem("crm_user");
  if (!user) {
    alert("Debes iniciar sesión primero");
    showScreen("login");
    return;
  }

  try {
    const currentRow = [...document.querySelectorAll("#table tbody tr")].find(row => {
      const editButton = row.querySelector(".edit-btn");
      return editButton && editButton.getAttribute("data-id") === String(id);
    });

    let name = "";
    let email = "";
    let phone = "";

    if (currentRow) {
      const cells = currentRow.querySelectorAll("td");
      name = cells[0]?.textContent?.trim() || "";
      email = cells[1]?.textContent?.trim() || "";
      phone = cells[2]?.textContent?.trim() || "";
    }

    const res = await fetch(`${API}/clients/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        email,
        phone,
        segment: newSegment
      })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.detail || "No se pudo actualizar el segmento");
    }

    loadClients();
  } catch (error) {
    console.error(error);
    alert(error.message || "Error actualizando segmento");
  }
}

async function loadClients() {
  const user = localStorage.getItem("crm_user");
  const tbody = document.querySelector("#table tbody");

  if (!tbody) return;

  if (!user) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center;color:#64748b;">
          Debes iniciar sesión para ver los clientes
        </td>
      </tr>
    `;
    return;
  }

  const searchInput = document.getElementById("search");
  const segmentInput = document.getElementById("filterSegment");

  const search = searchInput ? searchInput.value.trim() : "";
  const segment = segmentInput ? segmentInput.value : "";

  try {
    const res = await fetch(
      `${API}/clients?search=${encodeURIComponent(search)}&segment=${encodeURIComponent(segment)}`
    );

    if (!res.ok) {
      throw new Error("No se pudieron cargar los clientes");
    }

    const data = await res.json();
    tbody.innerHTML = "";

    if (data.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center;color:#64748b;">
            No hay clientes registrados
          </td>
        </tr>
      `;
      return;
    }

    data.forEach(c => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${escapeHtml(c.name)}</td>
        <td>${escapeHtml(c.email)}</td>
        <td>${escapeHtml(c.phone)}</td>
        <td>
          <select onchange="changeSegment(${c.id}, this.value)">
            <option value="General" ${c.segment === "General" ? "selected" : ""}>General</option>
            <option value="VIP" ${c.segment === "VIP" ? "selected" : ""}>VIP</option>
            <option value="Frecuente" ${c.segment === "Frecuente" ? "selected" : ""}>Frecuente</option>
          </select>
        </td>

        <td title="${escapeHtml(c.notes || "")}">
          ${escapeHtml((c.notes || "").slice(0, 30))}...
        </td>


        <td class="actions-cell">
          
          
          <button
            class="edit-btn"
            data-id="${c.id}"
            onclick="editClient(${c.id}, '${safeJs(c.name)}', '${safeJs(c.email)}', '${safeJs(c.phone)}', '${safeJs(c.segment)}', '${safeJs(c.notes || "")}')"
          >
            Editar
          </button>

          
          <button class="delete-btn" onclick="deleteClient(${c.id})">
            Eliminar
          </button>

          <button onclick="addPurchase(${c.id})">
            Compras
          </button>

          <button onclick="viewPurchases(${c.id})">
            Ver compras
          </button>
          
        </td>
      `;

      tbody.appendChild(tr);
    });
  } catch (error) {
    console.error(error);
    alert("Error cargando clientes");
  }
}

async function updateDashboard() {
  const scrollY = window.scrollY; // guardar scroll
  const totalElement = document.getElementById("totalClients");
  if (!totalElement) return;

  const user = localStorage.getItem("crm_user");
  if (!user) {
    totalElement.textContent = "0";
    return;
  }

  try {
    const res = await fetch(`${API}/clients`);

    if (!res.ok) {
      totalElement.textContent = "0";
      return;
    }

    const data = await res.json();

    totalElement.textContent = data.length;

    renderChart(data); // Aqui se conecta el gráfico

    const topRes = await fetch(`${API}/purchases/top`);

    if (topRes.ok) {
      const topData = await topRes.json();
      renderTopClientsChart(topData);
    } else {
      console.warn("Error cargando top clientes");
    }


  } catch (error) {
    console.error(error);
  }

  window.scrollTo(0, scrollY);

}

function safeJs(value) {
  return String(value)
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function logout() {
  localStorage.removeItem("crm_user");
  alert("Sesión cerrada correctamente");

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.remove("active");
  });

  document.getElementById("loginEmail").value = "";
  document.getElementById("loginPassword").value = "";

  showScreen("login");
}
function enterApp() {
  const welcome = document.getElementById("welcomeScreen");
  const app = document.querySelector(".app");

  welcome.style.opacity = "0";
  welcome.style.transform = "scale(1.05)";
  welcome.style.transition = "all 0.6s ease";

  setTimeout(() => {
    welcome.style.display = "none";
    app.style.display = "grid";

    app.style.opacity = "0";
    app.style.transform = "translateY(20px)";

    setTimeout(() => {
      app.style.transition = "all 0.6s ease";
      app.style.opacity = "1";
      app.style.transform = "translateY(0)";
    }, 50);

  }, 500);
}

async function addPurchase(clientId) {
  try {
    const res = await fetch(`${API}/purchases`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        client_id: clientId,
        amount: 1
      })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Error registrando compra");
    }

    loadClients(); // actualiza segmento automáticamente
    updateDashboard();
  } catch (error) {
    alert(error.message);
  }
}


async function viewPurchases(clientId) {
  try {
    const res = await fetch(`${API}/purchases/${clientId}`);

    if (!res.ok) {
      throw new Error("Error obteniendo compras");
    }

    const data = await res.json();

    const tbody = document.getElementById("purchasesTable");
    tbody.innerHTML = "";

    if (data.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="2">No hay compras</td>
        </tr>
      `;
    } else {
      data.forEach(p => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
          <td>${p.date}</td>
          <td>
            <button onclick="deletePurchase(${p.id}, ${clientId})">
              Eliminar
            </button>
          </td>
        `;

        tbody.appendChild(tr);
      });
    }

    showScreen("purchases");

  } catch (error) {
    alert(error.message);
  }
}


async function deletePurchase(purchaseId, clientId) {
  if (!confirm("¿Eliminar compra?")) return;

  try {
    const res = await fetch(`${API}/purchases/${purchaseId}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      throw new Error("Error eliminando compra");
    }

    viewPurchases(clientId); // recargar tabla
    loadClients(); // actualizar segmento
    updateDashboard();

  } catch (error) {
    alert(error.message);
  }
}

//Función para construir el gráfico
function renderChart(data) {
  const ctx = document.getElementById("clientsChart");

  if (!ctx) return;

  const segments = {
    General: 0,
    Frecuente: 0,
    VIP: 0
  };

  data.forEach(c => {
    if (segments[c.segment] !== undefined) {
      segments[c.segment]++;
    }
  });

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["General", "Frecuente", "VIP"],
      datasets: [{
        label: "Clientes por segmento",
        data: [
          segments.General,
          segments.Frecuente,
          segments.VIP
        ]
      }]
    }
  });
}

//Función Top clientes
function renderTopClientsChart(data) {
  const ctx = document.getElementById("topClientsChart");
  if (!ctx) return;

  const labels = data.map(c => c.name);
  const values = data.map(c => c.total);

  if (topChartInstance) {
    topChartInstance.destroy();
  }

  topChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Top 5 clientes con más compras",
        data: values
      }]
    }
  });
}

function exportChart(canvasId) {
  const canvas = document.getElementById(canvasId);

  const url = canvas.toDataURL("image/png");

  const a = document.createElement("a");
  a.href = url;
  a.download = `${canvasId}.png`;
  a.click();
}


checkLogin();
setInterval(() => {
  updateDashboard();
}, 5000);