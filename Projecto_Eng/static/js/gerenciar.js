document.addEventListener('DOMContentLoaded', () => {
  const tabela = document.getElementById("acessosTableBody");

  // Carregar os acessos ao carregar a página
  carregarAcessos();

  // Função para carregar acessos
  function carregarAcessos() {
    fetch("http://localhost:5000/api/historico")
      .then(res => res.json())
      .then(acessos => {
        tabela.innerHTML = "";

        acessos.forEach(acesso => {
          const linha = document.createElement("tr");

          linha.innerHTML = `
            <td class="px-4 py-2">${acesso.matricula}</td>
            <td class="px-4 py-2">${acesso.data_acesso || '---'}</td>
            <td class="px-4 py-2">${acesso.tipo_usuario}</td>
            <td class="px-4 py-2">${acesso.estado}</td>
            <td class="px-4 py-2">
              <button class="text-red-600 hover:underline" data-matricula="${acesso.matricula}">
                Remover
              </button>
            </td>
          `;

          tabela.appendChild(linha);
        });

        // Adiciona evento de clique para os botões de remover
        document.querySelectorAll("button[data-matricula]").forEach(btn => {
          btn.addEventListener("click", () => {
            const matricula = btn.dataset.matricula;
            confirmarRemocao(matricula);
          });
        });
      })
      .catch(err => {
        console.error("Erro ao carregar acessos:", err);
        alert("Erro ao carregar acessos.");
      });
  }

  // Função que remove o acesso via API
  function confirmarRemocao(matricula) {
    if (!matricula) return alert("Matrícula inválida.");

    // Buscar o ID do acesso pela matrícula (requer alteração no backend se não tiver ID direto)
    fetch(`http://localhost:5000/api/historico?busca=${matricula}`)
      .then(res => res.json())
      .then(acessos => {
        if (acessos.length === 0) {
          return alert("Acesso não encontrado.");
        }

        const id_acesso = acessos[0].id_acesso;

        if (!id_acesso) {
          return alert("ID do acesso não encontrado no servidor.");
        }

        if (confirm(`Deseja realmente remover o acesso da matrícula ${matricula}?`)) {
          fetch(`http://localhost:5000/api/acessos/${id_acesso}`, {
            method: 'DELETE'
          })
            .then(res => res.json())
            .then(resp => {
              alert(resp.mensagem || "Remoção concluída.");
              carregarAcessos(); // Recarrega a lista
            })
            .catch(err => {
              console.error("Erro ao remover:", err);
              alert("Erro ao remover acesso.");
            });
        }
      })
      .catch(err => {
        console.error("Erro ao buscar acesso:", err);
        alert("Erro ao buscar acesso.");
      });
  }
});
