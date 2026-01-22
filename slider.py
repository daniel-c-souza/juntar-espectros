import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# === Leitura do CSV ===
file_path = "saida_csv/jao_cobbind_consolidado.csv"
df = pd.read_csv(file_path, sep=",")

x = df.iloc[:, 0].values
y = df.iloc[:, 1:].values
labels = df.columns[1:]

# === Criar figura e eixos ===
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

# Todos os espectros em cinza
lines = []
for spec in y.T:
    line, = ax.plot(x, spec, color='gray', alpha=0.4, lw=1)
    lines.append(line)

# Espectro destacado
highlight, = ax.plot(x, y[:, 0], color='red', lw=2.0)
ax.set_xlabel("Número de onda (cm⁻¹)")
ax.set_ylabel("Absorbância")
ax.set_title(f"Tempo: {labels[0]}")
ax.invert_xaxis()  

ax.set_xlim(x.min(), x.max())
ax.set_ylim(y.min()*1.05, y.max()*1.05)

# === Slider ===
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
slider = Slider(ax_slider, "Espectro", 0, y.shape[1]-1, valinit=0, valstep=1)

def update(val):
    i = int(slider.val)
    highlight.set_ydata(y[:, i])
    ax.set_title(f"Tempo: {labels[i]}")
    fig.canvas.draw_idle()

slider.on_changed(update)

# === teclado===
def on_key(event):
    current_val = int(slider.val)
    if event.key == "right":
        new_val = min(current_val + 1, y.shape[1]-1)
        slider.set_val(new_val)
    elif event.key == "left":
        new_val = max(current_val - 1, 0)
        slider.set_val(new_val)

fig.canvas.mpl_connect("key_press_event", on_key)













plt.show()
