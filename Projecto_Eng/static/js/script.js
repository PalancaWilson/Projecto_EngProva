
document.addEventListener("DOMContentLoaded", () => {
  // LOGIN
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(loginForm);

      fetch("http://localhost:5000/login", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((res) => {
          alert(res.mensagem);
          if (res.status === "sucesso") {
            localStorage.setItem("token", res.token);
            window.location.href = "dashboard.html";
          }
        })
        .catch((error) => {
          console.error("Erro ao fazer login:", error);
          alert("Erro ao fazer login.");
        });
    });
  }

  // DASHBOARD (exemplo)
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("token");
      window.location.href = "index.html";
    });
  }

  // HISTÓRICO DE ACESSOS
  const tbody = document.getElementById("acessosTableBody");
  const campoBusca = document.querySelector("input[placeholder*='matrícula']");

  if (!tbody) {
    console.warn("Elemento 'acessosTableBody' não encontrado.");
    return;
  }

  function carregarAcessos(filtro = "") {
    let url = "http://127.0.0.1:5000/api/historico";
    if (filtro) url += "?" + filtro;

    fetch(url)
      .then(response => response.json())
      .then(dados => {
        tbody.innerHTML = "";

        if (!Array.isArray(dados) || dados.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="6" class="text-center text-gray-500 py-4">Nenhum acesso encontrado.</td>
            </tr>`;
          return;
        }

        dados.forEach(acesso => {
          const tr = document.createElement("tr");
          tr.classList.add("bg-gray-50", "rounded-lg");

          const statusClass = acesso.estado === 'Autorizado' ? 'text-green-600' : 'text-red-600';

          tr.innerHTML = `
            <td class="px-4 py-2">${acesso.data_acesso}</td>
            <td class="px-4 py-2">${acesso.hora_acesso}</td>
            <td class="px-4 py-2">${acesso.tipo_usuario}</td>
            <td class="px-4 py-2">${acesso.matricula}</td>
            <td class="px-4 py-2">
              <span class="${statusClass} font-semibold">${acesso.estado}</span>
            </td>
            <td class="px-4 py-2 text-center">
              <span class="material-symbols-outlined cursor-pointer text-gray-600 hover:text-gray-900">download</span>
            </td>
          `;
          tbody.appendChild(tr);
        });
      })
      .catch(error => {
        console.error("Erro ao carregar acessos:", error);
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center text-red-500 py-4">Erro ao carregar acessos.</td>
          </tr>`;
      });
  }

  if (campoBusca) {
    campoBusca.addEventListener("input", () => {
      const valor = campoBusca.value.trim();
      carregarAcessos(valor ? "busca=" + encodeURIComponent(valor) : "");
    });
  }

  carregarAcessos();

  // FORMULÁRIO DE CADASTRO DE VEÍCULO
  const formVeiculo = document.getElementById("formCadastroVeiculo");
  const selectTipoUsuario = document.getElementById("tipo_usuario");

  if (selectTipoUsuario) {
    fetch("http://localhost:5000/frequentadores")
      .then((res) => res.json())
      .then((data) => {
        const tiposUnicos = new Set();
        data.forEach((f) => {
          if (!tiposUnicos.has(f.tipo)) {
            const option = document.createElement("option");
            option.value = f.tipo;
            option.textContent = f.tipo;
            selectTipoUsuario.appendChild(option);
            tiposUnicos.add(f.tipo);
          }
        });
      })
      .catch((err) => {
        console.error("Erro ao carregar frequentadores:", err);
        alert("Não foi possível carregar os tipos de usuário.");
      });
  }

  if (formVeiculo) {
    formVeiculo.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(formVeiculo);
      const matricula = formData.get("matricula");
      const proprietario = formData.get("proprietario");
      const tipo_usuario = formData.get("tipo_usuario");

      const nomeValido = /^[A-Za-zÀ-ÿ\s]+$/.test(proprietario);
      if (!nomeValido) {
        alert("O nome do proprietário deve conter apenas letras.");
        return;
      }

      const padraoMatricula = /^[A-Z]{2}-\d{2}-\d{2}-[A-Z]{2}$/;
      if (!padraoMatricula.test(matricula)) {
        alert("A matrícula deve estar no formato LD-48-17-HO.");
        return;
      }

      if (!matricula || !proprietario || !tipo_usuario) {
        alert("Preencha todos os campos obrigatórios.");
        return;
      }

      fetch("http://localhost:5000/cadastrar-veiculo", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((res) => {
          alert(res.mensagem);
          if (res.status === "sucesso") {
            formVeiculo.reset();
          }
        })
        .catch((error) => {
          console.error("Erro ao cadastrar veículo:", error);
          alert("Erro ao cadastrar veículo.");
        });
    });
  }
});


document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.getElementById("acessosTableBody");
  const campoBusca = document.querySelector("input[placeholder*='matrícula']");

  if (!tbody) {
    console.warn("Elemento 'acessosTableBody' não encontrado.");
    return;
  }

  function carregarAcessos(filtro = "") {
    let url = "http://127.0.0.1:5000/api/historico";
    if (filtro) url += "?" + filtro;

    fetch(url)
      .then(response => response.json())
      .then(dados => {
        tbody.innerHTML = "";

        if (!Array.isArray(dados) || dados.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="6" class="text-center text-gray-500 py-4">Nenhum acesso encontrado.</td>
            </tr>`;
          return;
        }

        dados.forEach(acesso => {
          const tr = document.createElement("tr");
          tr.classList.add("bg-gray-50", "rounded-lg");

          const statusClass = acesso.estado === 'Autorizado' ? 'text-green-600' : 'text-red-600';

          tr.innerHTML = `
            <td class="px-4 py-2">${acesso.data_acesso}</td>
            <td class="px-4 py-2">${acesso.hora_acesso}</td>
            <td class="px-4 py-2">${acesso.tipo_usuario}</td>
            <td class="px-4 py-2">${acesso.matricula}</td>
            <td class="px-4 py-2">
              <span class="${statusClass} font-semibold">${acesso.estado}</span>
            </td>
            <td class="px-4 py-2 text-center">
              <span class="material-symbols-outlined cursor-pointer text-gray-600 hover:text-gray-900">download</span>
            </td>
          `;
          tbody.appendChild(tr);
        });
      })
      .catch(error => {
        console.error("Erro ao carregar acessos:", error);
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center text-red-500 py-4">Erro ao carregar acessos.</td>
          </tr>`;
      });
  }

  if (campoBusca) {
    campoBusca.addEventListener("input", () => {
      const valor = campoBusca.value.trim();
      carregarAcessos(valor ? "busca=" + encodeURIComponent(valor) : "");
    });
  }

  carregarAcessos();
});
