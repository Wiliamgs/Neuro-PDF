
import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO

# --- CONFIGURAÇÃO PREMIUM ---
st.set_page_config(page_title="Neuro | PDF Suite", page_icon="📄", layout="centered")

# --- CSS ESTILO APPLE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #ffffff; }
    .main-title { font-weight: 700; font-size: 42px; letter-spacing: -1.2px; color: #1d1d1f; }
    /* Estilização da Sidebar */
    [data-testid="stSidebar"] { background-color: #f5f5f7; border-right: 1px solid #d2d2d7; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #0071e3; color: white; border: none; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAV ---
st.sidebar.markdown("# Neuro PDF.")
tool = st.sidebar.radio("Ferramentas:", [
    "Juntar PDFs", 
    "Dividir PDF", 
    "Comprimir PDF", 
    "Remover/Reorganizar Páginas",
    "Proteger com Senha",
    "Imagem para PDF"
])

st.markdown(f'<h1 class="main-title">{tool}.</h1>', unsafe_allow_html=True)

# --- LÓGICA DAS FERRAMENTAS ---

if tool == "Juntar PDFs":
    st.write("Combine vários documentos em um único arquivo.")
    uploaded_files = st.file_uploader("Selecione os arquivos", type="pdf", accept_multiple_files=True)
    if st.button("Unificar Documentos") and uploaded_files:
        new_pdf = fitz.open()
        for f in uploaded_files:
            with fitz.open(stream=f.read(), filetype="pdf") as doc:
                new_pdf.insert_pdf(doc)
        
        output = BytesIO()
        new_pdf.save(output)
        st.download_button("✓ Baixar PDF Unificado", data=output.getvalue(), file_name="unificado.pdf")

elif tool == "Remover/Reorganizar Páginas":
    st.write("Digite as páginas que deseja manter (ex: 1, 2, 5).")
    f = st.file_uploader("Selecione o PDF", type="pdf")
    pages_to_keep = st.text_input("Páginas a manter (separadas por vírgula)")
    if st.button("Processar") and f and pages_to_keep:
        doc = fitz.open(stream=f.read(), filetype="pdf")
        page_list = [int(p.strip()) - 1 for p in pages_to_keep.split(",")]
        doc.select(page_list) # Aqui ele remove as que não estão na lista
        output = BytesIO()
        doc.save(output)
        st.download_button("✓ Baixar PDF Editado", data=output.getvalue(), file_name="editado.pdf")

elif tool == "Proteger com Senha":
    f = st.file_uploader("Selecione o PDF", type="pdf")
    password = st.text_input("Defina a senha de abertura", type="password")
    if st.button("Proteger PDF") and f and password:
        doc = fitz.open(stream=f.read(), filetype="pdf")
        output = BytesIO()
        # Permissões padrão: permitir impressão e cópia, mas exigir senha para abrir
        doc.save(output, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=password)
        st.download_button("✓ Baixar PDF Protegido", data=output.getvalue(), file_name="protegido.pdf")

# --- FOOTER ---
st.markdown("<br><hr><center><p style='color: #86868b; font-size: 12px;'>Neurointegrando | Privacy First Architecture</p></center>", unsafe_allow_html=True)
