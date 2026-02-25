"""
Styles et thème centralisés - Optimisation pour app_optimise.py
Extrait de app.py pour séparation des responsabilités et maintenabilité.
"""
import os
import base64
import json


# =====================
# CONSTANTES CSS
# =====================
SIDEBAR_BG_PLAIN = "background: #FAFAFA !important;"


def _load_sidebar_bg_image() -> str:
    """Charge l'image nav.png pour la sidebar (page connexion)."""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        nav_path = os.path.join(project_root, "assets", "nav.png")
        if os.path.exists(nav_path):
            with open(nav_path, "rb") as f:
                nav_b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"""
        background-image: url('data:image/png;base64,{nav_b64}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        """
    except Exception:
        pass
    return SIDEBAR_BG_PLAIN


def get_main_css() -> str:
    """Retourne le CSS principal (palette violet/bleu/beige)."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    :root {
        --violet-clair: #B19CD9;
        --bleu-turquoise: #40E0D0;
        --beige: #FEFEFE;
        --beige-fonce: #FAFAFA;
        --beige-tres-fonce: #F5F5F5;
        --blanc: #FFFFFF;
        --noir: #2C2C2C;
        --gris-fonce: #6C6C6C;
        --radius-sm: 8px;
        --radius-md: 12px;
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stApp { background: #FEFEFE !important; font-family: 'Inter', sans-serif; }
    .main .block-container { background: #FEFEFE !important; padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    [data-testid="stSidebar"] { border-right: 2px solid #F5F5F5; }
    
    .stButton > button {
        background: linear-gradient(135deg, #B19CD9 0%, #40E0D0 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover { opacity: 0.9; transform: translateY(-2px); }
    
    button[kind="primary"], [data-baseweb="button"] {
        background: linear-gradient(135deg, #B19CD9 0%, #40E0D0 100%) !important;
        color: #FFFFFF !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #B19CD9 0%, #40E0D0 100%) !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stMetricValue"] { font-size: 2.5rem; font-weight: 700; color: var(--noir); }
    h1, h2, h3, h4, h5, h6 { font-family: 'Poppins', sans-serif; color: var(--noir); }
    a, a:visited, a:hover { color: #B19CD9 !important; }
    </style>
    """


def get_sidebar_styles_css(sidebar_bg_css: str) -> str:
    """Retourne le CSS de la sidebar avec fond personnalisé."""
    return f"""
    <style>
    [data-testid="stSidebar"] {{ {sidebar_bg_css} }}
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] .stButton > button {{
        background: linear-gradient(180deg, rgba(246, 239, 232, 0.9) 0%, rgba(143, 186, 217, 0.88) 50%, rgba(154, 143, 216, 0.87) 100%) !important;
        color: #3B2F4A !important;
        border: 1px solid rgba(59, 47, 74, 0.12) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{ opacity: 0.92 !important; }}
    </style>
    """


def get_page_background_html(page_id: str, page_background_images: dict) -> str:
    """
    Retourne le HTML pour l'image de fond de la zone principale selon la page.
    Logo logoBon.png affiché au coin gauche.
    """
    image_name = page_background_images.get(page_id)
    if not image_name:
        return ""
    project_root = os.path.dirname(os.path.dirname(__file__))
    img_path = os.path.join(project_root, "assets", image_name)
    if not os.path.exists(img_path):
        return ""
    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(image_name)[1].lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
        data_uri = f"data:{mime};base64,{b64}"
        data_uri_js = json.dumps(data_uri)
        data_uri_css = data_uri.replace("'", "\\'")

        logo_html = ""
        logo_path = os.path.join(project_root, "assets", "logoBon.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f_logo:
                logo_b64 = base64.b64encode(f_logo.read()).decode("utf-8")
            logo_html = f'<div style="position:fixed;top:1rem;left:1rem;z-index:99999;width:110px;height:auto;background:rgba(255,255,255,0.95);padding:6px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);"><img src="data:image/png;base64,{logo_b64}" alt="Logo" style="width:100%;height:auto;display:block;"></div>'

        return f"""
    {logo_html}
    <style id="page-bg-style">
    body .main, section.main {{ position: relative !important; min-height: 100vh !important; background: #FAFAFA !important; }}
    body .main::before, section.main::before {{
        content: '' !important; position: absolute !important; inset: 0 !important; z-index: -2 !important;
        background-image: url('{data_uri_css}') !important; background-size: cover !important;
        background-position: center !important; filter: blur(14px) !important; opacity: 0.75 !important;
    }}
    body .main::after, section.main::after {{
        content: '' !important; position: absolute !important; inset: 0 !important; z-index: -1 !important;
        background: rgba(255, 255, 255, 0.72) !important;
    }}
    body .main .block-container {{ background: rgba(255, 255, 255, 0.98) !important; border-radius: 12px !important; }}
    </style>
    <script>
    (function() {{
        var dataUri = {data_uri_js};
        function applyBg() {{
            var main = document.querySelector(".main");
            if (main && !main.querySelector('.page-bg-blur')) {{
                var blur = document.createElement('div');
                blur.className = 'page-bg-blur';
                blur.style.cssText = 'position:absolute;inset:0;z-index:-2;background-image:url(' + dataUri + ');background-size:cover;background-position:center;filter:blur(14px);opacity:0.75;';
                main.insertBefore(blur, main.firstChild);
                var veil = document.createElement('div');
                veil.className = 'page-bg-veil';
                veil.style.cssText = 'position:absolute;inset:0;z-index:-1;background:rgba(255,255,255,0.72);';
                main.insertBefore(veil, main.firstChild);
            }}
        }}
        applyBg();
        if (document.readyState !== "complete") window.addEventListener("load", applyBg);
        setTimeout(applyBg, 100);
    }})();
    </script>
    """
    except Exception:
        return ""
