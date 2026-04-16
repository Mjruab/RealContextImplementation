import os
import streamlit as st
import base64
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Insight Sketch", layout="wide")

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #fffde7; color: #333; }

[data-testid="stSidebar"] {
    background-color: #fff9c4 !important;
    border-right: 1px solid #f9a825;
}

/* Títulos */
h1 { color: #f57f17 !important; }
h2, h3 { color: #e65100 !important; }

/* Inputs */
input, textarea {
    background-color: #fffff0 !important;
    border: 1px solid #f9a825 !important;
}

/* Botones */
.stButton > button {
    background: #f9a825 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover {
    background: #f57f17 !important;
}

/* Cards */
.header-card {
    background: #fff8e1;
    border-left: 5px solid #f9a825;
    padding: 28px;
    border-radius: 8px;
    margin-bottom: 24px;
}

.section-card {
    background: #fff8e1;
    border: 1px solid #ffe082;
    padding: 22px;
    border-radius: 8px;
    margin-bottom: 16px;
}

/* Texto guía */
.helper-text {
    color: #6b7280;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "descripcion" not in st.session_state:
    st.session_state.descripcion = ""

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = "canvas_1"

# ─────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────
def encode_image(img):
    img.save("img.png")
    with open("img.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_prompt(nivel):
    if nivel == "Niño":
        return "Explica el dibujo de forma muy simple, con un dato curioso y una pregunta fácil."
    elif nivel == "Joven":
        return "Explica el dibujo, da 2 datos curiosos, su importancia y haz una pregunta."
    else:
        return "Da una explicación profunda, contexto real, datos relevantes y una pregunta reflexiva."

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Insight Sketch")

    st.markdown("### 🎯 Nivel de aprendizaje")
    nivel = st.radio(
        "Nivel",
        ["Niño", "Joven", "Adulto"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### 📌 ¿Cómo funciona?")
    st.markdown("""
    1. Dibuja algo  
    2. Analiza el dibujo  
    3. Aprende del resultado  
    4. Responde y sigue explorando  
    """)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-card">
<h1>🧠 Insight Sketch</h1>
<p style="color:#f57f17;">
Aprende del mundo dibujando — la IA interpreta y te enseña
</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DIBUJO
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### ✏️ Dibuja tu idea")
st.markdown('<p class="helper-text">Haz un boceto. Abajo aparecerá el análisis</p>', unsafe_allow_html=True)

canvas = st_canvas(
    stroke_width=5,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=320,
    width=500,
    drawing_mode="freedraw",
    key=st.session_state.canvas_key,
)

col_btn1, col_btn2 = st.columns([1,3])

with col_btn1:
    if st.button("🧹 Limpiar"):
        st.session_state.canvas_key = "canvas_" + str(np.random.randint(0,10000))
        st.session_state.analysis_done = False
        st.rerun()

with col_btn2:
    st.markdown('<p class="helper-text">⬇️ El resultado aparecerá más abajo</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ANÁLISIS
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### 🤖 Análisis inteligente")

api_key = st.text_input("API Key", type="password")
os.environ["OPENAI_API_KEY"] = api_key

if st.button("🔍 Analizar dibujo"):
    if canvas.image_data is not None and api_key:

        with st.spinner("Analizando..."):
            img = Image.fromarray(canvas.image_data.astype('uint8'))
            base64_img = encode_image(img)

            prompt = get_prompt(nivel)

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_img}"
                            }
                        }
                    ]
                }],
                max_tokens=500
            )

            st.session_state.descripcion = response.choices[0].message.content
            st.session_state.analysis_done = True

    else:
        st.warning("Dibuja algo y agrega tu API key")

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────────
if st.session_state.analysis_done:

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("### 🧠 Resultado")
    st.write(st.session_state.descripcion)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INTERACCIÓN
# ─────────────────────────────────────────────
if st.session_state.analysis_done:

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("### 💬 Sigue aprendiendo")

    user_answer = st.text_input("Tu respuesta")

    if st.button("Responder"):
        with st.spinner("Pensando..."):

            follow_prompt = f"""
            Basado en:
            {st.session_state.descripcion}

            Usuario respondió:
            {user_answer}

            Amplía el conocimiento de forma clara y amigable.
            """

            follow_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": follow_prompt}],
                max_tokens=300
            )

            st.write(follow_response.choices[0].message.content)

    st.markdown('</div>', unsafe_allow_html=True)
