# preprocess_data.py
import pandas as pd
import json

# --- CONFIGURAÇÃO DAS COLUNAS ---
# Garanta que estes nomes correspondem EXATAMENTE ao seu ficheiro CSV.
COLUNA_DATA = 'data da venda'
COLUNA_VALOR_VENDA = 'valor total da venda'
COLUNA_REGIONAL = 'regional'
COLUNA_CONSULTOR = 'consultor'
COLUNA_UNIDADE_NEGOCIO = 'unid negocio'
# -----------------------------------

print("Iniciando o pré-processamento dos dados...")

# Carrega o ficheiro de dados completo
try:
    df = pd.read_csv('dados.csv', sep=';')
except Exception:
    df = pd.read_csv('dados.csv', sep=',')

print("Ficheiro CSV carregado. Iniciando limpeza...")

# --- LIMPEZA E PREPARAÇÃO DOS DADOS (VERSÃO ROBUSTA) ---
# 1. Converte a coluna de data
df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], dayfirst=True, errors='coerce')

# 2. Tenta converter a coluna de valor para número diretamente.
# 'coerce' transformará em NaN (Not a Number) o que não for um número puro.
numeric_values = pd.to_numeric(df[COLUNA_VALOR_VENDA], errors='coerce')

# 3. Para os valores que falharam (são NaN), tenta a limpeza de texto.
# Isto só afeta as células que não eram números puros (ex: continham "R$").
text_values = df[COLUNA_VALOR_VENDA][numeric_values.isna()]
cleaned_values = (
    text_values.astype(str)
    .str.replace('R$', '', regex=False)
    .str.strip()
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
)
cleaned_numeric = pd.to_numeric(cleaned_values, errors='coerce')

# 4. Combina os resultados: usa os valores que já eram numéricos
# e preenche os que não eram com a versão limpa.
df[COLUNA_VALOR_VENDA] = numeric_values.fillna(cleaned_numeric)

# 5. Remove linhas onde a conversão de data ou valor falhou
df.dropna(subset=[COLUNA_DATA, COLUNA_VALOR_VENDA], inplace=True)

print(f"Limpeza concluída. {len(df)} linhas válidas encontradas para processamento.")

# --- CÁLCULO DAS AGREGAÇÕES E SALVAMENTO ---

# 1. KPIs
faturamento_total = df[COLUNA_VALOR_VENDA].sum()
total_contratos = len(df)
ticket_medio = faturamento_total / total_contratos if total_contratos > 0 else 0

kpis = {
    "faturamento_total": float(faturamento_total),
    "total_contratos": int(total_contratos),
    "ticket_medio": float(ticket_medio)
}
with open('kpis.json', 'w') as f:
    json.dump(kpis, f)
print("KPIs salvos em kpis.json")

# 2. Vendas por Regional
df_regional = df.groupby(COLUNA_REGIONAL)[COLUNA_VALOR_VENDA].sum().sort_values(ascending=False).reset_index()
df_regional.to_csv('summary_regional.csv', index=False)
print("Resumo por regional salvo em summary_regional.csv")

# 3. Top 10 Consultores
df_consultor = df.groupby(COLUNA_CONSULTOR)[COLUNA_VALOR_VENDA].sum().nlargest(10).sort_values().reset_index()
df_consultor.to_csv('summary_consultor.csv', index=False)
print("Resumo por consultor salvo em summary_consultor.csv")

# 4. Vendas por Unidade de Negócio
df_unidade = df.groupby(COLUNA_UNIDADE_NEGOCIO)[COLUNA_VALOR_VENDA].sum().reset_index()
df_unidade.to_csv('summary_unidade.csv', index=False)
print("Resumo por unidade de negócio salvo em summary_unidade.csv")

# 5. Evolução Mensal
df_mensal = df.set_index(COLUNA_DATA).groupby(pd.Grouper(freq='ME'))[COLUNA_VALOR_VENDA].sum().reset_index()
df_mensal.to_csv('summary_mensal.csv', index=False)
print("Resumo mensal salvo em summary_mensal.csv")

print("Pré-processamento concluído com sucesso!")
