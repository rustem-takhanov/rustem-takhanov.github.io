# Figure plates for the kissing-number papers

The four kissing-number pages (signed Johnson graphs, the 841st sphere, the quaternionic
construction, dimensions 25–31) show a figure plate instead of a single picture: one large
figure, a ledger of the parts, one or two exact companion figures and notes on how to read
them. The style follows the Cohn–Li Cap Atlas: caps for points, white dots for contacts,
dashed circles for empty sites, angle scales drawn to scale.

The site build does not run this code. It copies the finished SVG files from
`_source/illustrations/kissing_svg/`, and the captions, ledgers and notes live in
`_source/illustrations/kissing.py`, so `python build.py` still needs only the standard library.

## Regenerating the SVG files

Requirements: Python 3.9+, NumPy, fontTools and Matplotlib (only for its bundled STIXGeneral
font, used as a fallback for a few mathematical symbols).

Fonts: clone `https://github.com/IBM/plex` and `https://github.com/stipub/stixfonts` (both SIL
Open Font License) into one folder, named `plex` and `stix`, and point `KISSING_FONT_DIR` at
that folder. Each SVG embeds only the glyphs it uses, under the neutral names PlateSans,
PlateMono, PlateSerif and PlateMath.

From the source root (the folder containing `build.py`):

```bash
KISSING_FONT_DIR=/path/to/fonts python3 tools/kissing_figures/generate.py
```

The font directory must be supplied explicitly; the generator reports a missing
directory or font file rather than relying on a path from its original computer.

Optional: set `KISSING_CERT_DIR` to the unpacked `kissing_final_certificates` folder of
`github.com/k-nic/kissing_d25-31`; the script then re-derives the angles of the slack figure
from the certificates and checks them against the stored values.
If this variable is set to a missing directory, generation stops with an error
instead of silently skipping the certificate check. With the variable unset,
the supplied angles are used and no certificate recomputation is performed.

## What is checked before anything is drawn (`data.py`)

- Construction 1 of the signed-Johnson-graph paper (n = 12) with classical free zones, and with
  a free zone glued from two codes by Lemma 3: 840 unit vectors, largest inner product ½.
- The starting configuration of the 841 paper (Example 1 in both blocks, 720 bridges): 840 unit
  vectors, largest inner product ½; the turning curve is computed point by point and matches
  the closed form (√2/3)(cos θ + |sin θ|) beyond ±3.59°.
- The quaternionic 840-point model: all 352,380 inner products match the table in the paper.
- The lifting slice: 12 caps, 24 contacts, each removed owner overlapping its three lifted
  points.

## Files

- `capdraw.py`: SVG document, font subsetting and the orthographic cap-globe renderer.
- `data.py`: the exact constructions and their checks.
- `figures.py`: the eleven figures.
- `generate.py`: entry point; writes `../../illustrations/kissing_svg/*.svg`.
