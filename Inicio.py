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
# ESTILOS (TEMA UNIFICADO)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #fffde7; color: #333333; }

/* Títulos */
h1 {
    color: #f57f17 !important;
    font-weight: 700 !important;
}
h2, h3 {
    color: #e65100 !important;
    font-weight: 600 !important;
}

/* Inputs */
input, textarea {
    background-color: #fffff0 !important;
    border: 1px solid #f9a825 !important;
    border-radius: 6px !important;
    color: #111827 !important;
}

/* Select */
[data-baseweb="select"] > div {
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
        return """
        Observa este dibujo y responde:
        - ¿Qué es?
        - Explicación muy sencilla
        - 1 dato curioso divertido
        - Haz una pregunta fácil
        """
    elif nivel == "Joven":
        return """
        Observa este dibujo y responde:
        1. ¿Qué es?
        2. Explicación clara
        3. 2 datos curiosos
        4. ¿Por qué es importante?
        5. Haz una pregunta interesante
        """
    else:
        return """
        Observa este dibujo y responde:
        1. Identificación precisa
        2. Explicación más profunda
        3. 2-3 datos relevantes
        4. Impacto en el mundo real
        5. Pregunta reflexiva
        """

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-card">
<h1>🧠 Insight Sketch</h1>
<p style="color:#f57f17;">
Aprende del mundo dibujando — la IA interpreta, explica y conversa contigo
</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GUÍA
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-card">
<h3>¿Cómo funciona?</h3>
<p class="helper-text">
1. Dibuja algo<br>
2. Selecciona el nivel<br>
3. Analiza el dibujo<br>
4. Responde y sigue aprendiendo
</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NIVEL
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### 🎯 Nivel de aprendizaje")
st.markdown('<p class="helper-text">Define cómo la IA te explicará el contenido</p>', unsafe_allow_html=True)

nivel = st.selectbox(
    "Nivel",
    ["Niño", "Joven", "Adulto"],
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

# ─────────────────────────────────────────────
# CANVAS
# ─────────────────────────────────────────────
with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("### ✏️ Dibuja tu idea")
    st.markdown('<p class="helper-text">Haz un boceto simple</p>', unsafe_allow_html=True)

    canvas = st_canvas(
        stroke_width=5,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=400,
        drawing_mode="freedraw",
        key=st.session_state.canvas_key,
    )

    if st.button("🧹 Limpiar canvas"):
        st.session_state.canvas_key = "canvas_" + str(np.random.randint(0,10000))
        st.session_state.analysis_done = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# IA
# ─────────────────────────────────────────────
with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("### 🤖 Análisis inteligente")
    st.markdown('<p class="helper-text">La IA interpretará tu dibujo</p>', unsafe_allow_html=True)

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
                    max_tokens=400
                )

                st.session_state.descripcion = response.choices[0].message.content
                st.session_state.analysis_done = True

        else:
            st.warning("Dibuja algo y agrega tu API key")

    if st.session_state.analysis_done:
        st.markdown("### 🧠 Resultado")
        st.write(st.session_state.descripcion)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INTERACCIÓN
# ─────────────────────────────────────────────
if st.session_state.analysis_done:

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("### 💬 Sigue aprendiendo")
    st.markdown('<p class="helper-text">Responde y profundiza</p>', unsafe_allow_html=True)

    user_answer = st.text_input("Tu respuesta")

    if st.button("Responder"):
        with st.spinner("Pensando..."):

            follow_prompt = f"""
            El usuario vio esto:
            {st.session_state.descripcion}

            Respondió:
            {user_answer}

            Amplía la explicación de forma clara y amigable.
            """

            follow_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": follow_prompt}],
                max_tokens=300
            )

            st.markdown("### 🤖 Respuesta de la IA")
            st.write(follow_response.choices[0].message.content)

    st.markdown('</div>', unsafe_allow_html=True)
