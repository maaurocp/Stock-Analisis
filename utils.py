import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt



def show_report_popup(data):
    win = tk.Toplevel()
    win.title(data["name"])
    win.geometry("460x520")

    canvas = tk.Canvas(win)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    row_i = 0

    def row(label, value):
        nonlocal row_i
        tk.Label(scroll_frame, text=label, anchor="w", width=18).grid(row=row_i, column=0, sticky="w")
        tk.Label(scroll_frame, text=value, anchor="w").grid(row=row_i, column=1, sticky="w")
        row_i += 1

    tk.Label(scroll_frame, text=data["name"], font=("Arial", 14, "bold")).grid(row=row_i, column=0, columnspan=2, pady=10)
    row_i += 1

    row("Precio", data["price"])
    row("PE", format_float(data["pe"]))
    row("ROE", format_percent(data["roe"]) + rate_roe(data["roe"]))
    row("Sharpe", format_float(data["sharpe"]) + rate_sharpe(data["sharpe"]))
    row("FCF Yield", format_percent(data["fcf_yield"]) + rate_fcf_yield(data["fcf_yield"]))
    row("Debt / FCF", format_float(data["debt_fcf"]) + rate_debt_fcf(data["debt_fcf"]))
    row("Revenue Growth", format_percent(data["revenue_growth"]) + rate_growth(data["revenue_growth"]))
    row("FCF Margin", format_percent(data["fcf_margin"]) + rate_margin(data["fcf_margin"]))

    fcf = data["free_cashflow"]

    if fcf:
        tk.Label(scroll_frame, text="\nFree Cash Flow (3Y)", font=("Arial", 11, "bold")).grid(row=row_i, column=0, columnspan=2)
        row_i += 1

        for year in sorted(fcf.keys(), reverse=True):
            row(year, format_number(fcf[year]))


    r = data["returns"]

    if r:
        tk.Label(scroll_frame, text="\nReturns", font=("Arial", 11, "bold")).grid(row=row_i, column=0, columnspan=2)
        row_i += 1
        row("Hoy", format_percent(r["today"]))
        row("Semana", format_percent(r["week"]))
        row("Mes", format_percent(r["month"]))
    show_price_chart(data)


def show_price_chart(data):
    hist = data.get("history")

    if hist is None or hist.empty:
        return

    win = tk.Toplevel()
    win.title(f"{data['name']} - Last Month")

    fig = plt.Figure(figsize=(5,3), dpi=100)
    ax = fig.add_subplot(111)

    ax.plot(hist.index, hist["Close"], color="green", linewidth=2)
    ax.set_title("Last 30 days")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def format_number(n):
    if n is None:
        return "N/A"
    return f"{int(n):,}".replace(",", ".")


def format_percent(n):
    if n is None:
        return "N/A"
    return f"{n:.2f}%"


def format_float(n):
    if n is None:
        return "N/A"
    return f"{n:.2f}"

def rate_fcf_yield(v):
    if v is None: return ""
    if v < 3: return " (Bajo <3%)"
    if v < 5: return " (Aceptable 3–5%)"
    if v < 10: return " (Bueno 5–10%)"
    return " (Muy bueno >10%)"


def rate_debt_fcf(v):
    if v is None: return ""
    if v > 6: return " (Peligro >6)"
    if v > 3: return " (Cuidado 3–6)"
    return " (Excelente <3)"


def rate_growth(v):
    if v is None: return ""
    if v < 0: return " (Negativo)"
    if v < 5: return " (Débil 0–5%)"
    if v < 10: return " (Decente 5–10%)"
    return " (Fuerte >10%)"


def rate_margin(v):
    if v is None: return ""
    if v < 5: return " (Muy bajo <5%)"
    if v < 10: return " (Bajo 5–10%)"
    if v < 20: return " (Bueno 10–20%)"
    return " (Muy fuerte >20%)"


def rate_sharpe(v):
    if v is None: return ""
    if v < 0.5: return " (Malo <0.5)"
    if v < 1: return " (Aceptable 0.5–1)"
    if v < 2: return " (Bueno 1–2)"
    return " (Excelente >2)"


def rate_roe(v):
    if v is None: return ""
    if v < 5: return " (Muy bajo)"
    if v < 10: return " (Bajo)"
    if v < 15: return " (Decente)"
    return " (Muy bueno >15%)"
