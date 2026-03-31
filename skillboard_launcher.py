"""
SkillBoard — Lanceur client
Ouvre l'application dans une fenêtre navigateur native.
Le serveur Flask tourne sur Docker (réseau local ou cloud).
"""
import webview
import json
import os
import sys
import time
import urllib.request
import urllib.error


# ============================================================
# CHEMIN DE BASE — robuste sur Mac (.app) et Windows (.exe)
# ============================================================

if getattr(sys, 'frozen', False):
    # Mode compilé — l'exécutable est dans Contents/MacOS/ sur Mac
    # ou directement dans le dossier sur Windows
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Mode développement — même dossier que ce script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "skillboard.config.json")


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_CONFIG = {
    "server_url": "http://localhost:5001",
    "app_title": "SkillBoard",
    "window_width": 1280,
    "window_height": 800,
}


def load_config():
    """Charge la configuration depuis skillboard.config.json"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {**DEFAULT_CONFIG, **cfg}
        except Exception:
            pass
    return DEFAULT_CONFIG


def save_default_config():
    """Crée un fichier de config par défaut si absent"""
    if not os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# ============================================================
# VÉRIFICATION DU SERVEUR
# ============================================================

def wait_for_server(url, timeout=10):
    """
    Attend que le serveur soit disponible.
    Retourne True si le serveur répond, False après timeout.
    """
    health_url = f"{url.rstrip('/')}/login"
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.urlopen(health_url, timeout=2)
            if req.status in (200, 302):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def show_error_page(server_url):
    """Retourne une page HTML d'erreur claire pour l'utilisateur final"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>SkillBoard — Connexion impossible</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: linear-gradient(135deg, #c065e8 0%, #8e3db5 100%);
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 48px;
            max-width: 500px;
            width: 90%;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{ color: #8e3db5; margin-bottom: 16px; font-size: 1.8rem; }}
        p {{ color: #555; line-height: 1.6; margin-bottom: 12px; }}
        .url {{
            font-family: monospace;
            background: #f5f5f5;
            border: 1px solid #ddd;
            padding: 10px 20px;
            border-radius: 8px;
            color: #333;
            display: inline-block;
            margin: 12px 0;
            font-size: 1rem;
        }}
        .hint {{
            font-size: 0.85rem;
            color: #aaa;
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Connexion impossible</h1>
        <p>SkillBoard ne peut pas joindre le serveur.</p>
        <div class="url">{server_url}</div>
        <p>Vérifiez que le serveur est démarré et que vous êtes bien connecté au réseau.</p>
        <p class="hint">
            Contactez votre administrateur réseau si le problème persiste.
        </p>
    </div>
</body>
</html>"""


# ============================================================
# POINT D'ENTRÉE
# ============================================================

def main():
    save_default_config()
    config = load_config()

    server_url = config["server_url"].rstrip("/")
    title      = config["app_title"]
    width      = config["window_width"]
    height     = config["window_height"]

    server_ok = wait_for_server(server_url, timeout=10)

    if server_ok:
        window = webview.create_window(
            title=title,
            url=server_url,
            width=width,
            height=height,
            min_size=(900, 600),
            resizable=True,
            text_select=True,
        )
    else:
        window = webview.create_window(
            title=f"{title} — Connexion impossible",
            html=show_error_page(server_url),
            width=600,
            height=480,
            resizable=False,
        )

    webview.start(debug=False)


if __name__ == "__main__":
    main()