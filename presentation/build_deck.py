"""Baut die Präsentation aus den Ergebnissen in results/ (nur results/, nie data/).

Start:  python presentation/build_deck.py
Ergebnis: presentation/Aktienanalyse_Praesentation.pptx

Die Datei ist normal in PowerPoint bearbeitbar: Texte sind Textfelder, die
Balkendiagramme sind native PowerPoint-Charts (Rechtsklick > Daten bearbeiten),
die Zeitreihen sind PNG-Bilder aus results/figures/.
"""
import json
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from lxml import etree

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
FIG = RES / "figures"
OUT = Path(__file__).resolve().parent / "Aktienanalyse_Praesentation.pptx"

# ---------- Design (Creme, Tinte, Serifen-Kursiv + Mono-Labels) ----------
BG, INK, MUTED, LINE = "F7F6F2", "1A1A19", "6B6A66", "D9D7CF"
ACCENT = "EB6834"
SERIF, MONO = "Georgia", "Consolas"
MODEL_COLORS = {"Lineare Regression": "2A78D6", "Random Forest": "EB6834", "Gradient Boosting": "1BAF7A",
                "Persistenz-Regel": "8C8B86", "SMA-Crossover": "B5B3AB", "Immer steigend": "6B6A66"}
SHORT = {"Persistenz-Regel": "Persistenz", "SMA-Crossover": "SMA-Cross", "Immer steigend": "Immer ↑",
         "Lineare Regression": "Lin. Regr.", "Random Forest": "Random Forest", "Gradient Boosting": "Grad. Boosting"}
HEADER_RIGHT = "AKTIENANALYSE"
FOOTER_LEFT = "IU INTERNATIONALE HOCHSCHULE"
SOURCE = "Eigene Darstellung, Daten: Yahoo Finance (yfinance)"

W, H = 13.333, 7.5
LM = 0.9          # linker Rand
CW = W - 2 * LM   # Inhaltsbreite


def rgb(h):
    return RGBColor.from_string(h)


# ---------- Daten laden ----------
info = json.loads((RES / "run_info.json").read_text(encoding="utf-8"))
M = pd.read_csv(RES / "metrics.csv")
C = pd.read_csv(RES / "criteria.csv").set_index("Modell")
P = pd.read_csv(RES / "predictions_test.csv")


def m(model, period, metric):
    return float(M[(M.Modell == model) & (M.Zeitraum == period)][metric].iloc[0])


def de(x, d=2):
    """Zahl im deutschen Format (Komma)."""
    return f"{x:.{d}f}".replace(".", ",").replace("-", "−")


MODELS = ["Lineare Regression", "Random Forest", "Gradient Boosting"]
n_crit = int(C.loc[MODELS, ["K1_schlaegt_Persistenz", "K2_R2_ueber_0", "K3_Treffer_signifikant"]].sum().sum())
any_trust = bool(C.loc[MODELS, "vertrauenswuerdig"].any())

# ---------- Hilfsfunktionen ----------
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
slides_meta = []   # (Folie, Kapitel) – für Seitenzahlen


def tb(slide, x, y, w, h, text, size=20, font=SERIF, color=INK, italic=False, bold=False,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spc=None, line=None, space_after=0):
    """Textfeld. In `text` schaltet ein Sternchen * Kursiv um; \\n beginnt einen neuen Absatz."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line:
            p.line_spacing = line
        p.space_after = Pt(space_after)
        ital = italic
        for seg in para.split("*"):
            if seg:
                r = p.add_run()
                r.text = seg
                f = r.font
                f.name, f.size, f.bold, f.italic = font, Pt(size), bold, ital
                f.color.rgb = rgb(color)
                if spc:
                    r._r.get_or_add_rPr().set("spc", str(spc))
            ital = not ital
    return box


def rule(slide, x, y, w, color=LINE, weight=0.75):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Pt(weight))
    r.fill.solid()
    r.fill.fore_color.rgb = rgb(color)
    r.line.fill.background()
    st = r._element.find(qn('p:style'))
    if st is not None:
        r._element.remove(st)   # Theme-Stil (Schatten) entfernen
    return r


def new_slide(chapter=None, title=None, notes=""):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(BG)
    s._chapter, s._title = chapter, title
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def decorate(slide, idx, total, with_header=True):
    """Marke, Main-Liner rechts oben, Fußzeile und Seitenzahl."""
    d = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(LM), Inches(0.42), Inches(0.2), Inches(0.28))
    d.fill.solid(); d.fill.fore_color.rgb = rgb(INK); d.line.fill.background()
    if d._element.find(qn('p:style')) is not None:
        d._element.remove(d._element.find(qn('p:style')))
    if with_header:
        tb(slide, W - LM - 4, 0.5, 4, 0.3, HEADER_RIGHT, 11, MONO, INK, align=PP_ALIGN.RIGHT, spc=100)
    tb(slide, LM, H - 0.6, 5, 0.3, FOOTER_LEFT, 10, MONO, INK, spc=100)
    tb(slide, W - LM - 2, H - 0.6, 2, 0.3, f"{idx:02d} / {total:02d}", 10, MONO, MUTED, align=PP_ALIGN.RIGHT, spc=100)
    if slide._chapter:
        tb(slide, LM, 1.0, 9, 0.3, slide._chapter, 11, MONO, MUTED, spc=100)
    if slide._title:
        tb(slide, LM, 1.3, CW, 0.9, slide._title, 38, SERIF, INK, italic=True)


def numbered(slide, items, x=LM, y=2.55, w=None, size=24, gap=0.95, label_w=0.7):
    """Nummerierte Liste (01, 02, ...) wie in der Vorlage; *...* wird kursiv."""
    w = w or CW
    gaps = gap if isinstance(gap, (list, tuple)) else [gap] * len(items)
    yy = y
    for i, t in enumerate(items):
        tb(slide, x, yy + 0.1, label_w, 0.3, f"{i + 1:02d}", 11, MONO, MUTED, spc=100)
        tb(slide, x + label_w, yy, w - label_w, gaps[i] - 0.1, t, size, SERIF, INK, line=1.05)
        yy += gaps[i]


def caption(slide, x, y, w, nr, extra=""):
    tb(slide, x, y, w, 0.3, f"ABB. {nr} · {SOURCE}{extra}".upper(), 9, MONO, MUTED, spc=50)


def picture(slide, name, x, y, w):
    return slide.shapes.add_picture(str(FIG / name), Inches(x), Inches(y), width=Inches(w))


def style_chart(ch, size=11):
    ch.font.size = Pt(size)
    ch.font.name = SERIF
    ch.font.color.rgb = rgb(INK)


def native_bar(slide, x, y, w, h, cats, vals, colors, fmt="0.0", vmin=None, vmax=None, major=None, title=None):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series("Wert", vals)
    ch = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    style_chart(ch)
    ch.has_legend = False
    ch.has_title = bool(title)
    if title:
        ch.chart_title.text_frame.text = title
        r = ch.chart_title.text_frame.paragraphs[0].runs[0]
        r.font.size, r.font.italic, r.font.name = Pt(14), True, SERIF
        r.font.color.rgb = rgb(INK)
        ch.chart_title.include_in_layout = False
    plot = ch.plots[0]
    plot.gap_width = 55
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(12)
    for i, c in enumerate(colors):
        pt = plot.series[0].points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(c)
    _axes(ch, vmin, vmax, major)
    return ch


def _axes(ch, vmin, vmax, major):
    va, ca = ch.value_axis, ch.category_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = rgb(LINE)
    va.major_gridlines.format.line.width = Pt(0.75)
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(11)
    va.tick_labels.font.color.rgb = rgb(MUTED)
    if vmin is not None:
        va.minimum_scale = vmin
    if vmax is not None:
        va.maximum_scale = vmax
    if major:
        va.major_unit = major
    ca.format.line.color.rgb = rgb(LINE)
    ca.tick_labels.font.size = Pt(11)
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW


def cell_border_bottom(cell, color=LINE, w=9525):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for old in tcPr.findall(qn(tag)):
            tcPr.remove(old)
    for tag in ("a:lnL", "a:lnR", "a:lnT"):
        ln = etree.SubElement(tcPr, qn(tag), w="0")
        etree.SubElement(ln, qn("a:noFill"))
    ln = etree.SubElement(tcPr, qn("a:lnB"), w=str(w))
    sf = etree.SubElement(ln, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:srgbClr"), val=color)
    # Reihenfolge laut Schema: Linien vor dem Füllbereich
    for child in list(tcPr):
        if child.tag in (qn("a:noFill"), qn("a:solidFill")):
            tcPr.remove(child)
            tcPr.append(child)


def table(slide, x, y, w, rows, col_w, row_h=0.62, size=15, header_size=11):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
    tbl = shape.table
    tbl._tbl.tblPr.find(qn("a:tableStyleId")).text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # "Kein Stil, kein Raster"
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, txt in enumerate(row):
            c = tbl.cell(i, j)
            c.fill.background()
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.08)
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = txt
            f = r.font
            if i == 0:
                f.name, f.size, f.color.rgb = MONO, Pt(header_size), rgb(MUTED)
            else:
                f.name, f.size, f.color.rgb = SERIF, Pt(size), rgb(INK)
                f.italic = j == 0
            cell_border_bottom(c, INK if i == 0 else LINE, 12700 if i == 0 else 9525)
    return tbl


# ---------- Folien ----------
S = []   # Liste (slide)


def add(slide):
    S.append(slide)
    return slide


# 1 Titel
s = add(new_slide(notes="Begrüßung, Thema in einem Satz: Ich teste, ob einfache Modelle den Google-Kurs besser vorhersagen als eine simple Faustregel. (ca. 0:20)"))
tb(s, LM, 2.2, CW, 1.4, "Aktienanalyse", 66, SERIF, INK, italic=True)
tb(s, LM, 3.75, 10.5, 1.3, "Können einfache Standardmodelle die Google-Aktie\nvertrauenswürdig vorhersagen?", 28, SERIF, INK, line=1.05)
rule(s, LM, 5.35, CW)
tb(s, LM, 5.55, CW, 0.3, "PROJEKT: PROGRAMMIERUNG MIT PYTHON · DLBFTPPP01", 12, MONO, INK, spc=100)
tb(s, LM, 5.95, CW, 0.3, "[NAME] · [MATRIKELNUMMER] · [DATUM]", 12, MONO, MUTED, spc=100)

# 2 Gliederung
s = add(new_slide("GLIEDERUNG", "Der rote Faden", notes="Vier Kapitel, eine Frage. Am Ende beantworte ich sie. (ca. 0:20)"))
chapters = [("I", "Die Frage", "Aufgabe & Leitfrage · Daten"),
            ("II", "Messlatte & Kandidaten", "Baseline · Modelle · Warum diese"),
            ("III", "Der Test", "Training · Prognose"),
            ("IV", "Die Antwort", "Modellvergleich · Reflexion · Fazit")]
for i, (rn, name, sub) in enumerate(chapters):
    yy = 2.55 + i * 1.05
    tb(s, LM, yy + 0.12, 0.8, 0.4, rn, 14, MONO, MUTED, spc=100)
    tb(s, LM + 0.9, yy, 6.5, 0.6, name, 28, SERIF, INK, italic=True)
    tb(s, LM + 7.4, yy + 0.14, 4.0, 0.4, sub.upper(), 10, MONO, MUTED, spc=60)
    rule(s, LM, yy + 0.8, CW)

# 3 Leitfrage
s = add(new_slide("I · DIE FRAGE", "Aufgabe & Leitfrage",
                  notes="Aufgabe: Prognosemodell für eine Aktie, Training auf alten, Test auf neuesten Daten, Vergleich mit realen Daten. "
                        "Meine Leitfrage macht daraus eine Geschichte. 'Vertrauenswürdig' definiere ich vorab mit drei prüfbaren Kriterien. (ca. 1:30)"))
tb(s, LM, 2.3, CW, 1.4, "*Können einfache Standardmodelle den Kurs der Google-Aktie vertrauenswürdig vorhersagen, also besser als eine simple Faustregel?*",
   24, SERIF, INK, line=1.05)
tb(s, LM, 4.0, CW, 0.3, "„VERTRAUENSWÜRDIG“ HEISST IM TESTZEITRAUM:", 11, MONO, MUTED, spc=100)
numbered(s, ["*besser* als die Persistenz-Regel (MAE und RMSE)",
             "*R² größer als 0*, also besser als der Mittelwert",
             "Trefferquote *signifikant über 50 %* (Binomialtest, p < 0,05)"], y=4.4, size=21, gap=0.75)

# 4 Daten
s = add(new_slide("I · DIE FRAGE", "Daten verstehen",
                  notes="GOOGL = Alphabet. Daten per API von Yahoo Finance, keine manuelle Eingabe. Zu sehen: der Kursverlauf und die Trennung in Training (alt) und Test (neueste Daten). (ca. 1:00)"))
numbered(s, [f"*GOOGL* (Alphabet), Yahoo Finance via yfinance",
             f"*{info['raw_rows']} Handelstage*\n{info['raw_start']} – {info['raw_end']}",
             "*Ziel:* Kursänderung von heute auf morgen in $"], x=LM, y=2.55, w=4.4, size=20, gap=1.3, label_w=0.6)
picture(s, "01_kurs_mit_split.png", 5.6, 2.5, 6.85)
caption(s, 5.6, 6.2, 6.85, 1)

# 5 Baseline
s = add(new_slide("II · MESSLATTE & KANDIDATEN", "Die Messlatte: drei Regeln",
                  notes="Ein Modell ist nur dann gut, wenn es eine einfache Regel schlägt. Die Persistenz-Regel ist der Standard in der Zeitreihenprognose und folgt aus der Random-Walk-Theorie (Fama, 1970). "
                        "Die Regeln werden auf denselben Testdaten mit denselben Kennzahlen gemessen. (ca. 1:15)"))
numbered(s, ["*Persistenz-Regel:* Kurs morgen = Kurs heute (Random Walk, Fama, 1970)",
             "*SMA-Crossover:* SMA 10 über SMA 50 → steigend, sonst fallend",
             f"*Immer steigend:* Referenz für die Trefferquote – Aufwärtstage im Test: {de(info['up_share_test'], 1)} %"], size=24, gap=1.05)
tb(s, LM, 5.9, CW, 0.4, "Alle Regeln werden auf denselben Testdaten und mit denselben Kennzahlen gemessen wie die Modelle.", 15, SERIF, MUTED, italic=True)

# 6 Modelle
s = add(new_slide("II · MESSLATTE & KANDIDATEN", "Die Kandidaten: drei Modelle",
                  notes="Drei Modelle mit steigender Komplexität. Alle aus scikit-learn, Standardparameter wie gezeigt. (ca. 1:00)"))
cards = [("Lineare Regression", "Gewichtete Summe der Features.\nSehr gut erklärbar."),
         ("Random Forest", "100 Entscheidungsbäume, Tiefe ≤ 5.\nMittelwert aller Bäume (Breiman, 2001)."),
         ("Gradient Boosting", "100 flache Bäume (Tiefe 3).\nJeder korrigiert den Fehler des vorigen (Friedman, 2001).")]
cw = (CW - 0.8) / 3
for i, (name, desc) in enumerate(cards):
    xx = LM + i * (cw + 0.4)
    rule(s, xx, 2.7, cw, MODEL_COLORS[name], 3)
    tb(s, xx, 2.95, cw, 0.3, f"{i + 1:02d}", 11, MONO, MUTED, spc=100)
    tb(s, xx, 3.35, cw, 0.8, name, 24, SERIF, INK, italic=True)
    tb(s, xx, 4.4, cw, 1.6, desc, 18, SERIF, INK, line=1.1, space_after=6)

# 7 Warum
s = add(new_slide("II · MESSLATTE & KANDIDATEN", "Warum diese Modelle?",
                  notes="Begründung der Modellwahl (Aufgabe 3 verlangt sie): Standard, aufsteigende Komplexität, erklärbar. Es geht um den Prozess, nicht um ein High-End-Modell. (ca. 1:00)"))
numbered(s, ["*Standard in scikit-learn:* jeder kann es nachbauen (Pedregosa et al., 2011)",
             "*Aufsteigende Komplexität:* linear → Wald → Boosting. So zeigt sich, ob mehr Komplexität hilft",
             "*Einfach & erklärbar:* passt zur Leitfrage – kein High-End-Modell nötig"], size=24, gap=1.15)

# 8 Training
s = add(new_slide("III · DER TEST", "Training ohne Blick in die Zukunft",
                  notes="Chronologischer Split: die neuesten Daten sind der Test. Zehn Features, nur mit Information bis heute. Vier automatische Prüfungen (assert) fangen Data Leakage ab. (ca. 1:30)"))
numbered(s, [f"*Chronologischer Split:* älteste 80 % Training ({info['train_rows']} Tage), neueste 20 % Test ({info['test_rows']} Tage)",
             f"*{info['n_features']} Features:* Kurs, Volumen, Rendite, 3 Lags, SMA 10/50, Volatilität, RSI (Wilder, 1978)",
             f"*{info['leakage_checks']} automatische Leakage-Prüfungen* per assert – alle bestanden"], size=23, gap=1.15)

# 9 Prognose
rf_mean, gb_mean, real_mean = P["Random Forest"].mean(), P["Gradient Boosting"].mean(), P["Realität"].mean()
s = add(new_slide("III · DER TEST", "Prognose: Realität gegen Modelle",
                  notes="Grau: reale Tagesänderung. Die lineare Regression ist fast flach. Random Forest und Gradient Boosting prognostizieren über Monate Anstiege, die so nicht eintreten. (ca. 1:30)"))
picture(s, "02_prognose_test.png", LM, 2.4, 7.6)
caption(s, LM, 6.4, 7.6, 2)
tb(s, 8.8, 2.6, 3.7, 3.6,
   f"*Lineare Regression:* fast flach, sagt kaum Bewegung voraus\n"
   f"*Random Forest & Gradient Boosting:* im Mittel {de(rf_mean, 1)} bzw. {de(gb_mean, 1)} $ pro Tag prognostiziert\n"
   f"*Realität:* im Mittel {de(real_mean, 1)} $ pro Tag",
   17, SERIF, INK, line=1.05, space_after=14)

# 10 Training vs Test
s = add(new_slide("III · DER TEST", "Training vs. Test: Overfitting",
                  notes="Die Aufgabe verlangt die Bewertung in beiden Zeiträumen. Im Training sieht Gradient Boosting stark aus, im Test bricht es ein. Das ist klassisches Overfitting. (ca. 1:00)"))
cd = CategoryChartData()
cd.categories = MODELS
cd.add_series("Training", [m(n, "Training", "R2") for n in MODELS])
cd.add_series("Test", [m(n, "Test", "R2") for n in MODELS])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(LM), Inches(2.4), Inches(7.4), Inches(4.0), cd)
ch = gf.chart
style_chart(ch)
ch.has_title = True
ch.chart_title.text_frame.text = "Bestimmtheitsmaß R²"
r = ch.chart_title.text_frame.paragraphs[0].runs[0]
r.font.size, r.font.italic, r.font.name = Pt(14), True, SERIF
r.font.color.rgb = rgb(INK)
ch.chart_title.include_in_layout = False
ch.has_legend = True
ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.BOTTOM, False
ch.legend.font.size = Pt(12)
plot = ch.plots[0]
plot.gap_width, plot.overlap = 60, -5
plot.has_data_labels = True
plot.data_labels.number_format, plot.data_labels.number_format_is_linked = "0.00", False
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
plot.data_labels.font.size = Pt(12)
for ser, col in zip(plot.series, ("B5B3AB", INK)):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
_axes(ch, None, None, None)
caption(s, LM, 6.45, 7.4, 3, " (native PowerPoint-Grafik)")
gbt, gbs = m("Gradient Boosting", "Training", "R2"), m("Gradient Boosting", "Test", "R2")
tb(s, 8.7, 2.55, 3.8, 3.6,
   f"*Gradient Boosting:* R² {de(gbt)} im Training, {de(gbs)} im Test\n"
   f"*Random Forest:* {de(m('Random Forest', 'Training', 'R2'))} → {de(m('Random Forest', 'Test', 'R2'))}\n"
   "Gelernte Muster tragen nicht in den Testzeitraum",
   17, SERIF, INK, line=1.05, space_after=14)

# 11 Modellvergleich
s = add(new_slide("IV · DIE ANTWORT", "Modellvergleich im Test",
                  notes="Links: mittlerer absoluter Fehler, kleiner ist besser. Die Persistenz-Regel ist schwer zu schlagen. Rechts: Trefferquote der Richtung, die Marke ist 50 Prozent. "
                        "Kennzahlen: MAE, RMSE, R² und Trefferquote, Formeln unten. (ca. 1:30)"))
order_mae = ["Persistenz-Regel", "SMA-Crossover", "Immer steigend", "Lineare Regression", "Random Forest", "Gradient Boosting"]
native_bar(s, LM, 2.3, 5.7, 3.5, [SHORT[n] for n in order_mae], [m(n, "Test", "MAE") for n in order_mae],
           [MODEL_COLORS[n] for n in order_mae], "0.0", vmin=0, title="MAE in $ (kleiner ist besser)")
order_hit = ["SMA-Crossover", "Immer steigend", "Lineare Regression", "Random Forest", "Gradient Boosting"]
native_bar(s, 6.9, 2.3, 5.55, 3.5, [SHORT[n] for n in order_hit], [m(n, "Test", "Trefferquote") for n in order_hit],
           [MODEL_COLORS[n] for n in order_hit], "0.0", vmin=0, vmax=60, major=10, title="Trefferquote in % (Münzwurf = 50 %)")
rule(s, LM, 5.95, CW)
tb(s, LM, 6.05, CW, 0.4,
   "MAE = 1/n · Σ|y − ŷ|    RMSE = √(1/n · Σ(y − ŷ)²)    R² = 1 − SS_res / SS_tot    Trefferquote = Anteil richtiger Richtungen",
   11, MONO, INK)
tb(s, LM, 6.45, CW, 0.3, f"ABB. 4 · {SOURCE} · TESTZEITRAUM {info['test_start']} – {info['test_end']}".upper(), 9, MONO, MUTED, spc=50)

# 12 Antwort
s = add(new_slide("IV · DIE ANTWORT", "Die Antwort auf die Leitfrage",
                  notes="Drei Kriterien, drei Modelle. Entscheidend ist die Tabelle: Kein Modell erfüllt die Kriterien. Das ist eine ehrliche Antwort und passt zur Random-Walk-Hypothese. (ca. 1:00)"))
rows = [["MODELL", "SCHLÄGT PERSISTENZ", "R² > 0", "TREFFERQUOTE > 50 %", "VERTRAUENSWÜRDIG"]]
yn = lambda b: "ja" if bool(b) else "nein"
for n in MODELS:
    c = C.loc[n]
    rows.append([n, yn(c.K1_schlaegt_Persistenz), f"{yn(c.K2_R2_ueber_0)} ({de(m(n, 'Test', 'R2'))})",
                 f"{yn(c.K3_Treffer_signifikant)} (p = {de(c.p_Wert_Treffer)})", yn(c.vertrauenswuerdig)])
table(s, LM, 2.45, CW, rows, [3.0, 2.3, 2.0, 2.7, 2.53], row_h=0.7)
verdict = ("*Nein.* Kein Modell erfüllt eines der drei Kriterien." if n_crit == 0 else
           f"*Nein.* Die Modelle erfüllen nur {n_crit} von 9 Kriterien." if not any_trust else
           "*Teilweise.* Mindestens ein Modell erfüllt alle drei Kriterien.")
tb(s, LM, 5.7, CW, 0.7, verdict, 30, SERIF, INK, italic=False)

# 13 Reflexion
s = add(new_slide("IV · DIE ANTWORT", "Kritische Reflexion",
                  notes="Was lief gut, wo sind die Grenzen, was würde ich ändern. Die Ursache der großen Fehler ist eine Hypothese, kein Beweis. (ca. 1:30)"))
numbered(s, ["*Was lief gut:* durchgängiger Prozess, faire Messlatte, automatische Leakage-Prüfungen",
             f"*Grenzen:* eine Aktie, {info['test_rows']} Testtage. Die Kurse im Test (bis {de(info['close_test_max'], 0)} $) liegen über dem Trainingsmaximum ({de(info['close_train_max'], 0)} $), "
             f"und die Tagesschwankung ist fast doppelt so hoch (Std. {de(info['target_std_test'], 1)} $ statt {de(info['target_std_train'], 1)} $). Bäume extrapolieren nicht: mögliche Ursache der großen Fehler",
             "*Verbesserungen:* stationäre Features (z. B. Abstand zum SMA), Walk-forward-Validierung, mehrere Aktien und Zeiträume"],
         size=19, gap=[1.0, 1.9, 1.0])

# 14 Fazit
s = add(new_slide("IV · DIE ANTWORT", "Fazit",
                  notes="Drei Sätze zum Mitnehmen. (ca. 0:45)"))
numbered(s, [("*Leitfrage:* Nein. Einfache Standardmodelle schlagen in diesem Aufbau nicht einmal die Persistenz-Regel" if not any_trust
              else "*Leitfrage:* Teilweise. Mindestens ein Modell erfüllt alle drei Kriterien"),
             "*Passt zur Random-Walk-Hypothese* (Fama, 1970) – ist aber kein Beweis, sondern ein Test mit einer Aktie",
             "*Der Gewinn ist der Prozess:* sauber, nachvollziehbar und mit anderen Aktien und Modellen wiederholbar"],
         size=23, gap=1.2)

# 15 Backup Training-Prognose
s = add(new_slide("ANHANG", "Zusatz: Prognose im Trainingszeitraum",
                  notes="Backup: Die Aufgabe verlangt die Prognose auch für den Trainingszeitraum."))
picture(s, "03_prognose_training.png", LM, 2.4, 7.6)
caption(s, LM, 6.4, 7.6, 5)
tb(s, 8.8, 2.6, 3.7, 3, "Im Training liegen vor allem Random Forest und Gradient Boosting deutlich näher an der Realität als im Test.", 16, SERIF, INK, line=1.05)

# 16 Abbildungsverzeichnis
s = add(new_slide("ANHANG", "Abbildungsverzeichnis", notes=""))
figs = [("1", "Schlusskurs GOOGL mit Train/Test-Split", 4),
        ("2", "Prognose gegen Realität, Testzeitraum", 9),
        ("3", "Bestimmtheitsmaß R²: Training gegenüber Test", 10),
        ("4", "Modellvergleich im Test: MAE und Trefferquote", 11),
        ("5", "Prognose gegen Realität, Trainingszeitraum", 15)]
for i, (nr, name, fol) in enumerate(figs):
    yy = 2.5 + i * 0.7
    tb(s, LM, yy + 0.06, 1.5, 0.3, f"ABB. {nr}", 11, MONO, MUTED, spc=100)
    tb(s, LM + 1.5, yy, 8.0, 0.5, name, 20, SERIF, INK)
    tb(s, W - LM - 2, yy + 0.06, 2, 0.3, f"FOLIE {fol}", 11, MONO, MUTED, align=PP_ALIGN.RIGHT, spc=100)
    rule(s, LM, yy + 0.55, CW)
tb(s, LM, 6.05, CW, 0.4, f"Alle Abbildungen: {SOURCE}, Abruf {info['run_date']}.", 14, SERIF, MUTED, italic=True)

# 17 Literatur
s = add(new_slide("ANHANG", "Literaturverzeichnis", notes=""))
lit = ["Breiman, L. (2001). Random Forests. *Machine Learning, 45*(1), 5–32.",
       "Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *The Journal of Finance, 25*(2), 383–417.",
       "Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189–1232.",
       "Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.",
       "Wilder, J. W. (1978). *New concepts in technical trading systems.* Trend Research.",
       "Aroussi, R. (o. J.). *yfinance* [Software]. https://github.com/ranaroussi/yfinance"]
tb(s, LM, 2.45, CW, 4.2, "\n".join(lit), 16, SERIF, INK, line=1.05, space_after=9)

# ---------- Zusammensetzen: Seitenzahlen ----------
total = len(S)
for i, sl in enumerate(S, start=1):
    decorate(sl, i, total, with_header=(i != 1))

prs.save(OUT)
print(f"Gespeichert: {OUT} ({total} Folien)")
