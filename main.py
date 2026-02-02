import tkinter as tk
from analyzer import analyze_company
from utils import show_report_popup


def run_analysis():
    ticker = entry.get().upper().strip()
    if not ticker:
        return

    data = analyze_company(ticker)
    show_report_popup(data)


root = tk.Tk()
root.title("Stock Analyzer")
root.geometry("300x120")
root.resizable(False, False)

label = tk.Label(root, text="Ticker:")
label.pack(pady=5)

entry = tk.Entry(root, justify="center")
entry.pack()

button = tk.Button(root, text="Analizar", command=run_analysis)
button.pack(pady=10)

root.mainloop()
