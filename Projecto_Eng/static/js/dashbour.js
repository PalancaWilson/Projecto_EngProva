document.addEventListener('DOMContentLoaded', () => {

  // --- DASHBOARD ---
  if (document.getElementById("totalVeiculos")) {

    // Dados principais do dashboard
    fetch("http://127.0.0.1:5000/dashboardAdmin-data")
      .then(r => r.json())
      .then(d => {
        document.getElementById("totalVeiculos").textContent = d.total_veiculos;
        document.getElementById("tentativasNegadas").textContent = d.recusados;
        document.getElementById("acessosDia").textContent = d.acessos_dia;
        document.getElementById("pendencias").textContent = d.pendentes;
      })
      .catch(err => {
        console.error("Erro ao carregar dados do dashboard:", err);
      });

    // Tabela de últimos acessos
    fetch("http://127.0.0.1:5000/ultimos-acessos")
      .then(res => res.json())
      .then(acessos => {
        const tbody = document.getElementById("tabela-acessos");
        tbody.innerHTML = "";

        acessos.forEach(acesso => {
          const linha = document.createElement("tr");

          linha.innerHTML = `
            <td class="py-2">${acesso.hora}</td>
            <td>${acesso.matricula}</td>
            <td>
              <span class="${acesso.estado === 'Autorizado' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'} text-xs px-2 py-1 rounded">
                ${acesso.estado}
              </span>
            </td>
          `;

          tbody.appendChild(linha);
        });
      })
      .catch(err => {
        console.error("Erro ao carregar últimos acessos:", err);
      });

    // Gráfico de acessos por hora
    fetch("http://127.0.0.1:5000/grafico-acessos")
      .then(res => res.json())
      .then(dados => {
        const ctx = document.getElementById("grafico-acessos").getContext("2d");
        const labels = dados.map(d => `${d.hora}:00`);
        const valores = dados.map(d => d.total);

        new Chart(ctx, {
          type: "line",
          data: {
            labels: labels,
            datasets: [{
              label: "Acessos por Hora",
              data: valores,
              fill: true,
              borderColor: "#3a5af7",
              backgroundColor: "rgba(58, 90, 247, 0.1)",
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      })
      .catch(err => {
        console.error("Erro ao carregar gráfico de acessos:", err);
      });

  }

});



   // --- LOGOUT ---
  const logoutBtn = document.getElementById("logout");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      if (confirm("Deseja realmente sair?")) {
        sessionStorage.clear();
        window.location.href = "../template/index.html";
      }
    });
}