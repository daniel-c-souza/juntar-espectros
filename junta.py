import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
import matplotlib.cm as cm
# Diretório base dos experimentos
BASE_DIR = "exps"

# Diretórios de saída
CSV_DIR = "saida_csv"
PLOT_DIR = "plots"

# Cria as pastas de saída se não existirem
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# Lista os experimentos disponíveis
experiments = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

if not experiments:
    raise ValueError("Nenhum experimento encontrado no diretório 'exps'.")

print("Experimentos disponíveis:")
for i, exp in enumerate(experiments, 1):
    print(f"{i}. {exp}")

idx = int(input("\nSelecione o experimento (número): ")) - 1
exp_name = experiments[idx]
exp_path = os.path.join(BASE_DIR, exp_name)

# Lista arquivos CSV no experimento
csv_files = sorted([f for f in os.listdir(exp_path) if f.lower().endswith(".csv")])

if not csv_files:
    raise ValueError(f"Nenhum arquivo CSV encontrado em {exp_path}")

# -------------------------------
# Função robusta para leitura dos espectros
# -------------------------------
def ler_espectro(path):
    """Lê um arquivo de espectro, ignorando cabeçalhos e metadados."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Mantém apenas as linhas numéricas com separador ';'
    data_lines = []
    for line in lines:
        line = line.strip()
        if re.match(r"^[0-9]+(\.[0-9]+)?;[-+]?[0-9]*\.?[0-9]+$", line):
            data_lines.append(line)

    if not data_lines:
        raise ValueError(f"Nenhuma linha de dados numéricos encontrada em {path}")

    # Converte as linhas numéricas em DataFrame
    data_str = "\n".join(data_lines)
    df = pd.read_csv(StringIO(data_str), sep=";", header=None, names=["Wavenumber", "Absorbance"], decimal=".")
    return df

# -------------------------------
# Lê e armazena todos os espectros de uma vez
# -------------------------------
dataframes = []
col_names = []

for csv_file in csv_files:
    path = os.path.join(exp_path, csv_file)
    df = ler_espectro(path)

    # Extrai número final do nome (ex: 001 → tempo 0 min, 002 → 3 min, etc.)
    match = re.search(r"(\d{3})\.csv$", csv_file)
    if match:
        amostra_num = int(match.group(1))
        tempo_min = (amostra_num - 1)  # assume coleta a cada 3 min
        col_name = f"{tempo_min} min"
    else:
        col_name = os.path.splitext(csv_file)[0]

    df = df.rename(columns={"Absorbance": col_name})
    df = df[["Wavenumber", col_name]]
    dataframes.append(df)
    col_names.append(col_name)

# -------------------------------
# Junta tudo de uma vez (sem fragmentação)
# -------------------------------
df_combined = dataframes[0][["Wavenumber"]]
abs_data = [df[col] for df, col in zip(dataframes, col_names)]
df_combined = pd.concat([df_combined] + abs_data, axis=1)

# -------------------------------
# Salva CSV consolidado em pasta separada
# -------------------------------
output_csv = os.path.join(CSV_DIR, f"{exp_name}_consolidado.csv")
df_combined.to_csv(output_csv, index=False)
print(f"\n✅ Arquivo consolidado salvo em: {output_csv}")

# -------------------------------
# Gera e salva o gráfico em pasta separada
# -------------------------------
plt.figure(figsize=(10, 7))

# Cria gradiente de cores (do azul → vermelho)
num_curvas = len(df_combined.columns) - 1
colors = cm.coolwarm(np.linspace(0, 1, num_curvas))

for i, col in enumerate(df_combined.columns[1:]):
    plt.plot(df_combined["Wavenumber"], df_combined[col], label=col, color=colors[i])

plt.xlabel("Número de onda (cm⁻¹)")
plt.ylabel("Absorbância")
plt.title(f"Espectros - {exp_name}")


plt.tight_layout()
output_fig = os.path.join(PLOT_DIR, f"{exp_name}_espectros.png")
plt.savefig(output_fig, dpi=300, bbox_inches="tight")
plt.show()

print(f"✅ Gráfico salvo em: {output_fig}")
