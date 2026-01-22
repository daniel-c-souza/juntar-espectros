import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation, PillowWriter

# =====================================================
# 1) LEITURA DO CSV
# =====================================================
file_path = "saida_csv/jao_cobbind_consolidado.csv"
df = pd.read_csv(file_path, sep=",")

x = df.iloc[:, 0].values
y = df.iloc[:, 1:].values
labels = df.columns[1:]
n_espectros = y.shape[1]

print(f"Total de espectros: {n_espectros}")

# =====================================================
# 2) FIGURA E EIXOS
# =====================================================
fig, ax = plt.subplots(figsize=(8, 5))
plt.subplots_adjust(bottom=0.25)

# Todos os espectros em cinza
for spec in y.T:
    ax.plot(x, spec, color='gray', alpha=0.4, lw=1)

# Espectro destacado
highlight, = ax.plot(x, y[:, 0], color='red', lw=2.0)

ax.set_xlabel("Número de onda (cm⁻¹)")
ax.set_ylabel("Absorbância")
ax.set_title(f"Tempo: {labels[0]} (1/{n_espectros})")

ax.invert_xaxis()
ax.set_xlim(x.min(), x.max())
ax.set_ylim(y.min()*1.05, y.max()*1.05)
ax.grid(True, alpha=0.3)

# =====================================================
# 3) SLIDER
# =====================================================
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
slider = Slider(
    ax_slider,
    "Espectro",
    0,
    n_espectros - 1,
    valinit=0,
    valstep=1
)

def update_slider(val):
    i = int(slider.val)
    highlight.set_ydata(y[:, i])
    ax.set_title(f"Tempo: {labels[i]} ({i+1}/{n_espectros})")
    fig.canvas.draw_idle()

slider.on_changed(update_slider)

# =====================================================
# 4) CONTROLE POR TECLADO
# =====================================================
def on_key(event):
    current = int(slider.val)
    if event.key == "right":
        slider.set_val(min(current + 1, n_espectros - 1))
    elif event.key == "left":
        slider.set_val(max(current - 1, 0))

fig.canvas.mpl_connect("key_press_event", on_key)

# =====================================================
# 5) FUNÇÃO PARA ANIMAÇÃO (GIF)
# =====================================================
def update_frame(i):
    highlight.set_ydata(y[:, i])
    ax.set_title(f"Tempo: {labels[i]} ({i+1}/{n_espectros})")
    return highlight,

# =====================================================
# 6) CRIAR E SALVAR GIF
# =====================================================
print("🎞️ Gerando GIF... aguarde.")
ani = FuncAnimation(
    fig,
    update_frame,
    frames=range(n_espectros),
    interval=100,     # ms entre frames
    blit=False,
    repeat=False
)

writer = PillowWriter(fps=10)
ani.save("EXP_RENAN_2025_espectros.gif", writer=writer)

print("✅ GIF gerado com sucesso!")

# =====================================================
# 7) MOSTRAR INTERFACE INTERATIVA
# =====================================================
plt.show()
