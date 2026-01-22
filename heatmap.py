import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# 1) LEITURA DO CSV
# =====================================================
file_path = "combinados/exp_renan_2025.csv"
df = pd.read_csv(file_path, sep=",")

x = df.iloc[:, 0].values               # número de onda
Z = df.iloc[:, 1:].values.T            # espectros x pontos
labels = df.columns[1:]
n_espectros = Z.shape[0]

print(f"Heatmap com {n_espectros} espectros")

# =====================================================
# 2) FIGURA
# =====================================================
fig, ax = plt.subplots(figsize=(9, 6))

# =====================================================
# 3) HEATMAP
# =====================================================
im = ax.imshow(
    Z,
    aspect="auto",
    cmap="inferno",        # bom para IR
    origin="lower",        # primeiro espectro embaixo
    extent=[x.min(), x.max(), 0, n_espectros]
)

# =====================================================
# 4) AJUSTES DOS EIXOS
# =====================================================
ax.set_xlabel("Número de onda (cm⁻¹)")
ax.set_ylabel("Espectro / Tempo")

ax.invert_xaxis()  # padrão IR

# ticks no eixo Y (opcional)
step = max(1, n_espectros // 10)
ax.set_yticks(np.arange(0, n_espectros, step))
ax.set_yticklabels(labels[::step])

# =====================================================
# 5) BARRA DE CORES
# =====================================================
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Absorbância")

plt.tight_layout()
plt.savefig("heatmap_exp_renan_2025.png", dpi=300)
plt.show()
