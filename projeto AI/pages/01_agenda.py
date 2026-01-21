import streamlit as st
from datetime import date
import sqlite3 as sq
import pandas as pd
import time

# -----------------------------
# ESTILO DA APP (CSS)
# -----------------------------
st.markdown("""
    <style>
    /* Fundo principal */
    .stApp {
        background-color: #0E1117;
    }
            
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #3f2a2e;
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
    """, unsafe_allow_html=True)

if "username" not in st.session_state:
    st.session_state.username = None

# CRIAR E DEFENIR A DATA NA AGENDA --> agenda.csv
conn_agenda = sq.connect("agenda.csv", check_same_thread=False)
cursor_agenda = conn_agenda.cursor()
cursor_agenda.execute("""
CREATE TABLE IF NOT EXISTS agenda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    dia DATE NOT NULL,
    tipo NOT NULL,
    descricao TEXT
)
""")
conn_agenda.commit()

# CONECTAR À DATABASE PARA OS USERS --> users.csv
conn_users = sq.connect("users.csv", check_same_thread=False)
cursor_users = conn_users.cursor()

# GUARDA O DETALHES DA AGENDA
def guardar_agenda(username, dia, tipo, descricao):
    cursor_agenda.execute("INSERT INTO agenda (username, dia, tipo, descricao) VALUES (?,?,?,?)",(username, dia, tipo, descricao))
    conn_agenda.commit()
    st.success("Sucesso ao guardar o seu novo evento, pode verificá-lo nos registos.")

def novo_evento():
    if st.session_state.username is None:
        st.write("Por favor, inicie sessão ou registe-se.")
        if st.button("conta",key = 'botao_organizar_conta',use_container_width=True) == True:
            st.switch_page("conta.py")
        return
    username = st.session_state.username
    dia = st.date_input ('Escolha uma data',
        value = date(2026, 1, 21),
        min_value = date(2026, 1, 21))
    tipo = st.radio("Tipo:", ['Teste','Trabalho','Apresentação','Aniversário','Jogo','Outros'])
    descricao = st.text_area("Descrição:")
    key = 'tipo_novo_evento'
    if st.button('Confirmar'):
        if not dia or not tipo:
            st.error("Preencha todos os campos!")
        else:
            guardar_agenda(username, dia, tipo, descricao)
            time.sleep(1.5) 
            st.rerun()
    else:
        st.text("Quando terminar de preencher todos os campos clique no botão 'Confirmar'!")

# CRIA UMA TABELA EXTRAIDA DA TABELA GERAL DA AGENDA PARA O USERNAME EM SESSION STATE --> agenda.csv
def tabela_agenda(username):
    cursor_agenda.execute("SELECT dia, tipo, descricao FROM agenda WHERE username = ?", (username,))
    tabela_agenda = cursor_agenda.fetchall()
    tabela = pd.DataFrame(
            data=tabela_agenda,
                columns=("Dia","Tipo", "Descrição")
        )
    st.dataframe(
            data=tabela,
            use_container_width=True,
            hide_index=True
            )
    
# FUNCAO QUE VERIFICA A EXISTENCIA DE REGISTOS NA TABELA GERAL DA AGENDA RELATIVAS AO USERNAME EM SESSION STATE --> agenda.csv     
def existe_tabela(username):
    cursor_agenda.execute("SELECT username FROM agenda WHERE username = ?", (username,))
    tabela_agenda = cursor_agenda.fetchall()
    if not tabela_agenda:
        result = False
    else:
        result = True
    return result

# ---------------------------------
# ELIMINACAO DE EVENTOS DA TABELA
# ---------------------------------

# FUNCAO VÊ SE EXISTE UMA LINHA NA TABELA COM ESSES DADOS
def existe_na_tabela(dia, tipo, descricao):
    cursor_agenda.execute("SELECT id FROM agenda WHERE (username, dia, tipo, descricao) = (?,?,?,?)",(st.session_state.username, dia, tipo, descricao))
    result = cursor_agenda.fetchone()
    return result[0] if result else False
# VAI A TABELA DAS DESPESAS E ELIMINA AQUELA COM OS DADOS PEDIDOS E VAI A TABELA DOS USERS E REPÕE O VALOR DA DESPESA ELMINADA
def eliminar_dados(dia, tipo, descricao):
    cursor_agenda.execute("DELETE FROM agenda WHERE (username, dia, tipo, descricao) = (?,?,?,?)", (st.session_state.username, dia, tipo, descricao))
    conn_agenda.commit()
# FUNCAO DO LAYOUT DO POPOVER QUE PEDE OS INPUTS E EXECUTA AS FUNCOES ACIMA
def eliminar_agenda():
    with st.popover("Eliminar evento"):    
        st.markdown("Insira os detalhes do evento que deseja eliminar:")
        dia = st.date_input("Dia")
        tipo = st.radio("Tipo:", ['Teste','Trabalho','Apresentação','Aniversário','Jogo','Outros'])
        descricao = st.text_input("Descrição")
        key = 'tipo_eliminar_evento'
        if st.button("Confirmar", key="confirmar"):
            if not dia or not tipo:
                st.error("Preencha todos os campos!")
            else:
                id = existe_na_tabela(dia,tipo,descricao)
                if id!=False:
                    eliminar_dados(dia,tipo,descricao)
                    st.success("Evento eliminado com sucesso!")
                else:
                    st.error("Erro: esses dados não existem na tabela.")
        else:
            st.markdown("Quando preencher todos os campos clique em 'Confirmar'!")

# ---------------------------------
# LAYOUT DA PAGINA AGENDA
# ---------------------------------

# LAYOUT DA PAGINA DA CRIACAO DE NOVOS EVENTOS
def layout_nova_agenda():
    st.title("Novo evento")
    novo_evento()
# LAYOUT DA PAGINA DA VISUALIZACAO DE REGISTOS
def layout_registos_agenda():
    st.title("Agenda - Registos") 
    if st.session_state.get("username") is None:
        st.write("Por favor, inicie sessão ou registe-se.")   
        if st.button("conta",use_container_width=True) == True:
            st.switch_page("conta.py")
    if existe_tabela(st.session_state.username)==False:
        st.text("Ainda não há nada aqui, adicione um evento para continuar!")
    else:
        eliminar_agenda()
        st.subheader("Tabela de Eventos")
        tabela_agenda(st.session_state.username)

# ---------------------------------
# SIDEBAR
# ---------------------------------

def sidebar():
    page = st.sidebar.radio("Navegar",["Novo evento", "Registos"])
    if page == "Novo evento":
        layout_nova_agenda()
    if page == "Registos":
        layout_registos_agenda()

sidebar()
