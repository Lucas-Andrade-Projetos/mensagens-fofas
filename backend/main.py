from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid
from dotenv import load_dotenv
from pathlib import Path
import smtplib
import ssl
import json
import os

# Carrega variáveis de ambiente
load_dotenv()
EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")
SENHA_APP = os.getenv("SENHA_APP")

# Caminhos
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
PENSAMENTO_FILE = BASE_DIR / "pensamento.json"
MENSAGENS_FILE = BASE_DIR / "mensagens.json"

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory=(FRONTEND_DIR / "static").resolve()), name="static")

# WebSocket
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        data = get_pensamento_data()
        await websocket.send_json({"type": "pensamento", "value": data["count"]})
        if MENSAGENS_FILE.exists():
            with open(MENSAGENS_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if historico:
                    await websocket.send_json({"type": "mensagem", "value": historico[-1]})
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        clients.remove(websocket)

# Rotas HTML
@app.get("/")
async def index():
    return FileResponse((FRONTEND_DIR / "index.html").resolve(strict=True))

@app.get("/home.html")
async def home():
    return FileResponse((FRONTEND_DIR / "home.html").resolve(strict=True))

@app.get("/admin.html")
async def admin():
    return FileResponse((FRONTEND_DIR / "admin.html").resolve(strict=True))

# Pensamento: leitura e atualização
def get_pensamento_data():
    if PENSAMENTO_FILE.exists():
        with open(PENSAMENTO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"date": str(datetime.now().date()), "count": 0}
    if data["date"] != str(datetime.now().date()):
        data = {"date": str(datetime.now().date()), "count": 0}
        with open(PENSAMENTO_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    return data

def update_pensamento():
    data = get_pensamento_data()
    data["count"] += 1
    data["date"] = str(datetime.now().date())
    with open(PENSAMENTO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data["count"]

@app.post("/pensar")
async def pensar_nela():
    count = update_pensamento()
    for client in clients:
        await client.send_json({"type": "pensamento", "value": count})
    return {"status": "ok", "count": count}

@app.post("/enviar-mensagem")
async def enviar_mensagem(msg: dict):
    texto = msg.get("mensagem", "")
    if not texto:
        return {"status": "erro", "motivo": "mensagem vazia"}

    historico = []
    if MENSAGENS_FILE.exists():
        with open(MENSAGENS_FILE, "r", encoding="utf-8") as f:
            historico = json.load(f)

    historico.append(texto)
    with open(MENSAGENS_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

    for client in clients:
        await client.send_json({"type": "mensagem", "value": texto})
    return {"status": "ok"}

@app.post("/enviar-email")
async def enviar_email():
    try:
        msg = EmailMessage()
        msg["Subject"] = "Um carinho digital 💌"
        msg["From"] = EMAIL_ORIGEM
        msg["To"] = EMAIL_DESTINO

        cid = make_msgid()

        html = f"""
        <html>
          <body style="text-align: center; font-family: sans-serif;">
            <h2>💖 Você recebeu um carinho especial 💖</h2>
            <p>Espero que seu dia fique mais doce com essa imagem fofa:</p>
            <img src="cid:{cid[1:-1]}" style="width: 300px; border-radius: 12px;">
          </body>
        </html>
        """

        msg.set_content("Você recebeu um carinho especial 💌 (veja o e-mail em modo HTML).")
        msg.add_alternative(html, subtype="html")

        with open(BASE_DIR / "fofura.jpg", "rb") as img:
            img_data = img.read()
            msg.get_payload()[1].add_related(img_data, "image", "jpeg", cid=cid)

        contexto = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
            smtp.login(EMAIL_ORIGEM, SENHA_APP)
            smtp.send_message(msg)

        return {"status": "ok", "mensagem": "Email enviado com sucesso!"}
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}
