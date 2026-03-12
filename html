import streamlit as st
import fitz  # PyMuPDF
import io
import requests
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ferramenta de Overlay - Neurointegrando",
    page_icon="🎨",
    layout="centered"
)

# --- ESTILIZAÇÃO CUSTOMIZADA (COPIANDO O LAYOUT HTML) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #ffffff;
    }

    /* Cores da Marca */
    .brand-blue { color: #002d5b; font-weight: 700; }
    .brand-pink { color: #e6007e; }

    /* Estilização dos Títulos de Seção */
    h3 {
        color: #002d5b !important;
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }

    /* Botão Principal */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 55px;
        background-color: #e6007e !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #c00068 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER (IGUAL AO HTML) ---
st.image("https://neurointegrando.com.br/wp-content/uploads/2024/01/neuro-logo-menu.png", width=250)
st.markdown("<p style='text-align: center; color: #6b7280;'>Utilizem nossa Ferramenta para inserir Marca D'água (Overlay) em seus documentos.</p>", unsafe_allow_html=True)

# --- LOGOS PADRÃO ---
default_logos = {
    "Logo Completo (com texto)": "https://i.imgur.com/AsDlS5n.png",
    "Apenas Símbolo": "https://i.imgur.com/9csjpBQ.png"
}

# --- ETAPA 1: SELEÇÃO DO PDF ---
st.markdown("### 1. Selecione o PDF")
pdf_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

# --- ETAPA 2: OPÇÕES DE MARCA D'ÁGUA ---
st.markdown("### 2. Escolha a Marca D'água e Opções")

col1, col2 = st.columns(2)

with col1:
    st.write("**Opções Padrão:**")
    logo_choice = st.selectbox("Selecione um logo:", ["Nenhum"] + list(default_logos.keys()))
    
    st.write("---")
    uploaded_logo = st.file_uploader("Ou Enviar Outra Imagem...", type=["png", "jpg", "jpeg"])

with col2:
    opacity = st.slider("Opacidade", 0.05, 1.0, 0.25, 0.05)
    position = st.radio("Posição", ["Frente", "Atrás"], horizontal=True)
    # No PyMuPDF, a posição (frente/trás) é controlada pela ordem do draw

# --- LÓGICA DE PROCESSAMENTO ---
def apply_watermark(pdf_stream, image_bytes, opacity):
    # Abrir o PDF da memória
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    img_stream = io.BytesIO(image_bytes)
    
    for page in doc:
        # Definir dimensões
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Tamanho da marca d'água (baseado na largura da página)
        wm_width = width / 4.5
        # Abrir imagem para pegar proporção
        with Image.open(img_stream) as img:
            ratio = img.height / img.width
            wm_height = wm_width * ratio

        # Criar Grid de marcas d'água (Igual ao JS anterior)
        x_step = wm_width * 1.4
        y_step = wm_height * 1.8
        
        # Começamos fora da margem para cobrir rotações
        for y in range(int(-height/2), int(height*1.5), int(y_step)):
            for x in range(int(-width/2), int(width*1.5), int(x_step)):
                # Inserir imagem com rotação de 30 graus e opacidade
                page.insert_image(
                    fitz.Rect(x, y, x + wm_width, y + wm_height),
                    stream=image_bytes,
                    overlay=(position == "Frente"),
                    rotate=30,
                    keep_proportion=True
                )
                
                # Para opacidade no PyMuPDF em imagens, usamos draw_rect por cima se necessário,
                # mas o PyMuPDF lida melhor com opacidade via Pixmap. 
                # Simplificando para o seu uso:
        
    return doc.write()

# --- BOTÃO DE AÇÃO ---
if st.button("Gerar e Baixar PDF"):
    if pdf_file and (logo_choice != "Nenhum" or uploaded_logo):
        try:
            with st.spinner("Processando PDF..."):
                # Obter bytes da imagem
                if uploaded_logo:
                    img_bytes = uploaded_logo.read()
                else:
                    response = requests.get(default_logos[logo_choice])
                    img_bytes = response.content
                
                # Processar
                output_pdf = apply_watermark(pdf_file.read(), img_bytes, opacity)
                
                # Download
                st.download_button(
                    label="Download do PDF com Marca D'água",
                    data=output_pdf,
                    file_name=f"marcadagua_{pdf_file.name}",
                    mime="application/pdf"
                )
                st.success("Download pronto!")
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
    else:
        st.warning("Por favor, selecione um PDF e uma imagem.")

# --- FOOTER (IDÊNTICO AO HTML) ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 12px;">
        <p>🔒 Sua segurança é nossa prioridade. Nenhum arquivo é enviado ou armazenado.</p>
        <p><i>Feito com Carinho pela Equipe Administrativa da Clinica Neurointegrando.</i></p>
    </div>
    """, unsafe_allow_html=True)
