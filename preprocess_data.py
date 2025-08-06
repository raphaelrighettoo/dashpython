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
COLUNA_TRIMESTRE = 'trimestre'
COLUNA_ANO = 'ano' # Coluna para análise anual
# -----------------------------------

print("Iniciando o pré-processamento dos dados...")

# Carrega o ficheiro de dados completo
try:
    df = pd.read_csv('dados.csv', sep=';')
except Exception:
    df = pd.read_csv('dados.csv', sep=',')

print("Ficheiro CSV carregado. Iniciando limpeza...")

# --- LIMPEZA E PREPARAÇÃO DOS DADOS (VERSÃO ROBUSTA) ---
df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], dayfirst=True, errors='coerce')

numeric_values = pd.to_numeric(df[COLUNA_VALOR_VENDA], errors='coerce')
text_values = df[COLUNA_VALOR_VENDA][numeric_values.isna()]
cleaned_values = (
    text_values.astype(str)
    .str.replace('R$', '', regex=False)
    .str.strip()
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
)
cleaned_numeric = pd.to_numeric(cleaned_values, errors='coerce')
df[COLUNA_VALOR_VENDA] = numeric_values.fillna(cleaned_numeric)

# Garante que as colunas essenciais não tenham valores nulos
df.dropna(subset=[COLUNA_DATA, COLUNA_VALOR_VENDA, COLUNA_TRIMESTRE, COLUNA_ANO], inplace=True)

print(f"Limpeza concluída. {len(df)} linhas válidas encontradas para processamento.")

# --- CÁLCULO DAS AGREGAÇÕES E SALVAMENTO ---

# 1. KPIs (Totais gerais)
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

# 2. Vendas por Regional (trimestral)
df_regional_trimestral = df.groupby([COLUNA_REGIONAL, COLUNA_TRIMESTRE])[COLUNA_VALOR_VENDA].sum().reset_index()
df_regional_trimestral.to_csv('summary_regional_trimestral.csv', index=False)
print("Resumo por regional (trimestral) salvo em summary_regional_trimestral.csv")

# 3. Top 10 Consultores (total geral)
df_consultor = df.groupby(COLUNA_CONSULTOR)[COLUNA_VALOR_VENDA].sum().nlargest(10).sort_values().reset_index()
df_consultor.to_csv('summary_consultor.csv', index=False)
print("Resumo por consultor salvo em summary_consultor.csv")

# 4. Vendas por Unidade de Negócio (trimestral)
df_unidade_trimestral = df.groupby([COLUNA_UNIDADE_NEGOCIO, COLUNA_TRIMESTRE])[COLUNA_VALOR_VENDA].sum().reset_index()
df_unidade_trimestral.to_csv('summary_unidade_trimestral.csv', index=False)
print("Resumo por unidade de negócio (trimestral) salvo em summary_unidade_trimestral.csv")

# 5. Evolução Trimestral
df_trimestral = df.groupby(COLUNA_TRIMESTRE)[COLUNA_VALOR_VENDA].sum().reset_index()
df_trimestral['ano'] = '20' + df_trimestral[COLUNA_TRIMESTRE].str.extract(r'(\d+)$').fillna('0')
df_trimestral['trimestre_num'] = df_trimestral[COLUNA_TRIMESTRE].str.extract(r'(\d+)Tri').fillna('0')
df_trimestral = df_trimestral.sort_values(by=['ano', 'trimestre_num'])
df_trimestral.to_csv('summary_trimestral.csv', index=False)
print("Resumo trimestral salvo em summary_trimestral.csv")

# 6. Evolução Anual (NOVO)
df_anual = df.groupby(COLUNA_ANO)[COLUNA_VALOR_VENDA].sum().reset_index()
df_anual.to_csv('summary_anual.csv', index=False)
print("Resumo anual salvo em summary_anual.csv")

print("Pré-processamento concluído com sucesso!")
