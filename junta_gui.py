import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from pathlib import Path


# ========================================
# Função para ler espectros individuais
# ========================================
def ler_espectro(filepath):
    try:
        with open(filepath, encoding="latin1") as f:
            lines = f.readlines()
        header_idx = next(i for i, l in enumerate(lines) if "cm-1" in l)
        df = pd.read_csv(
            filepath,
            sep=";",
            skiprows=header_idx,
            encoding="latin1",
            names=["Wavenumber", "Absorbance"],
            header=0,
        )
        return df.dropna()
    except Exception as e:
        messagebox.showerror("Erro ao ler arquivo", f"{filepath}\n\n{e}")
        return None


# ========================================
# Função para juntar espectros
# ========================================
def juntar_espectros(exp_path, intervalo):
    csv_files = sorted(
        [f for f in os.listdir(exp_path) if f.endswith(".csv")],
        key=lambda x: int(x[-7:-4]) if x[-7:-4].isdigit() else 0
    )

    if not csv_files:
        messagebox.showwarning("Aviso", "Nenhum arquivo CSV encontrado!")
        return None

    dfs = []
    for i, file in enumerate(csv_files):
        df = ler_espectro(os.path.join(exp_path, file))
        if df is None:
            continue
        tempo_min = i * intervalo
        df = df.rename(columns={"Absorbance": f"{tempo_min} min"})
        dfs.append(df.set_index("Wavenumber"))

    df_combined = pd.concat(dfs, axis=1)
    df_combined.reset_index(inplace=True)
    return df_combined.copy()  # evita fragmentação


# ========================================
# Função para gerar o gráfico
# ========================================
def gerar_figura(df_combined, colormap_name):
    fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
    colors = plt.colormaps[colormap_name](
        np.linspace(0, 1, len(df_combined.columns) - 1)
    )

    for i, col in enumerate(df_combined.columns[1:]):
        ax.plot(df_combined["Wavenumber"], df_combined[col], color=colors[i])

    ax.set_xlabel("Número de onda (cm⁻¹)")
    ax.set_ylabel("Absorbância")
    ax.set_title("Espectros combinados")
    ax.invert_xaxis()
    fig.tight_layout()
    return fig


# ========================================
# GUI Principal
# ========================================
class App(ttk.Window):
    def __init__(self):
        super().__init__(title="Unir e Visualizar Espectros", themename="darkly")
        self.geometry("950x700")

        self.selected_dir = ttk.StringVar()
        self.intervalo = ttk.DoubleVar(value=3.0)
        self.colormap_name = ttk.StringVar(value="coolwarm")
        self.df_combined = None
        self.fig = None

        self._build_ui()

    # --------------------------------
    def _build_ui(self):
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill=X)

        ttk.Label(frame_top, text="Pasta dos espectros:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=5)
        self.entry_dir = ttk.Entry(frame_top, textvariable=self.selected_dir, width=60)
        self.entry_dir.pack(side=LEFT, padx=5)
        ttk.Button(frame_top, text="Selecionar pasta...", bootstyle=INFO, command=self.selecionar_pasta).pack(side=LEFT, padx=5)

        frame_opts = ttk.Frame(self, padding=(10, 5))
        frame_opts.pack(fill=X)

        ttk.Label(frame_opts, text="Intervalo (min):").pack(side=LEFT, padx=5)
        ttk.Entry(frame_opts, textvariable=self.intervalo, width=6).pack(side=LEFT)

        ttk.Label(frame_opts, text="Gradiente:").pack(side=LEFT, padx=5)
        cmap_list = sorted(plt.colormaps())
        self.combo_cmap = ttk.Combobox(frame_opts, textvariable=self.colormap_name, values=cmap_list, width=15)
        self.combo_cmap.pack(side=LEFT, padx=5)

        # Botões principais
        frame_btns = ttk.Frame(self, padding=10)
        frame_btns.pack(fill=X)

        ttk.Button(frame_btns, text="Gerar gráfico", bootstyle=INFO, width=25, command=self.plotar).pack(side=LEFT, padx=5)
        ttk.Button(frame_btns, text="Salvar CSV combinado", bootstyle=SUCCESS, width=25, command=self.salvar_csv).pack(side=LEFT, padx=5)
        ttk.Button(frame_btns, text="Salvar gráfico (PNG)", bootstyle=SECONDARY, width=25, command=self.salvar_grafico).pack(side=LEFT, padx=5)

        # Área do gráfico
        self.frame_plot = ttk.Frame(self, padding=10)
        self.frame_plot.pack(fill=BOTH, expand=YES)

    # --------------------------------
    # Funções de interação
    # --------------------------------
    def selecionar_pasta(self):
        path = filedialog.askdirectory(title="Selecione a pasta de espectros")
        if path:
            self.selected_dir.set(path)

    def plotar(self):
        exp_path = self.selected_dir.get()
        if not exp_path or not os.path.isdir(exp_path):
            messagebox.showwarning("Atenção", "Selecione uma pasta válida!")
            return

        self.df_combined = juntar_espectros(exp_path, self.intervalo.get())
        if self.df_combined is None:
            return

        for widget in self.frame_plot.winfo_children():
            widget.destroy()

        self.fig = gerar_figura(self.df_combined, self.colormap_name.get())
        canvas = FigureCanvasTkAgg(self.fig, master=self.frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES)

        # Salvar automaticamente em pasta de resultados
        

    def salvar_automatico(self, exp_path):
        """Salva automaticamente o CSV combinado em uma pasta 'resultados' paralela."""
        results_dir = os.path.join(os.path.dirname(exp_path), "resultados")
        os.makedirs(results_dir, exist_ok=True)

        exp_name = os.path.basename(exp_path.rstrip("/"))
        save_path = os.path.join(results_dir, f"{exp_name}_combined.csv")

        self.df_combined.to_csv(save_path, index=False, sep=";")
        print(f"[AutoSave] CSV salvo em: {save_path}")

    def salvar_csv(self):
        if self.df_combined is None:
            messagebox.showwarning("Aviso", "Gere o gráfico primeiro para combinar os dados.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="espectros_combinados.csv",
        )
        if save_path:
            self.df_combined.to_csv(save_path, index=False, sep=";")
            messagebox.showinfo("Salvo", f"Arquivo salvo em:\n{save_path}")

    def salvar_grafico(self):
        if self.fig is None:
            messagebox.showwarning("Aviso", "Gere o gráfico primeiro.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")],
            initialfile="grafico_espectros.png",
        )
        if save_path:
            self.fig.savefig(save_path, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Salvo", f"Gráfico salvo em:\n{save_path}")


# ========================================
# Execução
# ========================================
if __name__ == "__main__":
    app = App()

    # Função para encerrar com segurança
    def on_close():
        plt.close('all')  # Fecha todas as figuras abertas
        app.quit()        # Encerra o loop principal do Tk
        app.destroy()     # Destroi a janela e libera recursos
        os._exit(0)       # Garante finalização completa do processo (seguro aqui)

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()