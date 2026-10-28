#!/usr/bin/env python3
"""Regenerate the SVG figures of the four kissing-number plates.

Development tool (NumPy and fontTools required); the site build itself only copies
the SVG files written here. Font sources: IBM Plex (github.com/IBM/plex) and STIX Two
(github.com/stipub/stixfonts), both under the SIL Open Font License; set
KISSING_FONT_DIR to the folder holding the two checkouts. Subsets are embedded in each
SVG under neutral family names.

    python3 generate.py            # writes ../../illustrations/kissing_svg/*.svg
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import data      # noqa: E402
import figures   # noqa: E402

OUT = HERE.parent.parent / 'illustrations' / 'kissing_svg'

# The first figure of each plate keeps the paper's original file name, so uploading
# the rebuilt site replaces the old picture in place.
FIGURES = {
    'signed-johnson-graphs': figures.fig_a_hero,
    'signed-johnson-graphs-gluing': figures.fig_a_glue,
    'signed-johnson-graphs-angles': figures.fig_a_angles,
    '841st-sphere': figures.fig_b_hero,
    '841st-sphere-equator': figures.fig_b_equator,
    '841st-sphere-turning': figures.fig_b_turn,
    'quaternionic-kissing': figures.fig_c_hero,
    'quaternionic-kissing-contacts': figures.fig_c_contacts,
    'quaternionic-kissing-angles': figures.fig_c_fingerprint,
    'kissing-dimensions-25-31': figures.fig_d_hero,
    'kissing-dimensions-25-31-slack': figures.fig_d_slack,
}


def main():
    checks = data.summary()
    print('checks passed:', ', '.join(sorted(checks)))
    redo = data.recompute_slack()
    if redo:
        for key in ('d29', 'd31'):
            for k, v in redo[key].items():
                assert abs(v - data.SLACK[key][k]) < 5e-4, (key, k, v)
        for k, v in redo['before29'].items():
            assert abs(v - data.SLACK['before'][k]) < 5e-4, (k, v)
        print('certificate angles re-derived:', redo['n29'], redo['n31'])
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGURES.items():
        doc = fn()
        if isinstance(doc, tuple):
            doc = doc[0]
        svg = doc.svg()
        (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
        print(f'{name}.svg  {doc.w}x{doc.h}  {len(svg) // 1024} KB')


if __name__ == '__main__':
    main()
