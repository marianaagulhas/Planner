import streamlit as st
import sqlite3 as sq
import time

# -----------------------------
# ESTILO DA APP (CSS)
# -----------------------------
st.markdown(
    """
    <style>
    /* Fundo principal */
    .stApp {
        background-color: #5a3b40;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #3f2a2e;
    }

    /* Títulos (MESMA COR DO BOTÃO) */
    h1, h2, h3 {
        color: #f8b4c4;
        font-weight: 700;
    }

    /* Labels */
    label {
        color: #f8b4c4;
        font-weight: 600;
    }

    /* Inputs */
    input {
        background-color: #ffffff !important;
        border: 2px solid #e89ab0 !important;
        color: #3f2a2e !important;
        border-radius: 20px;
        padding: 0.6em;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #e89ab0 !important;
        color: #3f2a2e !important;
        border-radius: 20px;
    }

    /* Botões */
    .stButton > button {
        background-color: #f8b4c4;
        color: #5a3b40;
        border-radius: 25px;
        border: none;
        padding: 0.6em 1.5em;
        font-weight: 700;
    }

    .stButton > button:hover {
        background-color: #e89ab0;
        color: #3f2a2e;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# CRIAR E DEFINIR A DATABASE PARA OS USERS --> users.csv
conn_users = sq.connect("users.db", check_same_thread=False)
cursor_users = conn_users.cursor()
cursor_users.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn_users.commit()

# VAI VER NA TABELA SE EXISTE UM USERNAME E PASSWORD IGUAIS AOS QUE FORAM PEDIDOS
def entrar(username, password):
    cursor_users.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    return cursor_users.fetchone()

# GUARDA NA TABELA DOS USERS O USERNAME PASSWORD E QUANTIA INICIAL DO NOVO USER --> users.csv
def registar(username, password):
    try:
        cursor_users.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn_users.commit()
        return True
    except:
        return False
    
# FUNCAO DE REDIRECIONAMENTO ATE QUALQUER PAGINA DA APP
def op():
    st.text("Escolhe para aonde queres ser redirecionado ")
    agenda = st.columns(1)
    organizar_semana = st.colums(2)
    if agenda.button("agenda",use_container_width=True):
        st.switch_page("pages/01_agenda.py")
    elif organizar_semana.button('organize a sua semana',use_container_width=True):
        st.switch_page('pages/02_semana.py')
  

#FUNÇÃO PARA ENTRAR OU REGISTAR CONTA 
def conta():
    st.title('Bem-vindo/a ao Planner :)')
    choice = st.selectbox('Entrar/Registar', ['Entrar', 'Registar'])

    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if choice == 'Registar':
        if st.button('Criar a minha conta'):
            if not username or not password:
                st.error('Preencha todos os campos!')
            else:
                if registar(username, password):
                    st.success('Conta criada com sucesso!')
                else:
                    st.error('Usuário já existe.')

    else:
        if st.button('Entrar'):
            user = entrar(username, password)
            if user:
                st.session_state.username = username
                st.success(f"Bem-vindo(a), {username}!")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")


conta()
