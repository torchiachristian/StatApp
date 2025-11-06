# Stat Tracker — Christian

Applicazione desktop Linux (Python + CustomTkinter) per autovalutazione personale.  
Traccia statistiche giornaliere, storico, grafici e report mensili.

## Requisiti
- Linux Mint / Ubuntu
- Python 3.10+
- Librerie Python:
  pip install customtkinter matplotlib pandas numpy
- Tkinter (se manca): sudo apt install python3-tk

## Avvio
Da terminale nella cartella del progetto:
python3 main.py

## Modifica delle metriche
Aprire `main.py`, cercare `DEFAULT_STATS` e modificare i dizionari per aggiungere/rimuovere metriche.

## File di dati
- `stats.json` → valori correnti
- `stats_history.json` → storico giornaliero
- `stats_export.csv` → esportazione CSV

