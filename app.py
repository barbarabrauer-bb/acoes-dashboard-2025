import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Análise de Ações 2025", page_icon="📈", layout="wide")

st.title("📈 Dashboard de Ações Brasileiras — 2025")
st.markdown("Análise de **VALE3**, **BBSE3** e **PRIO3** ao longo de 2025.")

ACOES = {
    "VALE3": "VALE3.SA",
    "BBSE3": "BBSE3.SA",
    "PRIO3": "PRIO3.SA",
}

CORES = {
    "VALE3": "#1f77b4",
    "BBSE3": "#ff7f0e",
    "PRIO3": "#2ca02c",
}

with st.sidebar:
    st.header("Filtros")
    acoes_selecionadas = []
    for nome in ACOES:
        if st.checkbox(nome, value=True):
            acoes_selecionadas.append(nome)

    st.markdown("---")
    data_inicio = st.date_input("Data início", value=date(2025, 1, 2), min_value=date(2025, 1, 2), max_value=date(2025, 12, 31))
    data_fim = st.date_input("Data fim", value=min(date.today(), date(2025, 12, 31)), min_value=date(2025, 1, 2), max_value=date(2025, 12, 31))

if not acoes_selecionadas:
    st.warning("Selecione ao menos uma ação no painel lateral.")
    st.stop()

@st.cache_data(ttl=3600)
def carregar_dados(tickers, inicio, fim):
    dados = {}
    for nome, ticker in tickers.items():
        df = yf.download(ticker, start=inicio, end=fim, progress=False, auto_adjust=True)
        if not df.empty:
            df.index = pd.to_datetime(df.index)
            dados[nome] = df
    return dados

with st.spinner("Carregando dados do Yahoo Finance..."):
    dados = carregar_dados(
        {k: ACOES[k] for k in acoes_selecionadas},
        data_inicio.strftime("%Y-%m-%d"),
        data_fim.strftime("%Y-%m-%d"),
    )

if not dados:
    st.error("Não foi possível carregar dados. Verifique sua conexão.")
    st.stop()

# --- Gráfico 1: Cotação (linha) ---
st.subheader("Cotação — Preço de Fechamento (R$)")
fig_linha = go.Figure()
for nome, df in dados.items():
    close = df["Close"].squeeze()
    fig_linha.add_trace(go.Scatter(
        x=close.index,
        y=close.values,
        name=nome,
        line=dict(color=CORES[nome], width=2),
        hovertemplate="%{x|%d/%m/%Y}<br>R$ %{y:.2f}<extra>" + nome + "</extra>",
    ))
fig_linha.update_layout(
    xaxis_title="Data",
    yaxis_title="Preço (R$)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=420,
)
st.plotly_chart(fig_linha, use_container_width=True)

# --- Gráfico 2: Performance acumulada (%) ---
st.subheader("Performance Acumulada (%)")
fig_perf = go.Figure()
for nome, df in dados.items():
    close = df["Close"].squeeze().dropna()
    if len(close) > 0:
        perf = (close / close.iloc[0] - 1) * 100
        fig_perf.add_trace(go.Scatter(
            x=perf.index,
            y=perf.values,
            name=nome,
            line=dict(color=CORES[nome], width=2),
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:.2f}%<extra>" + nome + "</extra>",
        ))
fig_perf.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
fig_perf.update_layout(
    xaxis_title="Data",
    yaxis_title="Retorno acumulado (%)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=420,
)
st.plotly_chart(fig_perf, use_container_width=True)

# --- Gráfico 3: Barras de variação diária por ação ---
st.subheader("Variação Diária (R$)")
for nome, df in dados.items():
    close = df["Close"].squeeze()
    daily_change = close.diff()
    colors = ["#2ca02c" if x >= 0 else "#d62728" for x in daily_change]

    fig_barras = go.Figure(go.Bar(
        x=daily_change.index,
        y=daily_change.values,
        name=nome,
        marker=dict(color=colors),
        hovertemplate="%{x|%d/%m/%Y}<br>Variação: R$ %{y:.2f}<extra>" + nome + "</extra>",
    ))
    fig_barras.update_layout(
        title=nome,
        xaxis_title="Data",
        yaxis_title="Variação (R$)",
        height=380,
        showlegend=False,
    )
    st.plotly_chart(fig_barras, use_container_width=True)

# --- Tabela de Resumo ---
st.subheader("Resumo do Período")
resumo = []
for nome, df in dados.items():
    close = df["Close"].squeeze().dropna()
    if len(close) < 2:
        continue
    preco_inicial = close.iloc[0]
    preco_final = close.iloc[-1]
    variacao = (preco_final / preco_inicial - 1) * 100
    maior_alta = close.pct_change().max() * 100
    maior_queda = close.pct_change().min() * 100
    resumo.append({
        "Ação": nome,
        "Preço Inicial (R$)": f"{preco_inicial:.2f}",
        "Preço Atual (R$)": f"{preco_final:.2f}",
        "Variação (%)": f"{variacao:+.2f}%",
        "Maior Alta Diária": f"{maior_alta:+.2f}%",
        "Maior Queda Diária": f"{maior_queda:+.2f}%",
    })

if resumo:
    df_resumo = pd.DataFrame(resumo).set_index("Ação")
    st.dataframe(df_resumo, use_container_width=True)

st.caption("Dados fornecidos pelo Yahoo Finance via yfinance. Atualizado a cada hora.")
