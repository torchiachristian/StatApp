import json, os, csv, datetime
from statistics import mean, stdev
import customtkinter as ctk
from tkinter import messagebox
import datetime

DATA_FILE = "stats.json"
HISTORY_FILE = "stats_history.json"

# --- STRUTTURA BASE DI DEFAULT (puoi sostituire con i tuoi domini) ---
DEFAULT_STATS = {
    "Fondamenta (autogoverno e struttura interna)": [
        "Disciplina", "Autocontrollo", "Costanza", "Sonno / Recupero", "Alimentazione",
        "Gestione del Tempo", "Ordine Ambientale", "Resistenza alla Lussuria",
        "Sobrietà Digitale", "Resilienza"
    ],
    "Funzionalità (capacità operative e cognitive)": [
        "Focus", "Energia", "Chiarezza Mentale", "Memoria di Lavoro", "Problem Solving",
        "Apprendimento", "Gestione Stress", "Precisione", "Efficienza", "Rapidità Decisionale"
    ],
    "Dominio (interazione e impatto)": [
        "Sicurezza", "Leadership", "Assertività", "Comunicazione", "Empatia Strategica",
        "Lettura Sociale", "Reputazione", "Influenza", "Resistenza al Rifiuto", "Capacità di Negoziazione"
    ],
    "Trascendenza (direzione e coerenza esistenziale)": [
        "Motivazione", "Scopo", "Integrità", "Autostima", "Visione Lungo Termine",
        "Gratitudine", "Creatività", "Umiltà", "Spiritualità / Filosofia Personale", "Disidentificazione dall’Ego"
    ]
}

# --- FUNZIONI DI BASE DATI ---

def load_current():
    """Carica i valori correnti o crea il file con i valori di default."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = DEFAULT_STATS.copy()
        save_current(data)
    return data

def save_current(data: dict):
    """Salva i valori correnti nel file principale."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_history():
    """Carica lo storico giornaliero."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history: dict):
    """Salva l'intero storico giornaliero."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def add_today_entry(current_stats: dict):
    """Aggiunge i valori odierni allo storico (usa la data odierna come chiave)."""
    today = str(datetime.date.today())
    history = load_history()
    history[today] = current_stats
    save_history(history)

def export_csv():
    """Esporta lo storico in formato CSV per analisi esterna."""
    history = load_history()
    if not history:
        return
    keys = sorted(next(iter(history.values())).keys())
    with open("stats_export.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Data"] + keys)
        for day, vals in sorted(history.items()):
            row = [day] + [vals.get(k, "") for k in keys]
            writer.writerow(row)

def monthly_report():
    """Calcola media, deviazione standard e trend mensile per ogni metrica."""
    history = load_history()
    if not history:
        return {}

    # Raggruppa per mese
    monthly = {}
    for date_str, values in history.items():
        y, m, *_ = date_str.split("-")
        key = f"{y}-{m}"
        monthly.setdefault(key, []).append(values)

    # Calcola statistiche per ogni mese
    reports = {}
    for month, entries in monthly.items():
        metrics = {}
        for metric in entries[0]:
            vals = [e.get(metric, 0) for e in entries]
            metrics[metric] = {
                "media": round(mean(vals), 2),
                "deviazione": round(stdev(vals), 2) if len(vals) > 1 else 0.0
            }
        reports[month] = metrics

    # Calcolo variazione percentuale mese su mese
    months_sorted = sorted(reports.keys())
    for i in range(1, len(months_sorted)):
        prev_m, curr_m = months_sorted[i - 1], months_sorted[i]
        for k in reports[curr_m]:
            prev_val = reports[prev_m].get(k, {}).get("media", 0)
            curr_val = reports[curr_m][k]["media"]
            if prev_val != 0:
                diff = ((curr_val - prev_val) / prev_val) * 100
            else:
                diff = 0
            reports[curr_m][k]["variazione_%"] = round(diff, 1)

    return reports
class StatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stat Tracker — Christian")
        self.geometry("1000x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.stats = load_current()

        # --- CREAZIONE TABS ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_valori = self.tabview.add("Valori")
        self.tab_analisi = self.tabview.add("Analisi")
        self.tab_dashboard = self.tabview.add("Dashboard")

        # --- INIZIALIZZA CONTENUTI ---
        self.create_valori_tab()
        self.create_analisi_tab()
        self.create_dashboard_tab()

    # -------------------------------
    # TAB: VALORI
    # -------------------------------
    def create_valori_tab(self):
        self.valori_frame = ctk.CTkScrollableFrame(self.tab_valori)
        self.valori_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.sliders = {}
        for name in self.stats.keys():
            row = ctk.CTkFrame(self.valori_frame)
            row.pack(fill="x", pady=5)
            label = ctk.CTkLabel(row, text=name, width=250, anchor="w")
            label.pack(side="left", padx=5)
            slider = ctk.CTkSlider(row, from_=0, to=10, number_of_steps=100)
            slider.set(self.stats[name])
            slider.pack(side="left", fill="x", expand=True, padx=5)
            value_label = ctk.CTkLabel(row, text=f"{self.stats[name]:.1f}/10", width=60)
            value_label.pack(side="left", padx=5)
            slider.configure(command=lambda v, lbl=value_label: lbl.configure(text=f"{float(v):.1f}/10"))
            self.sliders[name] = slider

        save_btn = ctk.CTkButton(self.tab_valori, text="Salva giornata", command=self.save_day)
        save_btn.pack(pady=10)

    def save_day(self):
        for k, s in self.sliders.items():
            self.stats[k] = round(s.get(), 2)
        save_current(self.stats)
        add_today_entry(self.stats)
        messagebox.showinfo("Salvato", f"Valori salvati per {datetime.date.today()}")

    # -------------------------------
    # TAB: ANALISI (placeholder)
    # -------------------------------
    def create_analisi_tab(self):
        frame = ctk.CTkFrame(self.tab_analisi)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        label = ctk.CTkLabel(frame, text="Seleziona metrica e intervallo:")
        label.pack(pady=10)

        self.metric_choice = ctk.CTkOptionMenu(frame, values=list(self.stats.keys()))
        self.metric_choice.pack(pady=5)

        self.range_choice = ctk.CTkOptionMenu(frame, values=["7","30","90","365"], command=lambda _: None)
        self.range_choice.set("30")
        self.range_choice.pack(pady=5)

        plot_button = ctk.CTkButton(frame, text="Mostra Grafico", command=self.show_plot)
        plot_button.pack(pady=5)

        compare_button = ctk.CTkButton(frame, text="Confronta Metriche", command=self.show_comparison)
        compare_button.pack(pady=5)

        self.plot_area = ctk.CTkFrame(frame)
        self.plot_area.pack(fill="both", expand=True, padx=10, pady=10)


    def show_plot(self):
        for w in self.plot_area.winfo_children():
            w.destroy()
        metric = self.metric_choice.get()
        days = int(self.range_choice.get())
        fig = plot_metric(metric, days)
        if not fig:
            messagebox.showinfo("Info","Dati insufficienti.")
            return
        canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_comparison(self):
        for w in self.plot_area.winfo_children():
            w.destroy()
        # dialogo semplice: chiedi all’utente nomi metriche separati da virgola
        import tkinter.simpledialog as sd
        metrics = sd.askstring("Confronto", "Inserisci metriche separate da virgola:").split(",")
        metrics = [m.strip() for m in metrics if m.strip()]
        if not metrics:
            return
        days = int(self.range_choice.get())
        fig = plot_comparison(metrics, days)
        if not fig:
            messagebox.showinfo("Info","Dati insufficienti.")
            return
        canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    # -------------------------------
    # TAB: DASHBOARD (placeholder)
    # -------------------------------
    def create_dashboard_tab(self):
        self.dashboard_frame = ctk.CTkScrollableFrame(self.tab_dashboard)
        self.dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

        topbar = ctk.CTkFrame(self.tab_dashboard)
        topbar.pack(fill="x", pady=(0,10))

        refresh_btn = ctk.CTkButton(topbar, text="Aggiorna Report", command=self.refresh_dashboard)
        refresh_btn.pack(side="left", padx=10)

        export_btn = ctk.CTkButton(topbar, text="Esporta CSV", command=export_csv)
        export_btn.pack(side="left", padx=10)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        for w in self.dashboard_frame.winfo_children():
            w.destroy()

        reports = monthly_report()
        if not reports:
            ctk.CTkLabel(self.dashboard_frame, text="Nessun dato disponibile").pack(pady=20)
            return

        months = sorted(reports.keys())
        latest = months[-1]

        ctk.CTkLabel(
            self.dashboard_frame,
            text=f"Report mensile: {latest}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(5,15))

        table = ctk.CTkFrame(self.dashboard_frame)
        table.pack(fill="x", padx=10, pady=10)

        header = ctk.CTkLabel(
            table,
            text=f"{'Metrica':<30} {'Media':<10} {'Dev.Std':<10} {'Variaz.%':<10}",
            justify="left"
        )
        header.pack(anchor="w")

        prev_m = months[-2] if len(months) > 1 else None

        for metric, vals in reports[latest].items():
            media = vals.get("media", 0)
            dev = vals.get("deviazione", 0)
            var = vals.get("variazione_%", 0)

            if var > 2:
                fg = "green"
            elif var < -2:
                fg = "red"
            else:
                fg = "gray"

            line = ctk.CTkLabel(
                table,
                text=f"{metric:<30} {media:<10.2f} {dev:<10.2f} {var:+<10.1f}",
                justify="left",
                text_color=fg
            )
            line.pack(anchor="w")


import matplotlib
matplotlib.use("Agg")  # evita errori di backend su Linux senza display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import datetime as dt

def plot_metric(metric, days=30):
    """Ritorna un oggetto Figure matplotlib con l'andamento temporale della metrica."""
    hist = load_history()
    if not hist:
        return None

    df = pd.DataFrame(hist).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    if metric not in df.columns:
        return None

    start_date = df.index.max() - pd.Timedelta(days=days)
    df = df[df.index >= start_date]

    fig, ax = plt.subplots(figsize=(6,3), facecolor="#1e1e1e")
    ax.plot(df.index, df[metric], marker="o", color="cyan")
    ax.set_title(metric, color="white")
    ax.set_xlabel("Data", color="white")
    ax.set_ylabel("Valore", color="white")
    ax.tick_params(colors="white")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

def plot_comparison(metrics, days=30):
    """Ritorna un grafico comparativo tra più metriche."""
    hist = load_history()
    if not hist:
        return None
    df = pd.DataFrame(hist).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    start_date = df.index.max() - pd.Timedelta(days=days)
    df = df[df.index >= start_date]

    fig, ax = plt.subplots(figsize=(6,3), facecolor="#1e1e1e")
    for m in metrics:
        if m in df.columns:
            ax.plot(df.index, df[m], label=m)
    ax.set_title("Confronto Metriche", color="white")
    ax.legend()
    ax.set_xlabel("Data", color="white")
    ax.set_ylabel("Valore", color="white")
    ax.tick_params(colors="white")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

if __name__ == "__main__":
 app = StatApp()
 print("Applicazione avviata")
 app.mainloop()
 print("Applicazione terminata")
