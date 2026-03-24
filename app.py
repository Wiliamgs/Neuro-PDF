import streamlit as st
import fitz  # PyMuPDF
import io
import requests
import base64
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

# --- LOGOS EM BASE64 (Blindagem contra erro de rede) ---
# Substitua estas strings longas pelos códigos Base64 reais dos seus logos PNG
# Você pode gerar esses códigos em sites como 'base64-image.de'
LOGO_COMPLETO_B64 = "INSIRA_AQUI_O_CODIGO_BASE64_DO_LOGO_COMPLETO_PNG" 
LOGO_SIMBOLO_B64 = "INSIRA_AQUI_O_CODIGO_BASE64_DO_SIMBOLO_PNG"

def get_logo_bytes(choice):
    if choice == "Logo Completo (com texto)":
        return base64.b64decode(LOGO_COMPLETO_B64)
    elif choice == "Apenas Símbolo":
        return base64.b64decode(LOGO_SIMBOLO_B64)
    return None

# --- FUNÇÕES CORE ---

def apply_watermark(pdf_stream, image_bytes, opacity_val, overlay_pos):
    # Correção do erro técnico: bad image data
    # Garantir que os bytes da imagem sejam válidos
    if not image_bytes or len(image_bytes) < 10:
        raise ValueError("Dados da imagem inválidos ou vazios.")

    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    
    # Obter proporção da imagem de forma segura
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            ratio = img.height / img.width
    except Exception:
        # Se falhar ao ler a imagem, assume proporção quadrada (segurança)
        ratio = 1.0

    for page in doc:
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Tamanho da marca d'água (baseado na largura da página)
        wm_width = width / 4.5
        wm_height = wm_width * ratio

        # Grid de proteção
        x_step = wm_width * 1.4
        y_step = wm_height * 1.8
        
        for y in range(int(-height/2), int(height*1.5), int(y_step)):
            for x in range(int(-width/2), int(width*1.5), int(x_step)):
                # PyMuPDF fitz suporta opacidade diretamente no insert_image nas versões recentes
                page.insert_image(
                    fitz.Rect(x, y, x + wm_width, y + wm_height),
                    stream=image_bytes,
                    overlay=(overlay_pos == "Frente"),
                    rotate=30,
                    keep_proportion=True,
                    opacity=opacity_val # Aplicando a opacidade do slider
                )
    return doc.write()

# --- EXIBIÇÃO DA FERRAMENTA SELECIONADA ---

if tool_option == "Marca D'água (Overlay)":
    # --- HEADER PRINCIPAL ---
    st.markdown('<h1 class="main-title">Overlay Tool.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Documentos protegidos com a identidade da Neuro.</p>', unsafe_allow_html=True)

    # --- ETAPA 1: PDF ---
    st.markdown("### 1. Selecione o PDF")
    pdf_file = st.file_uploader("Arraste o arquivo aqui", type="pdf", label_visibility="collapsed")

    # --- ETAPA 2: OPÇÕES ---
    st.markdown("### 2. Personalize sua Marca D'água")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Identidade Visual**")
        logo_options = ["Nenhum", "Logo Completo (com texto)", "Apenas Símbolo"]
        logo_choice = st.selectbox("Escolha o logo padrão:", logo_options)
        st.write("---")
        uploaded_logo = st.file_uploader("Ou envie um arquivo personalizado:", type=["png", "jpg", "jpeg"])

    with col2:
        st.write("**Ajustes Finos**")
        opacity = st.slider("Opacidade (Transparência)", 0.05, 1.0, 0.25, 0.05)
        position = st.radio("Sobreposição", ["Frente", "Atrás"], horizontal=True)

    # --- BOTÃO DE AÇÃO ---
    if st.button("Gerar e Baixar PDF Protegido"):
        if pdf_file and (logo_choice != "Nenhum" or uploaded_logo):
            try:
                with st.spinner("Refinando seu documento..."):
                    
                    # Obter bytes da imagem de forma SEGURA
                    img_bytes = None
                    
                    if uploaded_logo:
                        img_bytes = uploaded_logo.read()
                    elif logo_choice != "Nenhum":
                        # Busca o logo em Base64 embutido no código (Sem usar internet)
                        img_bytes = get_logo_bytes(logo_choice)
                    
                    if not img_bytes:
                        raise ValueError("Não foi possível carregar a imagem da marca d'água.")
                    
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
                st.error(f"Ocorreu um erro técnico ao processar a imagem: {e}")
                st.warning("Dica: Tente usar um logo padrão diferente ou envie uma imagem PNG limpa.")
        else:
            st.warning("Ação necessária: Por favor, selecione um arquivo PDF e uma marca d'água.")

elif tool_option == "Juntar PDFs (Merge)":
    # [Código de Merge mantido, ele não usa requests, então está seguro]
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
    # [Código de Organize mantido, seguro]
    st.markdown('<h1 class="main-title">Organize Pages.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Selecione e ordene as páginas que deseja manter.</p>', unsafe_allow_html=True)
    
    f = st.file_uploader("Selecione o PDF", type="pdf")
    pages_to_keep = st.text_input("Páginas a manter (ex: 1, 3, 5-10)", help="Use vírgulas para separar e hífen para intervalos.")
    
    if st.button("Processar Documento") and f and pages_to_keep:
        try:
            with st.spinner("Editando páginas..."):
                doc = fitz.open(stream=f.read(), filetype="pdf")
                
                page_indices = []
                for part in pages_to_keep.split(','):
                    part = part.strip()
                    if not part: continue
                    if '-' in part:
                        try:
                            start, end = map(int, part.split('-'))
                            page_indices.extend(range(start - 1, end))
                        except: continue
                    else:
                        try: page_indices.append(int(part) - 1)
                        except: continue
                
                if not page_indices:
                    raise ValueError("Nenhuma página válida selecionada.")
                    
                doc.select(page_indices)
                output = io.BytesIO()
                doc.save(output)
                st.download_button("✓ Baixar PDF Editado", data=output.getvalue(), file_name="editado_neuro.pdf", mime="application/pdf")
                st.success("Páginas organizadas!")
        except Exception as e:
            st.error(f"Erro: Verifique se os números das páginas estão corretos. {e}")

elif tool_option == "Proteger com Senha":
    # [Código de Protect mantido, seguro]
    st.markdown('<h1 class="main-title">Protect PDF.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Criptografia AES-256 para documentos sensíveis (LGPD).</p>', unsafe_allow_html=True)
    
    f = st.file_uploader("Selecione o PDF", type="pdf")
    password = st.text_input("Defina a senha de abertura", type="password", help="Esta senha será exigida para abrir o arquivo.")
    
    if st.button("Proteger Documento") and f and password:
        try:
            with st.spinner("Aplicando criptografia..."):
                doc = fitz.open(stream=f.read(), filetype="pdf")
                output = io.BytesIO()
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
