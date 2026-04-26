#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#python manadsoversikt_a3_portrait_matplotlib.py --period 2025-08 -n Lina David Nora Nils Lykke

#python manadsoversikt_a3_portrait_matplotlib.py --period 2025-08 \
#  -n Lina David Nora Nils Lykke \
#  --font-ttf /sökväg/till/HelveticaNeue.ttf

import os
import argparse
import calendar
from datetime import date

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager as fm

SWEDISH_MONTHS = [
    "januari", "februari", "mars", "april", "maj", "juni",
    "juli", "augusti", "september", "oktober", "november", "december"
]

def parse_period(period_str: str):
    try:
        year_str, month_str = period_str.split("-")
        year = int(year_str); month = int(month_str)
        assert 1 <= month <= 12
        return year, month
    except Exception as e:
        raise argparse.ArgumentTypeError(
            "Ange --period i formatet ÅÅÅÅ-MM, t.ex. 2025-08"
        ) from e

def build_table_data(year: int, month: int, names: list[str]):
    days_in_month = calendar.monthrange(year, month)[1]
    header = ["Datum"] + names
    rows = []
    for d in range(1, days_in_month + 1):
        rows.append([f"{d}"] + [""] * len(names))  # endast datum-siffran
    return header, rows

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generera stående A3-PDF med månadsöversikt: datum (1..31) + en kolumn per namn."
    )
    parser.add_argument("--period", required=True, help="ÅÅÅÅ-MM, t.ex. 2025-08")
    parser.add_argument(
        "-n", "--names", nargs="+",
        default=["Lina", "David", "Nora", "Nils", "Lykke"],
        help='Namnlistan, t.ex.: -n Lina David Nora Nils Lykke'
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="Filnamn för PDF (default: kalender_ÅÅÅÅ_MM_A3_portrait.pdf)"
    )
    parser.add_argument(
        "--font-ttf", default=None,
        help="Sökväg till Helvetica Neue .ttf (valfritt, t.ex. /path/HelveticaNeue.ttf)"
    )
    parser.add_argument(
        "--left-col-frac", type=float, default=0.10,
        help="Andel av sidans bredd för datumkolumnen (0–1). Default 0.10"
    )
    parser.add_argument(
        "--no-weekend-shade", action="store_true",
        help="Stäng av skuggning av lördag/söndag"
    )
    args = parser.parse_args(argv)

    year, month = parse_period(args.period)
    out_path = args.output or f"kalender_{year}_{str(month).zfill(2)}_A3_portrait.pdf"

    # Font-inställning: försök registrera angiven TTF; annars fall-back
    if args.font_ttf and os.path.exists(args.font_ttf):
        try:
            fm.fontManager.addfont(args.font_ttf)
            font_name = fm.FontProperties(fname=args.font_ttf).get_name()
            plt.rcParams['font.family'] = font_name
        except Exception:
            plt.rcParams['font.family'] = 'DejaVu Sans'
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'

    # Bättre TTF-inbäddning i PDF
    plt.rcParams['pdf.fonttype'] = 42  # TrueType
    plt.rcParams['ps.fonttype'] = 42

    header, rows = build_table_data(year, month, args.names)

    # A3 porträtt i tum
    fig_w, fig_h = 11.69, 16.54

    with PdfPages(out_path) as pdf:
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.axis('off')

        # Titel: enbart månadens namn
        month_name = SWEDISH_MONTHS[month-1].capitalize()
        ax.set_title(f"{month_name}", fontsize=26, pad=18, fontweight='bold')

        # Marginaler (ax-koordinater 0..1)
        left_margin = 0.05
        right_margin = 0.05
        top_margin = 0.10
        bottom_margin = 0.04
        table_width = 1 - left_margin - right_margin
        table_height = 1 - top_margin - bottom_margin
        bbox = [left_margin, 1 - top_margin - table_height, table_width, table_height]

        total_cols = 1 + len(args.names)
        left_col_frac = max(0.04, min(args.left_col_frac, 0.30))  # rimlig spärr
        person_col_frac = (1 - left_col_frac) / len(args.names) if args.names else 1.0
        col_widths = [left_col_frac] + [person_col_frac] * len(args.names)

        # Tabell
        table = ax.table(
            cellText=rows,
            colLabels=header,
            cellLoc='center',
            loc='upper left',
            colWidths=col_widths,
            bbox=bbox
        )

        table.auto_set_font_size(False)
        table.set_fontsize(10)

        # Header-stil
        for c in range(total_cols):
            cell = table[(0, c)]
            cell.set_text_props(fontweight='bold', fontsize=12)

        # Rutnät & helgskuggning
        days_in_month = calendar.monthrange(year, month)[1]
        for i in range(days_in_month):
            wd = date(year, month, i+1).weekday()
            for c in range(total_cols):
                cell = table[(i+1, c)]  # +1 pga header-rad index 0
                cell.set_edgecolor('black')
                if not args.no_weekend_shade and wd >= 5:  # lör/sön
                    cell.set_facecolor((0.95, 0.95, 0.95))

        # Sätt kantlinjer även på headern
        for c in range(total_cols):
            table[(0, c)].set_edgecolor('black')

        # Export
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    print(f"✅ Klart! Skapade {out_path}")

if __name__ == "__main__":
    main()

