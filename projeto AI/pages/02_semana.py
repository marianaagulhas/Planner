import streamlit as st
import sqlite3 as sq
from dataclasses import dataclass, field
import uuid
import datetime
import pandas as pd
import plotly.express as px
import plotly.io as pio 
import plotly.graph_objects as go
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

# CRIAR E DEFENIR A DATA NA ORGANIZAÇÃO DA SEMANA --> semana.csv
conn_semana = sq.connect("semana.csv", check_same_thread=False)
cursor_semana = conn_semana.cursor()
cursor_semana.execute("""
CREATE TABLE IF NOT EXISTS semana (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarefa TEXT NOT NULL,
    username TEXT NOT NULL,
    dia DATE NOT NULL,
    verificação TEXT
)
""")
conn_semana.commit()

# CONECTAR À DATABASE PARA OS USERS --> users.csv
conn_users = sq.connect("users.csv", check_same_thread=False)
cursor_users = conn_users.cursor()

# GUARDA O DETALHES DA AGENDA
def guardar_semana(tarefa, username, dia, verificação):
    cursor_semana.execute("INSERT INTO semana (tarefa, username, dia, verificação) VALUES (?,?,?,?)",(tarefa, username, dia, verificação))
    conn_semana.commit()
    st.success("Sucesso ao guardar a sua nova tarefa, pode verificá-lo nos registos.")

def organizar():
    st.title('Tarefas - Adicionar')
    if st.session_state.username is None:
        st.write("Por favor, inicie sessão ou registe-se.")
        if st.button("conta",key = 'botao_organizar_conta',use_container_width=True) == True:
            st.switch_page("conta.py")
        return
    username = st.session_state.username
    if "hora_inicio" not in st.session_state:
        st.session_state.hora_inicio = datetime.time(0, 0)
    if "hora_fim" not in st.session_state:
        st.session_state.hora_fim = datetime.time(0, 0)
    st.session_state.setdefault("new_item_text", "") #texto da nova tarefa
    st.session_state.setdefault("todos", []) #lista tarefas
    if "username" in st.session_state:
        @dataclass
        class Todo:
            text: str
            dia : str
            inicio: datetime.time
            fim: datetime.time
            is_done: bool = False
            uid: uuid.UUID = field(default_factory=uuid.uuid4)
        if "todos" not in st.session_state:
            st.session_state.todos = []
        def remove_todo(i):
            st.session_state.todos.pop(i)
        def add_todo():
            st.session_state.todos.append(
                Todo(
                    text=st.session_state.new_item_text,
                    dia = dia,
                    inicio=st.session_state.hora_inicio,
                    fim=st.session_state.hora_fim
                )
            )
        def check_todo(i, new_value):
            st.session_state.todos[i].is_done = new_value
        def delete_all_checked():
            st.session_state.todos = [t for t in st.session_state.todos if not t.is_done]
        with st.form(key="new_item_form", clear_on_submit=True, border=False):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1]) 
            with col1:
                tarefa = st.text_input(
                    "Escolher tarefa",
                    label_visibility="collapsed",
                    placeholder="Insira uma tarefa",
                    key="new_item_text",
                )
            with col2:
                dia = st.selectbox(
                    "Escolher um dia da semana",
                    ["Segunda", "Terça", "Quarta", "Quinta", "Sexta","Sábado","Domingo"],
                    label_visibility="collapsed",
                )
            with col3:
                hora_inicio = st.time_input(
                    "Às:", 
                    label_visibility = "collapsed",
                    key="hora_inicio",
                )
            with col4:
                hora_fim = st.time_input (
                    "Às:", 
                    label_visibility = "collapsed",
                    key="hora_fim",
                )
            with col5:
                submitted = st.form_submit_button("+",
                icon=":material/add:",
                )
            if submitted:
                add_todo()
        if st.session_state.todos:
            with st.container(gap=None, border=True):
                for i, todo in enumerate(st.session_state.todos):
                    with st.container(horizontal=True, vertical_alignment="center"):
                        label = f"{todo.text} | {todo.dia} | {todo.inicio.strftime('%H:%M')} - {todo.fim.strftime('%H:%M')}"
                        verificação = st.checkbox(
                            label,
                            value=todo.is_done,
                            key=f"todo-chk-{todo.uid}",
                            )
                        todo.is_done = verificação
                        st.button(
                            ":material/delete:",
                            type="tertiary",
                            on_click=remove_todo,
                            args=[i],
                            key=f"delete_{i}",
                        )
            with st.container(horizontal=True, horizontal_alignment="center"):
                st.button(
                    ":small[Delete all checked]",
                    icon=":material/delete_forever:",
                    type="tertiary",
                    on_click=delete_all_checked,
                )
            if st.button('Confirmar'):
                    if not dia or not hora_inicio or not hora_fim or not tarefa:
                        st.error("Preencha todos os campos!")
                    else:
                        for todo in st.session_state.todos:
                            guardar_semana(
                                todo.text,
                                st.session_state.username,
                                todo.dia,
                                str(todo.is_done)
                            )
                        time.sleep(1.5)
                        st.rerun()
            else:
                      st.text("Quando terminar de preencher todos os campos clique no botão 'Confirmar'!")
        else:
            st.markdown(
            """
            <div style="background-color: #5a3b40; padding: 10px; border-radius: 5px; border: 1px solid #FF69B4;">
                <strong>Sem tarefas adicionadas!</strong>
            </div>
            """,
            unsafe_allow_html=True
            )

# CRIA UMA TABELA EXTRAIDA DA TABELA GERAL DA AGENDA PARA O USERNAME EM SESSION STATE --> agenda.csv
def tabela_semana(username):
    cursor_semana.execute("""SELECT tarefa, dia, verificação FROM semana WHERE username = ? 
                          ORDER BY CASE dia
                            WHEN 'Segunda' THEN 1
                            WHEN 'Terça' THEN 2
                            WHEN 'Quarta' THEN 3
                            WHEN 'Quinta' THEN 4
                            WHEN 'Sexta' THEN 5
                            WHEN 'Sábado' THEN 6
                            WHEN 'Domingo' THEN 7
                        END
                        """, (username,))
    tabela_semana = cursor_semana.fetchall()
    tabela = pd.DataFrame(
            data=tabela_semana,
                columns=("Tarefa","Dia", "Verificação")
        )
    st.dataframe(
            data=tabela,
            use_container_width=True,
            hide_index=True
            )

# FUNCAO QUE VERIFICA A EXISTENCIA DE REGISTOS NA TABELA GERAL DA SEMANA RELATIVAS AO USERNAME EM SESSION STATE --> agenda.csv     
def existe_tabela(username):
    cursor_semana.execute("SELECT username FROM semana WHERE username = ?", (username,))
    tabela_semana = cursor_semana.fetchall()
    if not tabela_semana:
        result = False
    else:
        result = True
    return result

# FUNCAO VÊ SE EXISTE UMA LINHA NA TABELA COM ESSES DADOS
def existe_na_tabela(tarefa, dia, verificação):
    cursor_semana.execute("SELECT id FROM semana WHERE (tarefa, dia, verificação) = (?,?,?)",(tarefa, st.session_state.username, dia, verificação))
    result = cursor_semana.fetchone()
    return result[0] if result else False

#----------------------------------
# ELIMINACAO DE EVENTOS DA TABELA
# ---------------------------------

# FUNCAO VÊ SE EXISTE UMA LINHA NA TABELA COM ESSES DADOS
def existe_na_tabela(dia):
    cursor_semana.execute("SELECT id FROM semana WHERE (username, dia) = (?,?)",(st.session_state.username, dia))
    result = cursor_semana.fetchone()
    return result[0] if result else False
# VAI A TABELA DAS DESPESAS E ELIMINA AQUELA COM OS DADOS PEDIDOS E VAI A TABELA DOS USERS E REPÕE O VALOR DA DESPESA ELMINADA
def eliminar_dados(dia):
    cursor_semana.execute("DELETE FROM semana WHERE (username, dia) = (?,?)", (st.session_state.username, dia))
    conn_semana.commit()
# FUNCAO DO LAYOUT DO POPOVER QUE PEDE OS INPUTS E EXECUTA AS FUNCOES ACIMA
def eliminar_dia():
    with st.popover("Eliminar dia"):    
        st.markdown("Insira o dia que pretende eliminar:")
        dia = st.selectbox(
        "Dia da semana",
        ["Segunda", "Terça", "Quarta", "Quinta", "Sexta","Sábado","Domingo"])
        key = 'tipo_eliminar_dia'
        if st.button("Confirmar", key="confirmar"):
            if not dia:
                st.error("Preencha todos os campos!")
            else:
                id = existe_na_tabela(dia)
                if id!=False:
                    eliminar_dados(dia)
                    st.success("Evento eliminado com sucesso!")
                else:
                    st.error("Erro: esses dados não existem na tabela.")
        else:
            st.markdown("Quando preencher todos os campos clique em 'Confirmar'!")
# ---------------------------------
# GRÁFICOS DAS TAREFAS
# ---------------------------------
def graficos():
    st.title('Gráficos - Tarefas')
    if st.session_state.username is None:
        st.write("Por favor, inicie sessão ou registe-se.")
        if st.button("conta", key='botao_graficos_conta', use_container_width=True):
            st.switch_page("conta.py")
        return
    cursor_semana.execute("SELECT dia, verificação FROM semana WHERE username = ?", (st.session_state.username,))
    dados = cursor_semana.fetchall()
    df = pd.DataFrame(dados, columns=['Dia', 'Verificação'])
    df['Verificação'] = df['Verificação'].map(lambda x: x == "True")
    dias = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    df['Dia'] = pd.Categorical(df['Dia'], categories=dias, ordered=True)
    #----------------------
    # Estilo dos gráficos
    #----------------------
    pio.templates["rosa_theme"] = go.layout.Template(
        data={
            "pie": [
                {
                    "marker": {"colors": ["#FF69B4", "#FFC0CB"]},
                    "textinfo": "percent+label",
                    "insidetextorientation": "radial"
                }
            ]
        }
    )
    pio.templates.default = pio.templates["rosa_theme"]
    st.subheader("Proporção de Tarefas Concluídas por Dia")
    for dia in dias:
        df_dia = df[df['Dia'] == dia]
        if df_dia.empty:
            st.write(f"{dia}: Nenhuma tarefa")
        else:
            contagem = df_dia['Verificação'].value_counts().reset_index()
            contagem.columns = ['Status', 'Quantidade']
            contagem['Status'] = contagem['Status'].map({True: 'Concluídas', False: 'Não Concluídas'})
            fig = px.pie(
                contagem,
                names='Status',
                values='Quantidade',
                title=f"Tarefas de {dia}"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",   
                plot_bgcolor="rgba(0,0,0,0)",    
                font_color="white"               
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------
# LAYOUT DA PAGINA SEMANA
# ---------------------------------

# LAYOUT DA PAGINA DA CRIACAO DE NOVAS TAREFAS
def layout_nova_semana():
    organizar()
# LAYOUT DA PAGINA DA VISUALIZACAO DE REGISTOS
def layout_registos_tarefas():
    st.title("Tarefas - Registos")    
    if st.session_state.get("username") is None:
        st.write("Por favor, inicie sessão ou registe-se.")   
        if st.button("conta", key='botao_registos_conta', use_container_width=True):
            st.switch_page("conta.py")
        return  
    if existe_tabela(st.session_state.username)==False:
        st.text("Ainda não há nada aqui, adicione um evento para continuar!")
    else:
        eliminar_dia()
        st.subheader("Tabela de Eventos")
        tabela_semana(st.session_state.username)
#LAYOUT DA PAGINA DA VISUALIZACAO DE GRÁFICOS
def layout_graficos():
    graficos()

# ---------------------------------
# SIDEBAR
# ---------------------------------

def sidebar():
    page = st.sidebar.radio("Navegar",["Organize a sua semana", "Registos","Gráficos"])
    if page == "Organize a sua semana":
        layout_nova_semana()
    if page == "Registos":
        layout_registos_tarefas()
    if page == 'Gráficos':
        layout_graficos()


sidebar()