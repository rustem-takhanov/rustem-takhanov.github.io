"""Drawing helpers for the kissing-number figure plates (Cap Atlas style).

Development tool, not part of the site build. Requires NumPy and fontTools.
The site build only copies the SVG files this package writes to
``_source/illustrations/kissing_svg``.
"""
from __future__ import annotations

import base64
import io
import math
import os
from html import escape
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------
# Palette (the Cohn-Li Cap Atlas tokens, light theme)
# --------------------------------------------------------------------------
BG = '#eef2f5'
PANEL = '#e2e8ee'
FG = '#15202b'
MUTED = '#536171'
RULE = '#c3cdd7'
CORE = '#a3b5c7'
SEAM = '#46525f'
NET_A = '#d45d27'   # orange
NET_B = '#bd3479'   # magenta
NET_C = '#b0840b'   # gold
NET_D = '#6b4bc0'   # violet
NET_E = '#1d7f86'   # teal (fifth colour, used only where five classes are needed)
DOT = '#ffffff'

LIGHT = np.array([-0.45, 0.55, 0.72])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------
FONT_DIR = Path(os.environ['KISSING_FONT_DIR']).expanduser() if os.environ.get('KISSING_FONT_DIR') else None
FONT_FILES = {
    'sans': 'plex/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf',
    'sans-m': 'plex/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Medium.ttf',
    'sans-sb': 'plex/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-SemiBold.ttf',
    'mono': 'plex/packages/plex-mono/fonts/complete/ttf/IBMPlexMono-Regular.ttf',
    'mono-m': 'plex/packages/plex-mono/fonts/complete/ttf/IBMPlexMono-Medium.ttf',
    'serif': 'stix/source/STIXTwoText-Regular.input.ttf',
    'serif-i': 'stix/source/STIXTwoText-Italic.input.ttf',
    'math': 'STIXGeneral.ttf',   # fallback for operators STIX Two Text lacks
}
# Local family names: subsets are embedded under neutral names, not the
# reserved font names of the original families.
FAMILY = {
    'sans': ('PlateSans', 400, 'normal'),
    'sans-m': ('PlateSans', 500, 'normal'),
    'sans-sb': ('PlateSans', 600, 'normal'),
    'mono': ('PlateMono', 400, 'normal'),
    'mono-m': ('PlateMono', 500, 'normal'),
    'serif': ('PlateSerif', 400, 'normal'),
    'serif-i': ('PlateSerif', 400, 'italic'),
    'math': ('PlateMath', 400, 'normal'),
}
STACK = {
    'PlateSans': "PlateSans, 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif",
    'PlateMono': "PlateMono, 'IBM Plex Mono', Menlo, Consolas, monospace",
    'PlateSerif': "PlateSerif, PlateMath, 'STIX Two Text', 'Times New Roman', serif",
    'PlateMath': "PlateMath, 'STIXGeneral', 'Cambria Math', serif",
}


def _font_path(role):
    rel = FONT_FILES[role]
    if role == 'math':
        import matplotlib
        return Path(matplotlib.get_data_path()) / 'fonts/ttf' / rel
    if FONT_DIR is None:
        raise FileNotFoundError('Set KISSING_FONT_DIR to the folder containing the plex and stix font checkouts; see tools/kissing_figures/README.md.')
    path = FONT_DIR / rel
    if not path.is_file():
        raise FileNotFoundError(f'Missing font {path}; check KISSING_FONT_DIR and the font setup in tools/kissing_figures/README.md.')
    return path


def subset_woff(role, chars):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    font = TTFont(str(_font_path(role)))
    cmap = font.getBestCmap()
    usable = sorted({c for c in chars if ord(c) in cmap})
    if not usable:
        return None, set()
    opts = subset.Options()
    opts.flavor = 'woff'
    opts.layout_features = ['kern', 'tnum', 'lnum']
    opts.hinting = False
    opts.name_IDs = []
    opts.name_legacy = False
    opts.notdef_outline = False
    opts.glyph_names = False
    opts.drop_tables += ['FFTM', 'meta']
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[ord(c) for c in usable])
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = 'woff'
    font.save(buf)
    return buf.getvalue(), set(usable)


def fmt(x):
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    s = f'{float(x):.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(a[k] + (b[k] - a[k]) * t):02x}' for k in range(3))


def shade(hexcol, n, ambient=0.58, diffuse=0.5):
    f = ambient + diffuse * max(float(np.dot(n, LIGHT)), 0.0)
    rgb = [min(255, round(int(hexcol[i:i + 2], 16) * f)) for i in (1, 3, 5)]
    return '#' + ''.join(f'{v:02x}' for v in rgb)


# --------------------------------------------------------------------------
# SVG document
# --------------------------------------------------------------------------
class Doc:
    def __init__(self, width, height, title, desc='', background=PANEL):
        self.w, self.h = width, height
        self.title, self.desc = title, desc
        self.parts = []
        self.defs = []
        self.chars = {}
        self._ids = 0
        if background:
            self.parts.append(f'<rect width="{width}" height="{height}" fill="{background}"/>')

    def uid(self, prefix='g'):
        self._ids += 1
        return f'{prefix}{self._ids}'

    def add(self, markup):
        self.parts.append(markup)

    # ---- text ---------------------------------------------------------
    def _track(self, role, s):
        self.chars.setdefault(role, set()).update(s)
        if role in ('serif', 'serif-i'):
            self.chars.setdefault('math', set()).update(s)

    def text(self, x, y, runs, size=14, fill=FG, anchor='start', role='sans',
             spacing=None, opacity=None, extra=''):
        """runs: a string, or a list of (role, string) / (role, string, attrs)."""
        if isinstance(runs, str):
            runs = [(role, runs)]
        fam0, w0, st0 = FAMILY[runs[0][0]]
        attrs = (f'x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(size)}" fill="{fill}" '
                 f'text-anchor="{anchor}"')
        if spacing:
            attrs += f' letter-spacing="{spacing}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        out = []
        for run in runs:
            r, s = run[0], run[1]
            extra_run = run[2] if len(run) > 2 else ''
            self._track(r, s)
            fam, w, st = FAMILY[r]
            out.append(f'<tspan font-family="{STACK[fam]}" font-weight="{w}" font-style="{st}"'
                       + (f' {extra_run}' if extra_run else '') + f'>{escape(s)}</tspan>')
        self.parts.append(f'<text {attrs}{(" " + extra) if extra else ""}>' + ''.join(out) + '</text>')

    # ---- primitives ---------------------------------------------------
    def line(self, x1, y1, x2, y2, stroke=FG, width=1, dash=None, opacity=None, cap='round'):
        a = f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{stroke}" stroke-width="{fmt(width)}" stroke-linecap="{cap}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.parts.append(a + '/>')

    def path(self, d, stroke='none', width=1, fill='none', dash=None, opacity=None, join='round', cap='round', extra=''):
        a = f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{fmt(width)}" stroke-linejoin="{join}" stroke-linecap="{cap}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if extra:
            a += ' ' + extra
        self.parts.append(a + '/>')

    def circle(self, x, y, r, fill=FG, stroke='none', width=1, dash=None, opacity=None):
        a = f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}"'
        if stroke != 'none':
            a += f' stroke="{stroke}" stroke-width="{fmt(width)}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.parts.append(a + '/>')

    def rect(self, x, y, w, h, fill=PANEL, stroke='none', width=1, rx=0, opacity=None, dash=None):
        a = f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(rx)}" fill="{fill}"'
        if stroke != 'none':
            a += f' stroke="{stroke}" stroke-width="{fmt(width)}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.parts.append(a + '/>')

    def polyline(self, pts, **kw):
        d = 'M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts)
        self.path(d, **kw)

    def cap2d(self, x, y, r, fill, stroke=BG, width=1.2):
        """A flat cap glyph for 2-D charts (Cap Atlas cube-figure style)."""
        self.circle(x, y, r, fill=fill, stroke=stroke, width=width)

    def empty2d(self, x, y, r, stroke=FG, width=1.2, dash='3 2.4', fill=BG):
        self.circle(x, y, r, fill=fill, stroke=stroke, width=width, dash=dash)

    def arrow(self, x1, y1, x2, y2, stroke=MUTED, width=1.2, head=6):
        self.line(x1, y1, x2, y2, stroke, width)
        ang = math.atan2(y2 - y1, x2 - x1)
        pts = [(x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42)), (x2, y2),
               (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))]
        self.polyline(pts, stroke=stroke, width=width)

    # ---- output -------------------------------------------------------
    def svg(self):
        faces = []
        for role, chars in sorted(self.chars.items()):
            if not chars:
                continue
            data, used = subset_woff(role, chars)
            if data is None:
                continue
            fam, w, st = FAMILY[role]
            b64 = base64.b64encode(data).decode('ascii')
            faces.append(f"@font-face{{font-family:{fam};font-weight:{w};font-style:{st};"
                         f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
        style = '<style>' + ''.join(faces) + 'text{font-kerning:normal}</style>' if faces else ''
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d">'
                f'<title id="t">{escape(self.title)}</title><desc id="d">{escape(self.desc)}</desc>')
        defs = ('<defs>' + ''.join(self.defs) + '</defs>') if self.defs else ''
        return head + style + defs + ''.join(self.parts) + '</svg>'


# --------------------------------------------------------------------------
# Cap globes (orthographic view of a unit sphere with spherical caps)
# --------------------------------------------------------------------------
def rot(axis, ang):
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s, t = math.cos(ang), math.sin(ang), 1 - math.cos(ang)
    return np.array([[c + t * x * x, t * x * y - s * z, t * x * z + s * y],
                     [t * x * y + s * z, c + t * y * y, t * y * z - s * x],
                     [t * x * z - s * y, t * y * z + s * x, c + t * z * z]])


def view_matrix(azimuth_deg, elevation_deg):
    """Model z is 'up'. Returns M with view = M @ model (x right, y up, z to viewer)."""
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    # model -> camera: first spin about model z, then tilt so model z points up-ish
    Rz = rot([0, 0, 1], -az)
    base = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)  # model (x,y,z) -> view (x, z, -y)
    Rx = rot([1, 0, 0], el)
    return Rx @ base @ Rz


def _basis(m):
    a = np.array([0.0, 0.0, 1.0]) if abs(m[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(m, a)
    u /= np.linalg.norm(u)
    w = np.cross(m, u)
    return u, w


def cap_outline(m, r, n=240):
    """Visible part of the spherical cap {p : p.m >= cos r} in view coordinates.

    Returns ('ellipse', (cx, cy, rx, ry, angle_deg)), ('poly', [(x, y), ...]) or (None, None).
    Coordinates are on the unit disc (y up)."""
    m = np.asarray(m, float)
    m = m / np.linalg.norm(m)
    theta = math.acos(max(-1.0, min(1.0, m[2])))
    if theta - r >= math.pi / 2:
        return None, None
    if theta + r <= math.pi / 2:
        cx, cy = math.cos(r) * m[0], math.cos(r) * m[1]
        a = math.sin(r)
        b = math.sin(r) * abs(m[2])
        ang = math.degrees(math.atan2(m[1], m[0])) + 90 if (m[0] ** 2 + m[1] ** 2) > 1e-12 else 0.0
        return 'ellipse', (cx, cy, a, b, ang)
    u, w = _basis(m)
    ts = np.linspace(0, 2 * math.pi, n, endpoint=False)
    P = (math.cos(r) * m)[None, :] + math.sin(r) * (np.cos(ts)[:, None] * u[None, :] + np.sin(ts)[:, None] * w[None, :])
    vis = P[:, 2] >= 0
    if not vis.any():
        return None, None
    # rotate so that we start right after an invisible sample
    k0 = int(np.argmax(~vis))
    order = [(k0 + i) % n for i in range(n)]
    seq = [i for i in order if vis[i]]
    # entry crossing (between previous invisible and first visible)
    def cross(i_in, i_out):
        a, b = P[i_out], P[i_in]
        t = a[2] / (a[2] - b[2])
        return a + (b - a) * t
    first, last = seq[0], seq[-1]
    p_start = cross(first, (first - 1) % n)
    p_end = cross(last, (last + 1) % n)
    pts = [p_start] + [P[i] for i in seq] + [p_end]
    # limb arc from p_end back to p_start, passing on the side of m
    a1 = math.atan2(p_end[1], p_end[0])
    a0 = math.atan2(p_start[1], p_start[0])
    am = math.atan2(m[1], m[0])
    def ccw(a, b):
        return (b - a) % (2 * math.pi)
    # two candidate arcs: ccw from a1 to a0, or cw from a1 to a0
    if ccw(a1, am) <= ccw(a1, a0):
        span = ccw(a1, a0)
        arc = [a1 + span * s for s in np.linspace(0, 1, 40)[1:-1]]
    else:
        span = ccw(a0, a1)
        arc = [a1 - span * s for s in np.linspace(0, 1, 40)[1:-1]]
    pts += [np.array([math.cos(a), math.sin(a), 0.0]) for a in arc]
    return 'poly', [(p[0], p[1]) for p in pts]


def front_arc(m, r, n=240):
    """Visible part of the boundary circle only (for dashed outlines)."""
    m = np.asarray(m, float)
    m = m / np.linalg.norm(m)
    u, w = _basis(m)
    ts = np.linspace(0, 2 * math.pi, n + 1)
    P = (math.cos(r) * m)[None, :] + math.sin(r) * (np.cos(ts)[:, None] * u[None, :] + np.sin(ts)[:, None] * w[None, :])
    segs, cur = [], []
    for p in P:
        if p[2] >= 0:
            cur.append((p[0], p[1]))
        elif cur:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    if len(segs) > 1 and P[0][2] >= 0 and P[-1][2] >= 0:
        segs = [segs[-1] + segs[0]] + segs[1:-1]
    return segs


class Globe:
    """An orthographic globe drawn into a Doc at centre (cx, cy) with radius R (pixels)."""

    def __init__(self, doc, cx, cy, R, M):
        self.doc, self.cx, self.cy, self.R, self.M = doc, cx, cy, R, M

    def to_px(self, x, y):
        return self.cx + self.R * x, self.cy - self.R * y

    def view(self, v):
        v = np.asarray(v, float)
        return self.M @ (v / np.linalg.norm(v))

    def sphere(self, seam=SEAM, rim=None):
        gid = self.doc.uid('sph')
        lx, ly = LIGHT[0] * 0.55, LIGHT[1] * 0.55
        fx, fy = 0.5 + lx / 2, 0.5 - ly / 2
        c_hi = shade(seam, LIGHT, 0.6, 0.45)
        c_mid = shade(seam, np.array([0, 0, 1.0]), 0.6, 0.45)
        c_lo = shade(seam, -LIGHT, 0.6, 0.45)
        self.doc.defs.append(
            f'<radialGradient id="{gid}" cx="{fmt(fx)}" cy="{fmt(fy)}" r="0.78" fx="{fmt(fx)}" fy="{fmt(fy)}">'
            f'<stop offset="0" stop-color="{c_hi}"/><stop offset="0.55" stop-color="{c_mid}"/>'
            f'<stop offset="1" stop-color="{c_lo}"/></radialGradient>')
        self.doc.circle(self.cx, self.cy, self.R, fill=f'url(#{gid})')
        if rim:
            self.doc.circle(self.cx, self.cy, self.R, fill='none', stroke=rim, width=1)

    def cap(self, direction, r, fill, ambient=0.58, diffuse=0.5, opacity=None, stroke=None, width=1.0):
        m = self.view(direction)
        kind, data = cap_outline(m, r)
        if kind is None:
            return
        col = shade(fill, m, ambient, diffuse)
        extra = ''
        if stroke:
            extra = f' stroke="{stroke}" stroke-width="{fmt(width)}"'
        op = f' opacity="{opacity}"' if opacity is not None else ''
        if kind == 'ellipse':
            cx, cy, a, b, ang = data
            X, Y = self.to_px(cx, cy)
            self.doc.add(f'<ellipse cx="{fmt(X)}" cy="{fmt(Y)}" rx="{fmt(a * self.R)}" ry="{fmt(max(b, 1e-4) * self.R)}" '
                         f'transform="rotate({fmt(-ang)} {fmt(X)} {fmt(Y)})" fill="{col}"{extra}{op}/>')
        else:
            pts = [self.to_px(x, y) for x, y in data]
            self.doc.add('<path d="M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts) + f'Z" fill="{col}"{extra}{op}/>')

    def outline(self, direction, r, stroke, width=1.4, dash='5 4', opacity=None):
        m = self.view(direction)
        for seg in front_arc(m, r):
            pts = [self.to_px(x, y) for x, y in seg]
            if len(pts) < 2:
                continue
            self.doc.path('M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts), stroke=stroke, width=width,
                          dash=dash, opacity=opacity)

    def dot(self, direction, r, fill=DOT):
        m = self.view(direction)
        if m[2] <= 0.02:
            return
        self.cap(direction, r, fill, ambient=1.0, diffuse=0.0)

    def great_circle(self, normal, stroke, width=1, dash=None, opacity=None, back=False):
        """Front (or back) half of the great circle orthogonal to `normal` (model coords)."""
        nrm = np.asarray(normal, float)
        nrm /= np.linalg.norm(nrm)
        u, w = _basis(nrm)
        ts = np.linspace(0, 2 * math.pi, 361)
        P = [self.M @ (math.cos(t) * u + math.sin(t) * w) for t in ts]
        segs, cur = [], []
        for p in P:
            if (p[2] >= 0) != back:
                cur.append(self.to_px(p[0], p[1]))
            elif cur:
                segs.append(cur)
                cur = []
        if cur:
            segs.append(cur)
        for seg in segs:
            if len(seg) > 1:
                self.doc.path('M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in seg), stroke=stroke, width=width,
                              dash=dash, opacity=opacity)

    def project(self, direction, radius=1.0):
        v = self.M @ (np.asarray(direction, float) / np.linalg.norm(direction)) * radius
        return self.to_px(v[0], v[1]), v[2]


def geodesic(globe, a, b, n=60):
    """Points (px) of the great-circle arc a->b in model coordinates, with visibility flags."""
    a = np.asarray(a, float) / np.linalg.norm(a)
    b = np.asarray(b, float) / np.linalg.norm(b)
    om = math.acos(max(-1, min(1, float(a @ b))))
    out = []
    for t in np.linspace(0, 1, n):
        if om < 1e-9:
            p = a
        else:
            p = (math.sin((1 - t) * om) * a + math.sin(t * om) * b) / math.sin(om)
        v = globe.M @ p
        out.append((globe.to_px(v[0], v[1]), v[2] >= 0))
    return out
