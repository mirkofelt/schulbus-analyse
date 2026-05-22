from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from schulbus_analyse.calendar import SCHNEE, SKRIPT, STREIK, schultage
from schulbus_analyse.stats import monthly_stats, overall_stats, weekday_stats

BG = "#1a1a2e"
AX_BG = "#16213e"
FG = "#e0e0e0"
GREEN = "#4caf50"
YELLOW = "#ff9800"
ORANGE = "#ff6600"
RED = "#f44336"
BLUE = "#2196f3"

MON_DE = {
    1: "Jan",
    2: "Feb",
    3: "Mär",
    4: "Apr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Okt",
    11: "Nov",
    12: "Dez",
}


def kat_color(v: float) -> str:
    if v <= 0:
        return GREEN
    if v < 5:
        return YELLOW
    if v < 10:
        return ORANGE
    return RED


def _style(ax):
    ax.set_facecolor(AX_BG)
    ax.tick_params(colors=FG, labelsize=8)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for sp in ax.spines.values():
        sp.set_color("#444")


def _footer(fig, text: str):
    fig.text(0.5, 0.01, text, ha="center", color="#888", fontsize=7.5)


def generate(df: pd.DataFrame, valid: pd.DataFrame, output: Path, start: date, end: date):
    days = schultage(start, end)
    recorded = {row["Datum"].date(): row["versp"] for _, row in df.iterrows()}
    ov = overall_stats(valid)
    ms = monthly_stats(valid)
    ws = weekday_stats(valid)
    schnee_d = {d for d in SCHNEE}

    with PdfPages(output) as pdf:
        _page_kpi(pdf, df, ov, start, end)
        _page_timeseries(pdf, days, recorded, schnee_d, start, end)
        _page_weekday_month(pdf, ms, ws)
        _page_histogram(pdf, valid)
        _page_trend(pdf, valid)


def _page_kpi(pdf, df, ov, start, end):
    fig = plt.figure(figsize=(11.7, 8.3), facecolor=BG)
    fig.suptitle(
        "Schulbus-Analyse · Linie 727 → Zeesen Schule (Soll 07:36)",
        color=FG,
        fontsize=14,
        fontweight="bold",
        y=0.97,
    )
    gs = gridspec.GridSpec(
        2, 3, figure=fig, hspace=0.55, wspace=0.4, left=0.08, right=0.96, top=0.87, bottom=0.08
    )
    kpis = [
        ("Aufgezeichnete\nFahrten", str(len(df)), BLUE),
        ("Davon verspätet\n(>0 min)", str(ov["n_late"]), ORANGE),
        ("Pünktlichkeitsquote", f"{ov['pct_punctual']:.0f} %", GREEN),
        ("Median Verspätung\n(nur verspätete)", f"{ov['median_late']} min", YELLOW),
        ("Mittelwert Verspätung\n(nur verspätete)", f"{ov['mean_late']} min", ORANGE),
        ("Ausfälle\n(Streik + Skript)", str(len(STREIK) + len(SKRIPT)), RED),
    ]
    for i, (lbl, val, col) in enumerate(kpis):
        ax = fig.add_subplot(gs[i // 3, i % 3])
        ax.set_facecolor(AX_BG)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color(col)
            sp.set_linewidth(2)
        ax.text(
            0.5,
            0.62,
            val,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=22,
            fontweight="bold",
            color=col,
        )
        ax.text(
            0.5, 0.22, lbl, transform=ax.transAxes, ha="center", va="center", fontsize=9, color=FG
        )
    legend = [
        (GREEN, "Pünktlich / zu früh (≤ 0 min)"),
        (YELLOW, "Leicht verspätet (1–4 min)"),
        (ORANGE, "Verspätet (5–9 min)"),
        (RED, "Stark verspätet (≥ 10 min)"),
    ]
    lx = 0.08
    for col, txt in legend:
        fig.patches.append(
            plt.Rectangle((lx, 0.05), 0.018, 0.025, transform=fig.transFigure, color=col, zorder=5)
        )
        fig.text(lx + 0.022, 0.062, txt, color=FG, fontsize=8, va="center")
        lx += 0.22
    _footer(
        fig,
        f"Analyse: {start:%d.%m.%Y}–{end:%d.%m.%Y} · "
        "Schneetage (15.01, 26.01) und Streik (27.02) ausgeschlossen",
    )
    pdf.savefig(fig, facecolor=BG)
    plt.close()


def _page_timeseries(pdf, days, recorded, schnee_d, start, end):
    fig, ax = plt.subplots(figsize=(11.7, 8.3), facecolor=BG)
    ax.set_facecolor(AX_BG)
    fig.suptitle(
        "Zeitreihe aller Schultage · Ankunft Zeesen Schule",
        color=FG,
        fontsize=13,
        fontweight="bold",
        y=0.97,
    )
    for i, d in enumerate(days):
        v = recorded.get(d)
        if v is not None:
            ax.bar(i, v, color=kat_color(v), width=0.8, zorder=3)
        else:
            sym = "❄" if d in schnee_d else ("S" if d in STREIK else "✕")
            col = RED if d in schnee_d else (ORANGE if d in STREIK else "#888")
            ax.text(i, -4, sym, ha="center", va="top", fontsize=7, color=col, zorder=4)
    ax.axhline(0, color="#888", lw=0.8, zorder=2)
    tick_idx = [i for i in range(len(days)) if i % 10 == 0]
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(
        [days[i].strftime("%d.%m") for i in tick_idx], rotation=45, ha="right", fontsize=7
    )
    prev_m = None
    for i, d in enumerate(days):
        if d.month != prev_m:
            ax.axvline(i - 0.5, color="#444", lw=0.8, ls="--", zorder=1)
            ax.text(i, 18, d.strftime("%b"), color="#888", fontsize=8, va="bottom")
            prev_m = d.month
    ax.set_ylabel("Verspätung (min)", color=FG)
    ax.set_xlabel("Schultag", color=FG)
    ax.set_xlim(-1, len(days))
    _style(ax)
    _footer(
        fig,
        "✕ = kein Datensatz (Skriptfehler)  ·  ❄ = Schnee/Eis  ·  S = Streik ver.di/RVS (27.02.)  ·  "
        "Negative Werte = Bus früher als 07:36",
    )
    pdf.savefig(fig, facecolor=BG)
    plt.close()


def _page_weekday_month(pdf, ms, ws):
    fig = plt.figure(figsize=(11.7, 8.3), facecolor=BG)
    fig.suptitle(
        "Wochentag- und Monatsvergleich · Mittelwert Verspätung (verfrühte = 0 min)",
        color=FG,
        fontsize=13,
        fontweight="bold",
        y=0.97,
    )
    gs3 = gridspec.GridSpec(
        1, 2, figure=fig, wspace=0.38, left=0.07, right=0.97, top=0.88, bottom=0.14
    )

    ax_m = fig.add_subplot(gs3[0])
    ax_m.set_facecolor(AX_BG)
    x = np.arange(len(ms))
    labels = [MON_DE[m] for m in ms["monat"]]
    bars = ax_m.bar(x, ms["mean_c"], color=ORANGE, zorder=3, width=0.5)
    for bar, v in zip(bars, ms["mean_c"]):
        h = max(bar.get_height(), 0.25)
        ax_m.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.15,
            f"{v}",
            ha="center",
            va="bottom",
            fontsize=9,
            color=FG,
            fontweight="bold",
        )
    for i, row in ms.iterrows():
        ax_m.text(
            x[i],
            -0.8,
            f"{int(row['n_late'])}/{int(row['n'])}\nspät",
            ha="center",
            va="top",
            fontsize=7.5,
            color="#aaa",
        )
    ax_m.set_xticks(x)
    ax_m.set_xticklabels(labels)
    ax_m.set_ylabel("Ø Verspätung (min)", color=FG)
    ax_m.set_title("Monatlicher Mittelwert", color=FG, fontsize=10)
    ax_m.set_ylim(bottom=-2.5)
    ax_m.axhline(0, color="#555", lw=0.7)
    _style(ax_m)

    ax_w = fig.add_subplot(gs3[1])
    ax_w.set_facecolor(AX_BG)
    x_pos = np.arange(5)
    ax_w.boxplot(
        list(ws.values()),
        positions=x_pos,
        patch_artist=True,
        medianprops=dict(color="white", lw=2),
        boxprops=dict(facecolor=BLUE, alpha=0.7),
        whiskerprops=dict(color=FG),
        capprops=dict(color=FG),
        flierprops=dict(marker="o", color=ORANGE, ms=5),
    )
    ax_w.set_xticks(x_pos)
    ax_w.set_xticklabels(["Mo", "Di", "Mi", "Do", "Fr"])
    ax_w.set_xlabel("Wochentag", color=FG)
    ax_w.set_ylabel("Verspätung (min, verfrühte = 0)", color=FG)
    ax_w.set_title("Wochentag-Vergleich", color=FG, fontsize=10)
    _style(ax_w)

    _footer(
        fig,
        "Mittelwert inkl. aller Fahrten · verfrühte Ankünfte = 0 min · Schnee/Eis + Streik ausgeschlossen",
    )
    pdf.savefig(fig, facecolor=BG)
    plt.close()


def _page_histogram(pdf, valid):
    fig, ax = plt.subplots(figsize=(11.7, 8.3), facecolor=BG)
    ax.set_facecolor(AX_BG)
    fig.suptitle(
        "Häufigkeitsverteilung der Verspätungen", color=FG, fontsize=13, fontweight="bold", y=0.97
    )
    all_v = valid["versp"].dropna().astype(int)
    min_v, max_v = int(all_v.min()), int(all_v.max())
    bar_xs = np.arange(min_v, max_v + 1)
    counts, _ = np.histogram(all_v, bins=range(min_v, max_v + 2))
    ax.bar(
        bar_xs, counts, width=0.8, color=[kat_color(b) for b in bar_xs], align="center", zorder=3
    )
    ax.set_xticks(range(min_v, max_v + 1))
    ax.set_xticklabels([str(v) for v in range(min_v, max_v + 1)], fontsize=7)
    ax.set_xlabel("Verspätung (min)", color=FG)
    ax.set_ylabel("Anzahl Fahrten", color=FG)
    ax.axvline(0, color="#888", lw=1, ls="--")
    _style(ax)
    _footer(
        fig,
        "Alle aufgezeichneten Fahrten inkl. verfrühter Ankünfte · Schnee/Eis + Streik ausgeschlossen",
    )
    pdf.savefig(fig, facecolor=BG)
    plt.close()


def _page_trend(pdf, valid):
    import matplotlib.dates as mdates

    fig, ax = plt.subplots(figsize=(11.7, 8.3), facecolor=BG)
    ax.set_facecolor(AX_BG)
    fig.suptitle(
        "Trend: Gleitender 10-Tage-Median der Verspätung",
        color=FG,
        fontsize=13,
        fontweight="bold",
        y=0.97,
    )
    trend = valid.sort_values("Datum").copy()
    trend["roll"] = trend["versp_c"].rolling(10, min_periods=3).median()
    ax.plot(
        trend["Datum"].values,
        trend["versp_c"].values,
        "o",
        color=BLUE,
        ms=4,
        alpha=0.5,
        label="Einzelfahrt",
    )
    ax.plot(
        trend["Datum"].values,
        trend["roll"].values,
        "-",
        color=YELLOW,
        lw=2.5,
        label="10-Tage-Median",
    )
    ax.axhline(0, color="#555", lw=0.7)
    ax.set_ylabel("Verspätung (min, verfrühte = 0)", color=FG)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    ax.legend(facecolor=AX_BG, labelcolor=FG, fontsize=9)
    _style(ax)
    _footer(fig, "Gleitender Median über jeweils 10 aufgezeichnete Fahrten")
    pdf.savefig(fig, facecolor=BG)
    plt.close()
