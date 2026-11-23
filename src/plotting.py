"""Einheitlich gestaltete Diagramme (werden als PNG gespeichert, nicht angezeigt)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import config

BG = "#F7F6F2"       # Folienhintergrund (Creme)
INK = "#1A1A19"      # Text
MUTED = "#6B6A66"    # Achsen, Raster
GRID = "#DEDCD5"
# Kategorische Reihenfolge fest (blau, orange, aqua), Regeln grau
COLORS = {
    "Lineare Regression": "#2a78d6",
    "Random Forest": "#eb6834",
    "Gradient Boosting": "#1baf7a",
    "Persistenz-Regel": "#8C8B86",
    "SMA-Crossover": "#B5B3AB",
}


def _style(ax, title, ylabel, xlabel=None):
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    ax.set_title(title, loc="left", pad=26, color=INK, fontsize=14, fontfamily="serif", fontstyle="italic")
    ax.set_ylabel(ylabel, color=MUTED, fontsize=11)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=10.5)
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def _save(fig, name):
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=BG)
    plt.close(fig)
    return path


def plot_price_with_split(df, split_date, name="01_kurs_mit_split"):
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.plot(df.index, df["Close"], color=INK, linewidth=1.6)
    ax.axvspan(split_date, df.index.max(), color="#eb6834", alpha=0.10, linewidth=0)
    ax.axvline(split_date, color="#eb6834", linewidth=1.4)
    ymax = ax.get_ylim()[1]
    ax.text(df.index.min(), ymax, "  Training", color=MUTED, va="top", fontsize=11)
    ax.text(split_date, ymax, "  Test (neueste Daten)", color="#eb6834", va="top", fontsize=11)
    _style(ax, f"{config.TICKER}: Schlusskurs und Train/Test-Split", "Schlusskurs in $")
    return _save(fig, name)


def plot_single_model(dates, y_true, pred, model, period, name, ylim=None):
    """Ein Modell gegen die Realität (ein Zeitraum). ylim vereinheitlicht die Achse für Vergleichbarkeit."""
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.plot(dates, y_true, color=INK, linewidth=1.0, alpha=0.55, label="Realität")
    ax.plot(dates, pred, color=COLORS.get(model, "#2a78d6"), linewidth=1.8, label=model)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    if ylim:
        ax.set_ylim(*ylim)
    _style(ax, f"{model}: {period}", "Preisänderung zum Folgetag in $")
    leg = ax.legend(frameon=False, fontsize=10, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.autofmt_xdate()
    return _save(fig, name)


def plot_metric_bars(table, metric, title, ylabel, name, reference=None, ref_label=None, period="Test"):
    """Balkendiagramm einer Kennzahl für alle Modelle/Regeln im gegebenen Zeitraum."""
    sub = table[table["Zeitraum"] == period].dropna(subset=[metric])
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    bars = ax.bar(sub["Modell"], sub[metric],
                  color=[COLORS.get(m, "#8C8B86") for m in sub["Modell"]], width=0.62)
    for b, v in zip(bars, sub[metric]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center",
                va="bottom" if v >= 0 else "top", color=INK, fontsize=10)
    if reference is not None:
        ax.axhline(reference, color=INK, linestyle="--", linewidth=1.1)
        ax.text(len(sub) - 0.5, reference, f" {ref_label}", color=INK, va="bottom", ha="right", fontsize=9)
    _style(ax, title, ylabel)
    ax.tick_params(axis="x", labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right")
    return _save(fig, name)


def plot_train_vs_test(table, metric, title, ylabel, name):
    """Gruppierte Balken Training vs. Test (Overfitting sichtbar machen)."""
    names = list(dict.fromkeys(table["Modell"]))
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    for i, (period, shade) in enumerate((("Training", 0.45), ("Test", 1.0))):
        vals = [table[(table["Modell"] == n) & (table["Zeitraum"] == period)][metric].iloc[0] for n in names]
        cols = [COLORS.get(n, "#8C8B86") for n in names]
        ax.bar(x + (i - 0.5) * 0.36, vals, width=0.34, color=cols, alpha=shade,
               label=period, edgecolor=BG, linewidth=1.2)
        for xi, v in zip(x + (i - 0.5) * 0.36, vals):
            ax.text(xi, v, f"{v:.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    _style(ax, title, ylabel)
    handles = [plt.Rectangle((0, 0), 1, 1, color=MUTED, alpha=a) for a in (0.45, 1.0)]
    leg = ax.legend(handles, ["Training (heller)", "Test (dunkler)"], frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color(INK)
    return _save(fig, name)
