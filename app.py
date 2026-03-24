import streamlit as st
import fitz  # PyMuPDF
import io
import requests
from PIL import Image
import time

# --- CONFIGURAÇÃO ESTILO APPLE ---
st.set_page_config(
    page_title="Neuro | Overlay Tool",
    page_icon="🎨",
    layout="centered"
)

# --- CSS: ESTÉTICA MINIMALISTA PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Fundo Limpo e Moderno */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
        color: #1d1d1f !important;
    }

    /* Títulos Impactantes */
    .main-title {
        font-weight: 700;
        font-size: 52px;
        letter-spacing: -1.5px;
        text-align: center;
        margin-top: 40px;
        color: #1d1d1f;
        margin-bottom: 5px;
    }
    .sub-title {
        font-weight: 400;
        font-size: 22px;
        color: #86868b;
        text-align: center;
        margin-bottom: 50px;
        letter-spacing: -0.5px;
    }

    /* Cartões e Inputs Estilizados */
    [data-testid="stFileUploadBlock"], .stSelectbox, .stSlider, .stRadio {
        background-color: #f5f5f7 !important;
        border-radius: 18px !important;
        padding: 20px !important;
        border: 1px solid #d2d2d7 !important;
    }

    /* Botão Principal Estilo iOS */
    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 55px !important;
        background-color: #0071e3 !important; /* Azul Clássico Apple */
        color: white !important;
        font-weight: 600 !important;
        font-size: 17px !important;
        border: none !important;
        transition: all 0.2s ease;
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #0077ed !important;
        transform: scale(1.01);
    }

    /* Ajuste de Alertas */
    .stAlert {
        border-radius: 14px !important;
        border: none !important;
        background-color: #f5f5f7 !important;
    }

    h3 {
        font-weight: 600 !important;
        color: #1d1d1f !important;
        letter-spacing: -0.5px !important;
        margin-top: 30px !important;
    }
    
    hr {
        border-top: 1px solid #d2d2d7 !important;
        opacity: 0.3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="main-title">Overlay Tool.</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Documentos protegidos com elegância.</p>', unsafe_allow_html=True)

# --- LOGOS PADRÃO ---
default_logos = {
    "Logo Completo (com texto)": "https://i.imgur.com/AsDlS5n.png",
    "Apenas Símbolo": "https://i.imgur.com/9csjpBQ.png"
}

# --- ETAPA 1: SELEÇÃO DO PDF ---
st.markdown("### 1. Selecione o PDF")
pdf_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

# --- ETAPA 2: OPÇÕES ---
st.markdown("### 2. Personalize sua Marca D'água")

col1, col2 = st.columns(2)

with col1:
    st.write("**Identidade Visual**")
    logo_choice = st.selectbox("Escolha o logo padrão:", ["Nenhum"] + list(default_logos.keys()))
    
    st.write("---")
    uploaded_logo = st.file_uploader("Ou envie um arquivo personalizado:", type=["png", "jpg", "jpeg"])

with col2:
    st.write("**Ajustes Finos**")
    opacity = st.slider("Opacidade", 0.05, 1.0, 0.25, 0.05)
    position = st.radio("Sobreposição", ["Frente", "Atrás"], horizontal=True)

# --- LÓGICA DE PROCESSAMENTO ---
def apply_watermark(pdf_stream, image_bytes, opacity, overlay_pos):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    img_stream = io.BytesIO(image_bytes)
    
    for page in doc:
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Proporção da imagem
        with Image.open(img_stream) as img:
            ratio = img.height / img.width
            wm_width = width / 4.5
            wm_height = wm_width * ratio

        # Grid de proteção
        x_step = wm_width * 1.4
        y_step = wm_height * 1.8
        
        for y in range(int(-height/2), int(height*1.5), int(y_step)):
            for x in range(int(-width/2), int(width*1.5), int(x_step)):
                page.insert_image(
                    fitz.Rect(x, y, x + wm_width, y + wm_height),
                    stream=image_bytes,
                    overlay=(overlay_pos == "Frente"),
                    rotate=30,
                    keep_proportion=True
                )
    return doc.write()

# --- BOTÃO DE AÇÃO ---
if st.button("Gerar e Baixar PDF"):
    if pdf_file and (logo_choice != "Nenhum" or uploaded_logo):
        try:
            with st.spinner("Refinando seu documento..."):
                # Obter bytes da imagem
                if uploaded_logo:
                    img_bytes = uploaded_logo.read()
                else:
                    response = requests.get(default_logos[logo_choice])
                    img_bytes = response.content
                
                # Processar
                output_pdf = apply_watermark(pdf_file.read(), img_bytes, opacity, position)
                
                # Download
                st.download_button(
                    label="✓ Baixar Documento Protegido",
                    data=output_pdf,
                    file_name=f"protegido_{pdf_file.name}",
                    mime="application/pdf"
                )
                st.success("Processamento concluído com sucesso.")
        except Exception as e:
            st.error(f"Ocorreu um erro técnico: {e}")
    else:
        st.warning("Ação necessária: Por favor, selecione um arquivo PDF e uma marca d'água.")

# --- FOOTER ---
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #86868b; font-size: 13px; font-family: 'Inter', sans-serif;">
        <p>Copyright © 2026 Clínica Neurointegrando. Todos os direitos reservados.</p>
        <p>🔒 <b>Privacidade garantida:</b> Seus arquivos são processados em memória volátil e nunca são armazenados em nossos servidores.</p>
    </div>
    """, unsafe_allow_html=True)
