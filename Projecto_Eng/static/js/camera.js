document.addEventListener("DOMContentLoaded", () => {
  const btnAtivarCamera = document.getElementById("btn-ativar-camera");
  const btnCapturar = document.getElementById("btn-capturar");
  const video = document.getElementById("camera-video");
  const canvas = document.getElementById("canvas-preview");
  const ctx = canvas?.getContext("2d");

  const loader = document.getElementById("loader");
  const resultado = document.getElementById("resultado-analise");
  const imgCapturada = document.getElementById("imagem-capturada");
  const spanMatricula = document.getElementById("matricula-analisada");
  const spanEstado = document.getElementById("estado-analisado");
  const msgOverlay = document.getElementById("mensagem-acesso");
  const overlay = document.getElementById("overlay-acesso");

  if (!btnAtivarCamera || !btnCapturar || !video || !canvas || !ctx) {
    console.error("❌ Elementos do DOM não encontrados. Verifique IDs no HTML.");
    return;
  }

  btnAtivarCamera.onclick = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      btnCapturar.classList.remove("hidden");
    } catch (err) {
      alert("Erro ao acessar a câmera.");
      console.error("❌ Erro ao iniciar câmera:", err);
    }
  };

  btnCapturar.onclick = () => {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.classList.remove("hidden");

    canvas.toBlob((blob) => {
      if (!blob) {
        alert("Erro ao gerar imagem.");
        return;
      }

      const formData = new FormData();
      formData.append("imagem", blob, "captura.jpg");

      loader?.classList.remove("hidden");

      fetch("http://127.0.0.1:5000/api/analisar-imagem", {
        method: "POST",
        body: formData,
      })
        .then(async (res) => {
          const texto = await res.text(); // Lê como texto primeiro
          console.log("📦 Resposta bruta do servidor:", texto);

          loader?.classList.add("hidden");

          if (!res.ok) throw new Error(`Erro HTTP ${res.status}`);

          let data;
          try {
            data = JSON.parse(texto);
          } catch (e) {
            throw new Error("❌ JSON inválido. Verifique a resposta do servidor.");
          }

          resultado?.classList.remove("hidden");
          imgCapturada.src = canvas.toDataURL();
          spanMatricula.innerText = data.matricula || "Não reconhecida";

          const permitido = data.status === "permitido";

          spanEstado.innerText = data.mensagem || (permitido ? "✅ Acesso Liberado" : "❌ Acesso Negado");
          spanEstado.className = permitido
            ? "text-green-600 font-semibold"
            : "text-red-600 font-semibold";

          msgOverlay.innerText = permitido ? "✅ Acesso Liberado" : "❌ Acesso Negado";
          msgOverlay.className = permitido
            ? "bg-green-600 text-white text-3xl font-bold px-10 py-6 rounded-xl shadow-lg"
            : "bg-red-600 text-white text-3xl font-bold px-10 py-6 rounded-xl shadow-lg";

          overlay.classList.remove("hidden");
          setTimeout(() => {
            overlay.classList.add("hidden");
          }, 3000);
        })
        .catch((error) => {
          loader?.classList.add("hidden");
          console.error("❌ Erro ao processar resposta da API:", error.message);
          alert("Erro ao processar imagem ou interpretar resposta.");
        });
    }, "image/jpeg");
  };
});
