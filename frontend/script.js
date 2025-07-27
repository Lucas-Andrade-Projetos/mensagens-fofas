// === Mensagens fofas ===
const mensagens = [
  "Você é a coisa mais linda do meu mundo 🌸",
  "Seu sorriso vale meu dia inteiro 😊",
  "Penso em você o tempo todo 💭❤️",
  "Queria te dar um abraço agora mesmo 🤗",
  "Você é meu lugar seguro 🏡💕"
];

// === Elementos principais ===
const btnMensagem = document.getElementById("mensagemBtn");
const elMensagem = document.getElementById("mensagem");
const elContador = document.getElementById("contador");
const elCoracao = document.getElementById("coracao");

// === Funções principais ===

function mostrarMensagemAleatoria() {
  const index = Math.floor(Math.random() * mensagens.length);
  elMensagem.innerText = mensagens[index];
}

function atualizarMensagem(mensagem) {
  elMensagem.innerText = mensagem;
}

function atualizarPensamento(valor) {
  elContador.innerText = valor;

  if (valor > 0) {
    const intensidade = Math.min(valor, 20);
    const duracao = Math.max(0.2, 1 - intensidade * 0.03);
    const brilho = 1 + intensidade * 0.05;

    elCoracao.style.animation = `bater ${duracao}s infinite ease-in-out`;
    elCoracao.style.filter = `brightness(${brilho})`;
  } else {
    elCoracao.style.animation = "none";
    elCoracao.style.filter = "brightness(1)";
  }
}

function iniciarWebSocket() {
  const socket = new WebSocket("ws://localhost:8000/ws");

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === "mensagem") {
        atualizarMensagem(data.value);
      } else if (data.type === "pensamento") {
        atualizarPensamento(parseInt(data.value));
      }
    } catch (e) {
      console.error("Erro ao interpretar mensagem WebSocket:", e);
    }
  };

  socket.onerror = () => {
    console.error("Erro de conexão WebSocket");
  };
}

function iniciarCanvasParticulas() {
  const canvas = document.getElementById("matrixCanvas");
  if (!canvas) return;

  function ajustarCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  window.addEventListener("resize", ajustarCanvas);
  ajustarCanvas();
}

function iniciarEstrelas() {
  const container = document.getElementById("particulas");
  if (!container) return;

  for (let i = 0; i < 40; i++) {
    const estrela = document.createElement("div");
    estrela.className = "estrela";
    estrela.style.left = `${Math.random() * 100}%`;
    estrela.style.top = `${Math.random() * 100}%`;
    estrela.style.animationDelay = `${Math.random() * 6}s`;
    container.appendChild(estrela);
  }
}

// === Inicialização ===
function iniciar() {
  btnMensagem.addEventListener("click", mostrarMensagemAleatoria);
  iniciarWebSocket();
  iniciarCanvasParticulas();
  iniciarEstrelas();
}

document.addEventListener("DOMContentLoaded", iniciar);
