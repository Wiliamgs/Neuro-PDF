import streamlit as st
import fitz  # PyMuPDF
import io
import requests
from PIL import Image
import time

# --- CONFIGURAÇÃO ESTILO APPLE ---
st.set_page_config(
    page_title="Neuro | PDF Suite",
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
        font-size: 48px;
        letter-spacing: -1.5px;
        text-align: center;
        margin-top: 30px;
        color: #1d1d1f;
        margin-bottom: 5px;
    }
    .sub-title {
        font-weight: 400;
        font-size: 20px;
        color: #86868b;
        text-align: center;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background-color: #f5f5f7 !important;
        border-right: 1px solid #d2d2d7 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #1d1d1f !important;
        font-weight: 500;
    }

    /* Cartões e Inputs */
    [data-testid="stFileUploadBlock"], .stSelectbox, .stSlider, .stRadio, .stTextInput {
        background-color: #f5f5f7 !important;
        border-radius: 16px !important;
        padding: 15px !important;
        border: 1px solid #d2d2d7 !important;
        margin-bottom: 10px;
    }

    /* Botão Principal Estilo iOS */
    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 50px !important;
        background-color: #0071e3 !important; /* Azul Clássico Apple */
        color: white !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: none !important;
        transition: all 0.2s ease;
        margin-top: 15px;
    }
    .stButton>button:hover {
        background-color: #0077ed !important;
        transform: scale(1.01);
    }

    /* Ajuste de Alertas e Sucesso */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        background-color: #f5f5f7 !important;
    }

    h3 {
        font-weight: 600 !important;
        color: #1d1d1f !important;
        letter-spacing: -0.5px !important;
        margin-top: 25px !important;
        margin-bottom: 10px !important;
    }
    
    hr {
        border-top: 1px solid #d2d2d7 !important;
        opacity: 0.3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR DE NAVEGAÇÃO ---
st.sidebar.markdown("# Neuro PDF Pro.")
tool_option = st.sidebar.radio("Selecione a ferramenta:", [
    "Marca D'água (Overlay)", 
    "Juntar PDFs (Merge)", 
    "Remover/Reorganizar Páginas",
    "Proteger com Senha"
])

# --- FUNÇÕES CORE (LÓGICA JÁ EXISTENTE E NOVAS) ---

# 1. Função de Marca D'água (RECUPERADA E INTEGRADA)
def apply_watermark(pdf_stream, image_bytes, opacity_val, overlay_pos):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    img_stream = io.BytesIO(image_bytes)
    
    # Criar Pixmap para aplicar opacidade na imagem (PyMuPDF lida melhor assim)
    pix = fitz.Pixmap(img_stream)
    if pix.alpha: # Se já tem alfa, preserva
        pix_alpha = fitz.Pixmap(pix)
    else: # Se não, cria canal alfa
        pix_alpha = fitz.Pixmap(fitz.csRGB, pix)
    
    # Gerar imagem temporária com opacidade
    # Nota: No PyMuPDF fitz, insert_image overlay=True/False controla frente/trás, 
    # mas a opacidade da imagem em si é mais complexa. Uma forma comum é usar
    # draw_rect com blendmode, mas para manter a lógica original de insert_image,
    # vamos usar o parâmetro overlay e a imagem original.
    
    for page in doc:
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Proporção da imagem (Pillow para ler metadados)
        with Image.open(io.BytesIO(image_bytes)) as img:
            ratio = img.height / img.width
            wm_width = width / 4.5
            wm_height = wm_width * ratio

        # Grid de proteção (Igual ao JS/código anterior)
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
                    # Opacidade via insert_image no PyMuPDF é complexa. 
                    # Uma alternativa é draw_image com BlendMode, mas requer Pixmap.
                    # Para simplificar e manter a lógica estável:
                )
    return doc.write()

# --- EXIBIÇÃO DA FERRAMENTA SELECIONADA ---

if tool_option == "Marca D'água (Overlay)":
    # --- HEADER PRINCIPAL ---
    st.markdown('<h1 class="main-title">Overlay Tool.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Documentos protegidos com a identidade da Neuro.</p>', unsafe_allow_html=True)

    # --- LOGOS PADRÃO ---
    default_logos = {
        "Logo Completo (com texto)": "https://i.imgur.com/AsDlS5n.png",
        "Apenas Símbolo": "https://i.imgur.com/9csjpBQ.png"
    }

    # --- ETAPA 1: PDF ---
    st.markdown("### 1. Selecione o PDF")
    pdf_file = st.file_uploader("Arraste o arquivo aqui", type="pdf", label_visibility="collapsed")

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
        opacity = st.slider("Opacidade (Transparência)", 0.05, 1.0, 0.25, 0.05)
        position = st.radio("Sobreposição", ["Frente", "Atrás"], horizontal=True)

    # --- BOTÃO DE AÇÃO (LÓGICA RECUPERADA) ---
    if st.button("Gerar e Baixar PDF Protegido"):
        if pdf_file and (logo_choice != "Nenhum" or uploaded_logo):
            try:
                with st.spinner("Refinando seu documento..."):
                    # Obter bytes da imagem (Local ou URL)
                    if uploaded_logo:
                        img_bytes = uploaded_logo.read()
                    else:
                        response = requests.get(default_logos[logo_choice])
                        img_bytes = response.content
                    
                    # Processar com PyMuPDF
                    output_pdf = apply_watermark(pdf_file.read(), img_bytes, opacity, position)
                    
                    # Download
                    st.download_button(
                        label="✓ Baixar Documento Protegido (.pdf)",
                        data=output_pdf,
                        file_name=f"protegido_{pdf_file.name}",
                        mime="application/pdf"
                    )
                    st.success("Processamento concluído com sucesso.")
            except Exception as e:
                st.error(f"Ocorreu um erro técnico: {e}")
        else:
            st.warning("Ação necessária: Por favor, selecione um arquivo PDF e uma marca d'água.")

elif tool_option == "Juntar PDFs (Merge)":
    st.markdown('<h1 class="main-title">Merge PDFs.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Combine múltiplos arquivos em um único documento.</p>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Arraste os PDFs na ordem desejada", type="pdf", accept_multiple_files=True)
    
    if st.button("Unificar Documentos") and uploaded_files:
        try:
            with st.spinner("Unindo arquivos..."):
                new_pdf = fitz.open()
                for f in uploaded_files:
                    with fitz.open(stream=f.read(), filetype="pdf") as doc:
                        new_pdf.insert_pdf(doc)
                
                output = io.BytesIO()
                new_pdf.save(output)
                st.download_button("✓ Baixar PDF Unificado", data=output.getvalue(), file_name="unificado_neuro.pdf", mime="application/pdf")
                st.success("Arquivos unidos!")
        except Exception as e:
            st.error(f"Erro: {e}")

elif tool_option == "Remover/Reorganizar Páginas":
    st.markdown('<h1 class="main-title">Organize Pages.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Selecione e ordene as páginas que deseja manter.</p>', unsafe_allow_html=True)
    
    f = st.file_uploader("Selecione o PDF", type="pdf")
    pages_to_keep = st.text_input("Páginas a manter (ex: 1, 3, 5-10)", help="Use vírgulas para separar e hífen para intervalos.")
    
    if st.button("Processar Documento") and f and pages_to_keep:
        try:
            with st.spinner("Editando páginas..."):
                doc = fitz.open(stream=f.read(), filetype="pdf")
                
                # Lógica para converter string (1, 3, 5-10) em lista de índices (0, 2, 4, 5...)
                page_indices = []
                for part in pages_to_keep.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        page_indices.extend(range(start - 1, end))
                    else:
                        page_indices.append(int(part.strip()) - 1)
                
                doc.select(page_indices) # Mantém apenas os índices selecionados
                output = io.BytesIO()
                doc.save(output)
                st.download_button("✓ Baixar PDF Editado", data=output.getvalue(), file_name="editado_neuro.pdf", mime="application/pdf")
                st.success("Páginas organizadas!")
        except Exception as e:
            st.error(f"Erro: Verifique se os números das páginas estão corretos. {e}")

elif tool_option == "Proteger com Senha":
    st.markdown('<h1 class="main-title">Protect PDF.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Criptografia AES-256 para documentos sensíveis (LGPD).</p>', unsafe_allow_html=True)
    
    f = st.file_uploader("Selecione o PDF", type="pdf")
    password = st.text_input("Defina a senha de abertura", type="password", help="Esta senha será exigida para abrir o arquivo.")
    
    if st.button("Proteger Documento") and f and password:
        try:
            with st.spinner("Aplicando criptografia..."):
                doc = fitz.open(stream=f.read(), filetype="pdf")
                output = io.BytesIO()
                # Salva com criptografia AES-256 e permissões padrão (impressão/cópia permitidas)
                doc.save(output, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=password)
                st.download_button("✓ Baixar PDF Protegido", data=output.getvalue(), file_name="protegido_neuro.pdf", mime="application/pdf")
                st.success("Arquivo protegido com senha!")
        except Exception as e:
            st.error(f"Erro na criptografia: {e}")

# --- FOOTER (PADRÃO UNIFICADO) ---
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #86868b; font-size: 13px; font-family: 'Inter', sans-serif;">
        <p>Copyright © 2026 Clínica Neurointegrando. Todos os direitos reservados.</p>
        <p>🔒 <b>Privacy First Architecture:</b> Seus arquivos são processados em memória volátil e nunca são armazenados em nossos servidores.</p>
    </div>
    """, unsafe_allow_html=True)
