# gerar_dashboard.py
import pandas as pd
import plotly.express as px
import panel as pn
import json

# --- CONFIGURAÇÃO DAS COLUNAS ---
# Os nomes aqui devem corresponder aos nomes definidos no script de pré-processamento.
COLUNA_DATA = 'data da venda'
COLUNA_VALOR_VENDA = 'valor total da venda'
COLUNA_REGIONAL = 'regional'
COLUNA_CONSULTOR = 'consultor'
COLUNA_UNIDADE_NEGOCIO = 'unid negocio'
COLUNA_TRIMESTRE = 'trimestre' # Coluna para análise trimestral
# -----------------------------------

print("Iniciando a geração do dashboard a partir dos dados pré-processados...")

# Garante que a extensão do Plotly seja carregada
pn.extension('plotly')

# --- CARREGAMENTO DOS DADOS PRÉ-PROCESSADOS ---
with open('kpis.json', 'r') as f:
    kpis = json.load(f)

# Carrega os novos ficheiros de resumo trimestrais
df_regional_trimestral = pd.read_csv('summary_regional_trimestral.csv')
df_consultor = pd.read_csv('summary_consultor.csv') # Mantido como total
df_unidade_trimestral = pd.read_csv('summary_unidade_trimestral.csv')
df_trimestral = pd.read_csv('summary_trimestral.csv')
print("Arquivos de resumo carregados.")

# --- CRIAÇÃO DOS GRÁFICOS (AGORA COM VISÃO TRIMESTRAL) ---

# Gráfico 1: Vendas por Regional (agrupado por trimestre)
vendas_regional = px.bar(
    df_regional_trimestral, x=COLUNA_REGIONAL, y=COLUNA_VALOR_VENDA, color=COLUNA_TRIMESTRE,
    title='Faturamento por Regional (Trimestral)', text_auto='.2s', barmode='group'
).update_layout(yaxis_title='Faturamento (R$)', xaxis_title='Regional')

# Gráfico 2: Top 10 Consultores (mantido como total)
vendas_consultor = px.bar(
    df_consultor, x=COLUNA_VALOR_VENDA, y=COLUNA_CONSULTOR,
    title='Top 10 Consultores por Faturamento (Geral)', text_auto='.2s', orientation='h'
).update_layout(xaxis_title='Faturamento (R$)', yaxis_title='Consultor')

# Gráfico 3: Vendas por Unidade de Negócio (empilhado por trimestre)
vendas_unidade_negocio = px.bar(
    df_unidade_trimestral, x=COLUNA_UNIDADE_NEGOCIO, y=COLUNA_VALOR_VENDA, color=COLUNA_TRIMESTRE,
    title='Faturamento por Unidade de Negócio (Trimestral)'
).update_layout(yaxis_title='Faturamento (R$)', xaxis_title='Unidade de Negócio')

# Gráfico 4: Evolução Trimestral do Faturamento
evolucao_vendas = px.line(
    df_trimestral, x=COLUNA_TRIMESTRE, y=COLUNA_VALOR_VENDA,
    title='Evolução Trimestral do Faturamento', markers=True, text=COLUNA_VALOR_VENDA
).update_traces(textposition="bottom right").update_layout(xaxis_title='Trimestre', yaxis_title='Faturamento (R$)')
print("Gráficos criados.")

# --- MONTAGEM DO LAYOUT DO DASHBOARD ---
kpi_faturamento = pn.indicators.Number(name='Faturamento Total (Geral)', value=kpis['faturamento_total'], format='R$ {value:,.2f}')
kpi_ticket_medio = pn.indicators.Number(name='Ticket Médio (Geral)', value=kpis['ticket_medio'], format='R$ {value:,.2f}')
kpi_total_contratos = pn.indicators.Number(name='Total de Contratos (Geral)', value=kpis['total_contratos'], format='{value:,.0f}')

dashboard = pn.Column(
    pn.Row(
        pn.pane.Markdown("# Dashboard de Vendas Estratégico", styles={'font-size': '24pt', 'margin-left': '20px'}),
        align='center'
    ),
    pn.Row(
        kpi_faturamento, kpi_ticket_medio, kpi_total_contratos,
        align='center', styles={'gap': '2em'}
    ),
    pn.layout.Divider(),
    pn.Row(
        pn.Column(vendas_regional, evolucao_vendas),
        pn.Column(vendas_consultor, vendas_unidade_negocio)
    ),
    sizing_mode='stretch_width'
)

# --- SALVAR O DASHBOARD ---
dashboard.save(
    'index.html',
    embed=True,
    title='Dashboard de Vendas'
)

print("Dashboard 'index.html' gerado com sucesso!")
