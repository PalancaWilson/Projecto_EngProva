document.addEventListener("DOMContentLoaded", () => {
  const formVeiculo = document.getElementById("formCadastroVeiculo");
  const inputIdFrequentador = document.getElementById("id_frequentador");
  const selectTipoUsuario = document.getElementById("tipo_usuario");

  // 🔍 Quando o id_frequentador mudar, buscar tipo do usuário
  if (inputIdFrequentador) {
    inputIdFrequentador.addEventListener("blur", () => {
      const idFrequentador = inputIdFrequentador.value.trim();

      if (idFrequentador === "") return;

      fetch(`http://localhost:5000/api/frequentador/${idFrequentador}`)
        .then(r => {
          if (!r.ok) throw new Error("Frequentador não encontrado");
          return r.json();
        })
        .then(d => {
          selectTipoUsuario.value = d.tipo;
        })
        .catch(err => {
          alert("Frequentador não encontrado ou erro na consulta.");
          selectTipoUsuario.value = "";
        });
    });
  }

  // Envio do formulário (continua igual ao seu, incluindo validações)
  if (formVeiculo) {
    formVeiculo.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(formVeiculo);

      // Validações continuam aqui...

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

