import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Saúde mental",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
.main {
    padding-top: 0rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Carregamento de dados
# -------------------------
@st.cache_data
def load_data():
    base_path = Path(__file__).parent
    file_path = base_path / "data" / "dados_saude_mental_fake.csv"
    return pd.read_csv(file_path)

df = load_data()

# -------------------------
# Título
# -------------------------
st.title("🧠 Dashboard de Saúde Mental")
st.caption("Perfil demográfico, clínico e experiência com tratamento")

st.markdown("---")
st.sidebar.markdown("## 🔎 Filtros de Análise")

# -------------------------
# Filtros
# -------------------------
idade_min_global = int(df['idade'].min())
idade_max_global = int(df['idade'].max())

idade_min, idade_max = st.sidebar.slider(
    "Selecione a faixa etária",
    idade_min_global,
    idade_max_global,
    (idade_min_global, idade_max_global)
)

genero = st.sidebar.multiselect(
    "Selecione o gênero",
    df['genero'].unique(),
    default=df['genero'].unique()
)

estado_civil = st.sidebar.multiselect(
    "Selecione o estado civil",
    df['estado_civil'].unique(),
    default=df['estado_civil'].unique()
)

escolaridade = st.sidebar.multiselect(
    "Selecione o nível de escolaridade",
    df['nivel_escolaridade'].unique(),
    default=df['nivel_escolaridade'].unique()
)

# -------------------------
# DataFrame filtrado
# -------------------------
df_filtrado = df[
    (df['idade'].between(idade_min, idade_max)) &
    (df['genero'].isin(genero)) &
    (df['estado_civil'].isin(estado_civil)) &
    (df['nivel_escolaridade'].isin(escolaridade))
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com esses filtros.")
    st.stop()

# -------------------------
# Abas
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Perfil Demográfico",
    "Perfil Clínico",
    "Tratamento & Experiência",
    "Conclusões"
])

# =========================
# ABA 1 - PERFIL DEMOGRÁFICO
# =========================
with tab1:

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de pacientes", df_filtrado.shape[0])
    col2.metric("Idade média", f"{df_filtrado['idade'].mean():.0f} anos")
    col3.metric("Estresse médio", f"{df_filtrado['nivel_estresse_0_10'].mean():.1f}")

    st.markdown("---")

    fig = px.violin(
        df_filtrado,
        y="idade",
        x="genero",
        color="genero",
        box=True,
        points="outliers",
        title="Distribuição da idade dos pacientes por gênero",
        labels={"idade": "Idade", "genero": "Gênero"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    genero_counts = df_filtrado['genero'].value_counts().reset_index()
    genero_counts.columns = ['Gênero', 'Quantidade']

    fig = px.pie(
        genero_counts,
        names='Gênero',
        values='Quantidade',
        hole=0.5,
        title="Distribuição por gênero",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        estado_civil_counts = df_filtrado['estado_civil'].value_counts().reset_index()
        estado_civil_counts.columns = ['Estado civil', 'Quantidade']

        fig = px.treemap(
            estado_civil_counts,
            path=['Estado civil'],
            values='Quantidade',
            color='Quantidade',
            color_continuous_scale='Blues',
            title="Distribuição por estado civil",
        )
        fig.update_traces(textinfo="label+value+percent root")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        escolaridade_counts = (
            df_filtrado['nivel_escolaridade']
            .value_counts()
            .reset_index()
        )
        escolaridade_counts.columns = ['Escolaridade', 'Quantidade']
        escolaridade_counts = escolaridade_counts.sort_values('Quantidade', ascending=False)

        fig = px.funnel(
            escolaridade_counts,
            x='Quantidade',
            y='Escolaridade',
            color='Escolaridade',
            title="Distribuição por nível de escolaridade",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


# =========================
# ABA 2 - PERFIL CLÍNICO
# =========================
with tab2:

    diagnostico_counts = (
        df_filtrado['diagnostico_principal']
        .value_counts()
        .reset_index()
        .sort_values('count')
    )
    diagnostico_counts.columns = ['Diagnóstico principal', 'Quantidade']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=diagnostico_counts['Quantidade'],
        y=diagnostico_counts['Diagnóstico principal'],
        mode='markers',
        marker=dict(size=16, color=diagnostico_counts['Quantidade'], colorscale='Teal', showscale=False),
        name='',
    ))
    for _, row in diagnostico_counts.iterrows():
        fig.add_shape(
            type='line',
            x0=0, x1=row['Quantidade'],
            y0=row['Diagnóstico principal'], y1=row['Diagnóstico principal'],
            line=dict(color='rgba(0,150,150,0.4)', width=3),
        )
    fig.update_layout(
        title="Quantidade de pacientes por diagnóstico",
        xaxis_title="Quantidade",
        yaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)

    uso_medicacao_counts = df_filtrado['uso_medicacao'].value_counts(normalize=True) * 100
    uso_medicacao_counts = uso_medicacao_counts.reset_index()
    uso_medicacao_counts.columns = ['Uso de medicação', 'Porcentagem']

    col_med1, col_med2 = st.columns([2, 1])

    with col_med1:
        fig = px.pie(
            uso_medicacao_counts,
            names='Uso de medicação',
            values='Porcentagem',
            hole=0.5,
            title="Uso de medicação (%)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_med2:
        pct_sim = uso_medicacao_counts.loc[
            uso_medicacao_counts['Uso de medicação'].str.lower().isin(['sim', 'yes', 'true', '1']),
            'Porcentagem'
        ]
        pct_val = pct_sim.values[0] if len(pct_sim) else uso_medicacao_counts['Porcentagem'].iloc[0]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(pct_val, 1),
            number={
                'suffix': '%',
                'font': {'size': 36},
                'valueformat': '.1f'
            },
            title={'text': "Usa medicação"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': 'teal'},
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(0,150,150,0.1)'},
                    {'range': [50, 100], 'color': 'rgba(0,150,150,0.2)'},
                ],
            }
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=60, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Consultas por ano",
            f"{df_filtrado['numero_consultas_ano'].mean():.0f}"
        )

    with col2:
        st.metric(
            "Nível médio de estresse",
            f"{df_filtrado['nivel_estresse_0_10'].mean():.0f}"
        )

    fig = px.histogram(
        df_filtrado,
        x='faltas_consulta',
        color='faltas_consulta',
        color_discrete_sequence=px.colors.sequential.Teal,
        title="Distribuição de pacientes por número de faltas",
        labels={'faltas_consulta': 'Número de faltas', 'count': 'Quantidade'},
    )
    fig.update_layout(showlegend=False, bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

    estresse_por_diag = (
        df_filtrado
        .groupby('diagnostico_principal')['nivel_estresse_0_10']
        .mean()
        .reset_index()
    )
    estresse_por_diag.columns = ['Diagnóstico', 'Estresse médio']

    fig = px.bar_polar(
        estresse_por_diag,
        r='Estresse médio',
        theta='Diagnóstico',
        color='Diagnóstico',
        title="Nível médio de estresse por diagnóstico",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template='plotly_white',
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.box(
        df_filtrado,
        x="diagnostico_principal",
        y="nivel_estresse_0_10",
        color="diagnostico_principal",
        title="Distribuição do estresse por diagnóstico",
        points="outliers",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.strip(
        df_filtrado,
        x="diagnostico_principal",
        y="numero_consultas_ano",
        color="diagnostico_principal",
        title="Distribuição de consultas por diagnóstico",
        labels={"diagnostico_principal": "Diagnóstico", "numero_consultas_ano": "Consultas/ano"},
    )
    fig.update_traces(jitter=0.4, marker_size=4, opacity=0.5)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    diag_genero = (
        df_filtrado
        .groupby(['genero', 'diagnostico_principal'])
        .size()
        .reset_index(name='Quantidade')
    )

    fig = px.sunburst(
        diag_genero,
        path=['genero', 'diagnostico_principal'],
        values='Quantidade',
        color='diagnostico_principal',
        title="Distribuição de diagnósticos por gênero",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================
# ABA 3 - TRATAMENTO
# =========================
with tab3:

    satisfacao_counts = (
        df_filtrado['satisfacao_tratamento_1_5']
        .value_counts()
        .reset_index()
        .sort_values('satisfacao_tratamento_1_5')
    )
    satisfacao_counts.columns = ['Satisfação', 'Quantidade']
    satisfacao_counts['Rótulo'] = satisfacao_counts['Satisfação'].apply(
        lambda x: f"⭐ {x}"
    )
    satisfacao_counts['Pct'] = (
        satisfacao_counts['Quantidade'] / satisfacao_counts['Quantidade'].sum() * 100
    ).round(1)

    fig = px.bar(
        satisfacao_counts,
        x='Quantidade',
        y='Rótulo',
        orientation='h',
        color='Satisfação',
        color_continuous_scale='RdYlGn',
        text=satisfacao_counts['Pct'].apply(lambda x: f"{x}%"),
        title="Satisfação com tratamento (escala 1–5)",
        labels={'Rótulo': 'Nota de satisfação'},
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    relacao = (
        df_filtrado
        .groupby('numero_consultas_ano')['satisfacao_tratamento_1_5']
        .mean()
        .reset_index()
    )

    fig = px.line(
        relacao,
        x='numero_consultas_ano',
        y='satisfacao_tratamento_1_5',
        markers=True,
        title="Média de satisfação por número de consultas anuais",
        labels={
            'numero_consultas_ano': 'Consultas por ano',
            'satisfacao_tratamento_1_5': 'Satisfação média (1–5)',
        },
        line_shape='spline',
    )
    fig.update_traces(
        marker=dict(size=8, color='teal'),
        line=dict(color='teal', width=2.5),
    )
    st.plotly_chart(fig, use_container_width=True)

    heat = (
        df_filtrado
        .groupby(['numero_consultas_ano', 'satisfacao_tratamento_1_5'])
        .size()
        .reset_index(name='Quantidade')
    )

    fig = px.density_heatmap(
        heat,
        x="numero_consultas_ano",
        y="satisfacao_tratamento_1_5",
        z="Quantidade",
        color_continuous_scale="Teal",
        title="Concentração: Consultas vs Satisfação",
        labels={
            'numero_consultas_ano': 'Consultas por ano',
            'satisfacao_tratamento_1_5': 'Satisfação (1–5)',
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    genero_satisfacao = (
        df_filtrado
        .groupby(['genero', 'satisfacao_tratamento_1_5'])
        .size()
        .reset_index(name='Quantidade')
    )

    genero_satisfacao['Proporção (%)'] = (
        genero_satisfacao
        .groupby('genero')['Quantidade']
        .transform(lambda x: x / x.sum() * 100)
    )

    fig = px.bar(
        genero_satisfacao,
        x='satisfacao_tratamento_1_5',
        y='Proporção (%)',
        color='genero',
        barmode='group',
        title="Proporção de satisfação com tratamento por gênero",
        labels={
            'satisfacao_tratamento_1_5': 'Nota de satisfação (1–5)',
            'genero': 'Gênero',
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig, use_container_width=True)

    import numpy as np

    cores = px.colors.qualitative.Set2
    generos_unicos = df_filtrado['genero'].unique()
    cor_map = {g: cores[i % len(cores)] for i, g in enumerate(generos_unicos)}

    fig = go.Figure()
    for gen in generos_unicos:
        sub = df_filtrado[df_filtrado['genero'] == gen]
        fig.add_trace(go.Scatter(
            x=sub['nivel_estresse_0_10'],
            y=sub['satisfacao_tratamento_1_5'],
            mode='markers',
            name=gen,
            marker=dict(color=cor_map[gen], opacity=0.5, size=6),
        ))
        x_vals = sub['nivel_estresse_0_10'].dropna()
        y_vals = sub['satisfacao_tratamento_1_5'].dropna()
        idx = x_vals.index.intersection(y_vals.index)
        if len(idx) > 1:
            coef = np.polyfit(x_vals[idx], y_vals[idx], 1)
            x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
            y_line = np.polyval(coef, x_line)
            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=f"Tendência ({gen})",
                line=dict(color=cor_map[gen], width=2, dash='dash'),
                showlegend=False,
            ))

    fig.update_layout(
        title="Relação entre estresse e satisfação com o tratamento",
        xaxis_title="Nível de estresse (0–10)",
        yaxis_title="Satisfação (1–5)",
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================
# ABA 4 - CONCLUSÕES (INALTERADA)
# =========================
with tab4:

    st.markdown("""
A presente análise exploratória foi conduzida com base em uma amostra fictícia composta por 2.000 pacientes, com idade média aproximada de 44 anos. A distribuição por gênero mostrou equilíbrio entre os grupos masculino e feminino, enquanto o grupo não binário apresentou menor representatividade na amostra.

Em relação ao estado civil, observou-se maior concentração de pacientes solteiros e casados, sendo o grupo de viúvos o menos frequente. Quanto ao nível de escolaridade, indivíduos com ensino superior completo (graduação) representaram a maior parcela da amostra, enquanto pacientes com ensino médio apresentaram menor proporção relativa.

No que se refere ao diagnóstico principal, o Transtorno de Estresse Pós-Traumático (TEPT) apresentou a maior incidência entre os pacientes, seguido por quadros de depressão. O Transtorno do Pânico foi o diagnóstico menos frequente na amostra analisada.

A análise do uso de medicação indicou que aproximadamente 55,65% dos pacientes fazem uso de tratamento farmacológico, evidenciando predominância dessa abordagem terapêutica na amostra. O nível médio de estresse reportado foi 5 em uma escala de 0 a 10, indicando intensidade moderada.

Em relação à adesão ao tratamento, verificou-se que a maioria dos pacientes registrou apenas uma falta anual, não sendo observado padrão crítico de evasão. Quanto à intensidade do estresse por diagnóstico, pacientes com diagnóstico de ansiedade apresentaram os maiores níveis médios de estresse.

A distribuição proporcional dos diagnósticos por gênero revelou maior incidência de ansiedade e transtorno bipolar na população não binária, enquanto o TEPT apresentou maior concentração relativa entre mulheres. No que se refere à satisfação com o tratamento (escala de 1 a 5), a maioria dos pacientes atribuiu nota 4, indicando percepção predominantemente positiva (entre "bom" e "muito bom"). Entretanto, o grupo não binário apresentou níveis médios de satisfação inferiores aos demais grupos.

De modo geral, os resultados indicam padrões coerentes entre diagnóstico, percepção de estresse, uso de medicação e satisfação com o tratamento, permitindo uma compreensão estruturada do perfil clínico da amostra analisada.
""")

    st.markdown("----")

    st.markdown(f"""
**Autor:** Samuel de Andrade da Silva  
**Versão:** 1.0  
**Contato:** [samuelsilva00935@gmail.com](mailto:samuelsilva00935@gmail.com)

**Observação:** Dados fictícios utilizados exclusivamente para fins educacionais e prática em análise de dados.  
**Licença:** MIT
""")

























