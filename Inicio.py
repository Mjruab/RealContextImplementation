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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.stApp { background-color: #fffde7; }
h1 { color: #f57f17; }

.stButton > button {
    background: #f9a825;
    color: white;
    border-radius: 6px;
    font-weight: 600;
    width: 100%;
}
.stButton > button:hover { background: #f57f17; }

.card {
    background: #fff8e1;
    border: 1px solid #ffe082;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 15px;
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

if "pregunta" not in st.session_state:
    st.session_state.pregunta = ""

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = "canvas_1"

# ─────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────
def encode_image(img):
    img.save("img.png")
    with open("img.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="card">
<h1>🧠 Insight Sketch</h1>
<p>Aprende del mundo dibujando — la IA interpreta, enseña y conversa contigo</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SELECTOR DE NIVEL
# ─────────────────────────────────────────────
nivel = st.selectbox(
    "🎯 Nivel de aprendizaje",
    ["Niño", "Joven", "Adulto"]
)

# Ajuste dinámico del prompt
def get_prompt(nivel):
    if nivel == "Niño":
        return """
        Observa este dibujo y responde en español:
        - ¿Qué es?
        - Explicación MUY sencilla (como para un niño)
        - 1 dato curioso divertido
        - Haz una pregunta fácil
        """
    elif nivel == "Joven":
        return """
        Observa este dibujo y responde en español:
        1. ¿Qué es?
        2. Explicación clara
        3. 2 datos curiosos
        4. ¿Por qué es importante?
        5. Haz una pregunta interesante
        """
    else:
        return """
        Observa este dibujo y responde en español:
        1. Identificación precisa
        2. Explicación más profunda
        3. 2-3 datos relevantes
        4. Contexto o impacto en el mundo real
        5. Pregunta reflexiva
        """

# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

# ─────────────────────────────────────────────
# CANVAS
# ─────────────────────────────────────────────
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("✏️ Dibuja algo")

    canvas = st_canvas(
        stroke_width=5,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=400,
        drawing_mode="freedraw",
        key=st.session_state.canvas_key,
    )

    # BOTÓN LIMPIAR (REAL)
    if st.button("🧹 Limpiar canvas"):
        st.session_state.canvas_key = "canvas_" + str(np.random.randint(0,10000))
        st.session_state.analysis_done = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# IA
# ─────────────────────────────────────────────
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    api_key = st.text_input("🔑 API Key", type="password")
    os.environ["OPENAI_API_KEY"] = api_key

    if st.button("🔍 Analizar dibujo"):
        if canvas.image_data is not None and api_key:

            with st.spinner("Pensando..."):
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

                contenido = response.choices[0].message.content

                st.session_state.descripcion = contenido

                if "?" in contenido:
                    st.session_state.pregunta = contenido.split("?")[-2] + "?"

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

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("💬 Sigue aprendiendo")

    user_answer = st.text_input("Tu respuesta:")

    if st.button("Responder"):
        with st.spinner("Pensando..."):

            follow_prompt = f"""
            El usuario vio esto:
            {st.session_state.descripcion}

            Respondió:
            {user_answer}

            Responde de forma educativa, clara y amigable.
            Amplía la información sin evaluar ni juzgar.
            """

            follow_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": follow_prompt}],
                max_tokens=300
            )

            st.markdown("### 🤖 Respuesta de la IA")
            st.write(follow_response.choices[0].message.content)

    st.markdown('</div>', unsafe_allow_html=True)
