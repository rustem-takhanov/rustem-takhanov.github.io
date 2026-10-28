"""The eleven SVG figures of the kissing-number plates.

Run ``python3 generate.py`` (NumPy and fontTools required) to rewrite them into
``_source/illustrations/kissing_svg``.
"""
from __future__ import annotations

import itertools as it
import math

import numpy as np

from capdraw import (BG, CORE, DOT, FG, MUTED, NET_A, NET_B, NET_C, NET_D, NET_E, PANEL, RULE, SEAM,
                     Doc, Globe, fmt, mix, view_matrix)
import data

CLASS_COLOURS = [NET_A, NET_B, NET_C, NET_D, NET_E]
AXIAL = '#8597a9'          # fixed coordinate points: a darker core grey
CAP_GAP = math.radians(1.7)  # drawn caps are this much smaller than touching size


# ==========================================================================
# shared pieces
# ==========================================================================
def tesseract_positions(cx, cy, s):
    """Positions of the 16 vertices of a 4-cube (sign vectors) in a fixed oblique projection."""
    dirs = [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([0.62, 0.42]), np.array([-0.30, 0.55])]
    dirs = [d * s for d in dirs]
    pos = {}
    for signs in it.product((1, -1), repeat=4):
        p = sum(0.5 * sg * d for sg, d in zip(signs, dirs))
        pos[signs] = (cx + p[0], cy - p[1])
    return pos


def cube_edges(signs_list):
    out = []
    for a in signs_list:
        for b in signs_list:
            if a < b and sum(x != y for x, y in zip(a, b)) == 1:
                out.append((a, b))
    return out


def scale_axis(doc, x0, x1, y, lo, hi, ticks, label_fmt='{:g}°', size=11, tick=4):
    doc.line(x0, y, x1, y, FG, 1)
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    for t in ticks:
        doc.line(X(t), y, X(t), y + tick, FG, 1)
        doc.text(X(t), y + tick + size + 2, [('mono', label_fmt.format(t))], size=size, fill=MUTED, anchor='middle')
    return X


# ==========================================================================
# Plate D: dimensions 25-31
# ==========================================================================
def spread(ys, gap, lo, hi):
    """Push label positions apart (keeping order) so neighbours are at least `gap` apart."""
    ys = list(ys)
    for _ in range(200):
        moved = False
        for i in range(1, len(ys)):
            if ys[i] - ys[i - 1] < gap:
                d = (gap - (ys[i] - ys[i - 1])) / 2
                ys[i - 1] -= d
                ys[i] += d
                moved = True
        ys = [min(max(y, lo), hi) for y in ys]
        if not moved:
            break
    return ys


def fig_d_hero():
    lifted, hexagon, owners, contacts = data.lifting_slice()
    doc = Doc(900, 500, 'Leech lifting in one exact slice, and the heights of all blocks',
              'Left: a globe with twelve touching caps of true size. Three lifted caps sit around the removed '
              'owner direction u and three around minus u; six auxiliary caps lie on the equator. Right: a scale '
              'of the angle each kind of block makes with the 24-dimensional Leech space.')
    M = view_matrix(24, 36)
    g = Globe(doc, 232, 258, 206, M)
    g.sphere()
    r = math.radians(30) - CAP_GAP
    P = [(p, NET_A) for p in lifted] + [(p, NET_D) for p in hexagon]
    for p, col in sorted(P, key=lambda pc: (M @ pc[0])[2]):
        g.cap(p, r, col)
    pts = [p for p, _ in P]
    for i, j in contacts:
        g.dot(pts[i] + pts[j], math.radians(2.4))
    for o in owners:
        g.cap(o, math.radians(30), '#ffffff', ambient=1, diffuse=0, opacity=0.14)
        g.outline(o, math.radians(30), '#ffffff', 1.7, '6 5')
        (x, y), z = g.project(o)
        if z > 0:
            doc.circle(x, y, 3.4, fill='#ffffff')
    # callouts: anchor at the most frontal member of each group
    def front(group):
        return max(group, key=lambda p: (M @ (p / np.linalg.norm(p)))[2])

    def callout(p, tx, ty, title, sub, toward=(0.0, 0.0)):
        (x, y), _ = g.project(p, 1.0)
        x, y = x + toward[0], y + toward[1]
        doc.line(x, y, tx - 8, ty - 4, '#ffffff', 3.2, opacity=0.8)
        doc.line(x, y, tx - 8, ty - 4, FG, 1.0)
        doc.circle(x, y, 3, fill=FG, stroke='#ffffff', width=1.2)
        doc.text(tx, ty, [('sans-m', title)], size=13.5, fill=FG)
        doc.text(tx, ty + 16, sub, size=12, fill=MUTED)
    callout(owners[0], 470, 70, 'owner u, removed', [('sans', 'its cap would overlap all three')])
    callout(front(lifted), 470, 176, 'lifted points', [('serif', '(√⅔ u, √⅓ t)'), ('sans', ', three per owner')])
    callout(front(hexagon), 470, 330, 'auxiliary points', [('sans', 'in the plane of the tails t')])
    doc.text(232, 488, [('sans', 'An exact 3-D slice, to scale: twelve caps of angular radius 30°, 24 contacts')],
             size=12, fill=MUTED, anchor='middle')

    # ---- height ladder --------------------------------------------------
    x0, ytop, ybot = 700, 74, 444
    Y = lambda a: ytop + a / 90.0 * (ybot - ytop)
    doc.text(x0 - 72, 34, [('sans-sb', 'Angle out of ℝ²⁴')], size=13.5, fill=FG)
    doc.text(x0 - 72, 51, [('sans', 'every block of the five constructions')], size=11.5, fill=MUTED)
    doc.line(x0, ytop, x0, ybot, FG, 1)
    for t in range(0, 91, 15):
        doc.line(x0 - 3, Y(t), x0 + 3, Y(t), MUTED, 1)
    H = data.HEIGHTS
    rows = [
        ('bulk', CORE, 'Leech shell (bulk)', 'all five'),
        ('moved_bulk_d25', NET_E, '552 moved bulk points', 'd = 25'),
        ('caps_30', NET_B, 'caps, second layer', 'd = 25, 27'),
        ('lifted', NET_A, 'lifted, first layers', 'd = 26, 27, 29, 31'),
        ('frame', NET_C, 'frame layer', 'd = 29, 31'),
        ('auxiliary', NET_D, 'auxiliary block', 'all five'),
    ]
    ys = spread([Y(H[k]) for k, *_ in rows], 34, ytop - 6, ybot)
    for (key, col, name, dims), ty in zip(rows, ys):
        yy = Y(H[key])
        a = H[key]
        lab = f'{a:.2f}°' if abs(a - round(a)) > 1e-6 else f'{a:.0f}°'
        doc.line(x0 + 8, yy, x0 + 20, ty, MUTED, 0.8)
        doc.line(x0 - 8, yy, x0 - 20, ty, MUTED, 0.8)
        doc.circle(x0, yy, 6.5, fill=col, stroke=PANEL, width=1.6)
        doc.text(x0 - 24, ty + 4, [('mono-m', lab)], size=12.5, fill=FG, anchor='end')
        doc.text(x0 + 24, ty, [('sans', name)], size=12.5, fill=FG)
        doc.text(x0 + 24, ty + 15, [('mono' if dims.startswith('d =') else 'sans', dims)], size=11.5, fill=MUTED)
    doc.text(x0 - 72, ybot + 36, [('sans', '0° lies in ℝ²⁴; 90° lies in the extra coordinates')], size=11.5, fill=MUTED)
    return doc


def fig_d_slack():
    S = data.SLACK
    th = S['thresholds']
    doc = Doc(460, 330, 'Smallest angles before and after the rotation, dimensions 29 and 31',
              'Four zoomed angle scales, each starting at its bound. Hollow circles: the previous configurations '
              'with unrotated directions. Orange and violet triangles: the certified configurations in dimensions '
              '29 and 31.')
    rows = [('aux_tail', 'auxiliary point ↔ lifted direction'),
            ('tail_frame', 'lifted direction ↔ frame axis'),
            ('aux_frame', 'auxiliary point ↔ frame axis'),
            ('aux_aux', 'auxiliary point ↔ auxiliary point')]
    x0, x1 = 24, 436
    span = 2.0
    y = 26
    for key, name in rows:
        lo = th[key]
        X = lambda v: x0 + (v - lo) / span * (x1 - x0)
        b, a29, a31 = S['before'][key], S['d29'][key], S['d31'][key]
        doc.text(x0, y, [('sans-m', name), ('mono', f'  ≥ {lo:.2f}°'.replace('.00°', '°'))], size=12.5, fill=FG)
        doc.text(x1, y, [('mono', f'{b:.2f}° → {a29:.2f}° · {a31:.2f}°')], size=11.5, fill=MUTED, anchor='end')
        yl = y + 22
        doc.rect(x0, yl - 6, x1 - x0, 12, fill=BG, rx=2)
        doc.line(x0, yl - 9, x0, yl + 9, FG, 2)
        for t in (0.5, 1.0, 1.5, 2.0):
            doc.line(X(lo + t), yl + 6, X(lo + t), yl + 10, MUTED, 1)
            doc.text(X(lo + t), yl + 21, [('mono', f'+{t:g}°')], size=10, fill=MUTED,
                     anchor='end' if t == 2.0 else 'middle')
        doc.circle(X(b), yl, 5.5, fill=PANEL, stroke=FG, width=1.4)
        tri = lambda x, yy, up, col: doc.path(
            f'M{fmt(x)} {fmt(yy)} L{fmt(x - 5)} {fmt(yy + (-8 if up else 8))} L{fmt(x + 5)} {fmt(yy + (-8 if up else 8))} Z',
            fill=col, stroke=BG, width=1)
        tri(X(a29), yl - 6, True, NET_A)
        tri(X(a31), yl + 6, False, NET_D)
        if b - min(a29, a31) > 0.2:
            doc.arrow(X(b) - 9, yl, X(max(a29, a31)) + 9, yl, MUTED, 1.1, 5)
        y += 72
    ly = 318
    doc.circle(x0 + 6, ly - 4, 5, fill=PANEL, stroke=FG, width=1.3)
    doc.text(x0 + 16, ly, [('sans', 'previous, R = I')], size=11.5, fill=MUTED)
    doc.path(f'M{x0 + 146} {ly} l-5 -8 l10 0 Z', fill=NET_A)
    doc.text(x0 + 156, ly, [('sans', 'd = 29: 34 auxiliary')], size=11.5, fill=MUTED)
    doc.path(f'M{x0 + 296} {ly - 8} l-5 8 l10 0 Z', fill=NET_D)
    doc.text(x0 + 306, ly, [('sans', 'd = 31: 122')], size=11.5, fill=MUTED)
    return doc


# ==========================================================================
# Plate A: signed Johnson graphs
# ==========================================================================
def _k6_positions(cx, cy, R, mirror=False):
    pos = {}
    for k in range(5):
        a = math.radians(90 + (72 * k if mirror else -72 * k))
        pos[k] = (cx + R * math.cos(a), cy - R * math.sin(a))
    pos[5] = (cx, cy)
    return pos


def fig_a_hero():
    classes = data.gk6()
    doc = Doc(900, 500, 'Construction 1: 51 blocks on twelve coordinates from a 1-factorisation of K6',
              'Two copies of the complete graph on six vertices, each with its fifteen edges in five colours. '
              'Curves through five hubs join every edge on the left to every edge of the same colour on the right; '
              'each such pair of edges is a block of four coordinates carrying sixteen sign vectors, drawn as a 4-cube.')
    L = _k6_positions(168, 222, 118)
    Rr = _k6_positions(732, 222, 118, mirror=True)
    mid = lambda P, e: ((P[e[0]][0] + P[e[1]][0]) / 2, (P[e[0]][1] + P[e[1]][1]) / 2)
    hi_class = 0
    hi_block = ((2, 3), (1, 4))       # left edge {3,4}, right edge {2',5'}
    hubs = {c: (450, 112 + 46 * c) for c in range(5)}
    order = [c for c in range(5) if c != hi_class] + [hi_class]
    for c in order:
        hx, hy = hubs[c]
        for side, P in (('L', L), ('R', Rr)):
            for e in classes[c]:
                x, y = mid(P, e)
                sgn = 1 if side == 'L' else -1
                d = (f'M{fmt(x)} {fmt(y)} C{fmt(x + sgn * 150)} {fmt(y)} {fmt(hx - sgn * 120)} {fmt(hy)} '
                     f'{fmt(hx)} {fmt(hy)}')
                is_hi = c == hi_class and e == (hi_block[0] if side == 'L' else hi_block[1])
                doc.path(d, stroke=CLASS_COLOURS[c], width=2.8 if is_hi else 1.3,
                         opacity=1 if is_hi else (0.62 if c == hi_class else 0.42))
    for c in range(5):
        hx, hy = hubs[c]
        doc.circle(hx, hy, 11.5, fill=CLASS_COLOURS[c], stroke=PANEL, width=2)
        doc.text(hx, hy + 4.3, [('mono-m', '9')], size=12, fill='#ffffff', anchor='middle')
    for P, names in ((L, [str(k + 1) for k in range(6)]), (Rr, [f'{k + 1}′' for k in range(6)])):
        for c in range(5):
            for e in classes[c]:
                (x1, y1), (x2, y2) = P[e[0]], P[e[1]]
                doc.line(x1, y1, x2, y2, PANEL, 7)
                doc.line(x1, y1, x2, y2, CLASS_COLOURS[c], 3.0)
        for k in range(6):
            x, y = P[k]
            doc.circle(x, y, 13, fill=CORE, stroke=PANEL, width=2)
            doc.text(x, y + 4.5, [('mono-m', names[k])], size=12.5, fill=FG, anchor='middle')
    for P, e in ((L, hi_block[0]), (Rr, hi_block[1])):
        x, y = mid(P, e)
        doc.circle(x, y, 4.6, fill='#ffffff', stroke=NET_A, width=2)
    doc.text(168, 380, [('sans-m', 'coordinates 1–6')], size=13.5, fill=FG, anchor='middle')
    doc.text(168, 397, [('sans', 'free zone: 48 points + 12 axial points')], size=12, fill=MUTED, anchor='middle')
    doc.text(732, 380, [('sans-m', 'coordinates 1′–6′')], size=13.5, fill=FG, anchor='middle')
    doc.text(732, 397, [('sans', 'free zone: 48 points + 12 axial points')], size=12, fill=MUTED, anchor='middle')
    doc.text(450, 62, [('sans-m', '45 bridge blocks')], size=13.5, fill=FG, anchor='middle')
    doc.text(450, 79, [('sans', 'each hub joins 3 edges to 3 edges of its colour')], size=12, fill=MUTED, anchor='middle')
    # 4-cube of the highlighted block (Petrie projection of the tesseract)
    cx, cy, s = 470, 432, 27
    dirs = [np.array([math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)]) * s for k in range(4)]
    pos = {}
    for signs in it.product((1, -1), repeat=4):
        p = sum(0.5 * sg * d for sg, d in zip(signs, dirs))
        pos[signs] = (cx + p[0], cy - p[1] * 0.92)
    for a, b in cube_edges(list(pos)):
        doc.line(*pos[a], *pos[b], FG, 0.9, opacity=0.35)
    for sg in pos:
        doc.circle(*pos[sg], 5.6, fill=NET_A, stroke=PANEL, width=1.4)
    doc.text(548, 420, [('sans-m', 'one block, 16 points')], size=13, fill=FG)
    doc.text(548, 438, [('serif', '½(±e₃ ± e₄ ± e₂′ ± e₅′)')], size=13.5, fill=FG)
    doc.text(548, 455, [('sans', 'a 4-cube: one sign apart = touching')], size=12, fill=MUTED)
    doc.text(392, 420, [('mono-m', '45 × 16 = 720')], size=12.5, fill=FG, anchor='end')
    doc.text(392, 437, [('mono', ' 2 × 48 =  96')], size=12.5, fill=MUTED, anchor='end')
    doc.text(392, 454, [('mono', '12 ×  2 =  24')], size=12.5, fill=MUTED, anchor='end')
    doc.line(300, 462, 392, 462, MUTED, 0.8)
    doc.text(392, 479, [('mono-m', '840')], size=12.5, fill=FG, anchor='end')
    return doc


def _glue_slice(present_sign):
    """Sites of the slice span(e_m, e_a, (e_b + e_c)/sqrt 2): 4 axial, 8 block sites at x_m = +-1."""
    axial = [np.array(v, float) for v in ([0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0])]
    sites = []
    for xm in (1, -1):
        for xa in (1, -1):
            for xb in (1, -1):
                sites.append((np.array([xa / 2, xb / math.sqrt(2), xm / 2]), xm == present_sign))
    return axial, sites


def fig_a_glue():
    doc = Doc(460, 300, 'Two slices through an arrangement glued from two codes',
              'Two globes, each a three-dimensional slice through one block. Grey caps are axial points. '
              'Left: the four caps of a block of code C with first coordinate +1 are present and the four with '
              'first coordinate -1 are empty sites. Right: the reverse, for a block of code C prime.')
    M = view_matrix(34, 7)
    r = math.radians(30) - CAP_GAP
    for k, (cx, sign, col, name) in enumerate(((118, 1, NET_A, 'block {1, 2, 3, 4} of C'),
                                                 (342, -1, NET_B, 'block {1, 2, 3, 5} of C′'))):
        g = Globe(doc, cx, 138, 96, M)
        g.sphere()
        axial, sites = _glue_slice(sign)
        present = [p for p, ok in sites if ok]
        caps = [(p, CORE) for p in axial] + [(p, col) for p in present]
        for p, c in sorted(caps, key=lambda pc: (M @ pc[0])[2]):
            g.cap(p, r, c)
        for p, ok in sites:
            if not ok:
                g.outline(p, r, '#ffffff', 1.2, '4 3.5', opacity=0.85)
        allp = [p for p, _ in caps]
        for i in range(len(allp)):
            for j in range(i + 1, len(allp)):
                if abs(allp[i] @ allp[j] - 0.5) < 1e-9:
                    g.dot(allp[i] + allp[j], math.radians(3.0))
        doc.text(cx, 256, [('sans-m', name)], size=12.5, fill=FG, anchor='middle')
        doc.text(cx, 272, [('sans', 'x₁ = +1 kept' if sign == 1 else 'x₁ = −1 kept')], size=11.5, fill=MUTED,
                 anchor='middle')
    doc.text(230, 293, [('sans', 'grey: axial points ±e₁, ±e₂ · dashed: empty sites')], size=11, fill=MUTED,
             anchor='middle')
    return doc


def fig_a_angles():
    doc = Doc(460, 190, 'Inner products of signed 4-sets and the angles they give',
              'An angle scale from 30 to 185 degrees with a mark for each possible inner product u dot v of two points '
              'of squared length 4. The dashed mark at 41.41 degrees, inner product 3, is an edge of the signed Johnson '
              'graph: the two caps overlap. The bold mark at 60 degrees, inner product 2, is touching.')
    x0, x1, y = 16, 444, 128
    lo, hi = 30, 185
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    doc.rect(X(60), 44, X(185) - X(60), y - 44, fill=BG)
    doc.text(X(160), 100, [('sans', 'allowed: 60° or more')], size=11, fill=MUTED, anchor='middle')
    doc.line(x0, y, x1, y, FG, 1)
    tiers = [0, 1, 0, 1, 0, 1, 0, 1]
    for k, ip in enumerate((3, 2, 1, 0, -1, -2, -3, -4)):
        a = math.degrees(math.acos(ip / 4))
        if ip == 3:
            doc.line(X(a), y, X(a), 70, FG, 1.4, dash='3 3')
        elif ip == 2:
            doc.line(X(a), y, X(a), 70, FG, 2.6)
        else:
            doc.line(X(a), y, X(a), 78, MUTED, 1.2)
        doc.text(X(a), 66 if ip in (3, 2) else 74, [('mono-m', ('+' if ip > 0 else '') + str(ip).replace('-', '−'))],
                 size=11, fill=FG, anchor='middle')
        lab = f'{a:.2f}°'.replace('.00°', '°')
        doc.line(X(a), y, X(a), y + 4 + 13 * tiers[k], RULE, 1)
        doc.text(X(a), y + 16 + 13 * tiers[k], [('mono', lab)], size=10.5, fill=FG if ip in (3, 2) else MUTED,
                 anchor='middle' if ip > -4 else 'end')
    doc.text(x0, 18, [('sans-m', 'u · v'), ('sans', ' for two points of squared length 4, and their angle')], size=12, fill=FG)
    doc.text(x0, 34, [('sans', 'dashed: an edge of J±(n, 4), the caps overlap · bold: touching')], size=11, fill=MUTED)
    return doc


# ==========================================================================
# Plate B: the 841st sphere
# ==========================================================================
def fig_b_hero(seed_signs=None):
    X, labels = data.arrangement_841_start()
    if seed_signs is None:
        rng = np.random.default_rng(1)
        seed_signs = rng.choice([-1, 1], 12)
    x841 = np.asarray(seed_signs, float) / math.sqrt(12)
    over = np.where(X @ x841 > 0.5 + 1e-12)[0]
    doc = Doc(900, 500, 'The 840-point start of the search: two flexible blocks, 720 fixed bridges, one extra point',
              'Every cap is one of the 840 points. Centre: 720 bridge points in 45 tiles of 16, one row per colour '
              'class of K6. Left and right: the two 60-point blocks, each 12 axial points and a 48-system in three '
              'layers. Top: the 841st starting point, with lines to the 47 points it overlaps at the start.')
    pos = {}
    r = 3.9
    pitch = 9.2
    tile = 3 * pitch
    tgap = 17.0
    x_start, y_start = 450 - (9 * tile + 8 * tgap) / 2, 196
    classes = data.gk6()
    sign_order = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    idx = 0
    blocks_seen = {}
    for k, lab in enumerate(labels):
        if lab[0] != 'bridge':
            continue
        c, e, f, s = lab[1]
        key = (c, e, f)
        if key not in blocks_seen:
            col = classes[c].index(e) * 3 + classes[c].index(f)
            blocks_seen[key] = (c, col)
        c, col = blocks_seen[key]
        tx = x_start + col * (tile + tgap)
        ty = y_start + c * (tile + tgap)
        i = sign_order.index((s[0], s[1]))
        j = sign_order.index((s[2], s[3]))
        pos[k] = (tx + j * pitch, ty + i * pitch)
    # blocks
    def block_layout(side, x_c):
        out = {}
        layer = {'upper': [], 'lower': [], 'equator': [], 'axial': []}
        for k, lab in enumerate(labels):
            if lab[0] == side:
                layer[lab[1]].append(k)
        ax = layer['axial']     # order: +e0,-e0,+e1,-e1,...
        top, bot = ax[0], ax[1]
        rest = ax[2:]
        def grid(ks, x0, y0, ncol=4):
            for n, k in enumerate(ks):
                out[k] = (x0 + (n % ncol) * pitch, y0 + (n // ncol) * pitch)
        out[top] = (x_c, 150)
        grid(layer['upper'], x_c - 1.5 * pitch, 176)
        grid(layer['equator'], x_c - 1.5 * pitch, 236)
        grid(rest, x_c - 2 * pitch, 280, ncol=5)
        grid(layer['lower'], x_c - 1.5 * pitch, 316)
        out[bot] = (x_c, 362)
        return out
    pos.update(block_layout('A', 118))
    pos.update(block_layout('B', 782))
    # tile backgrounds
    for (c, e, f), (cc, col) in blocks_seen.items():
        tx = x_start + col * (tile + tgap)
        ty = y_start + cc * (tile + tgap)
        doc.rect(tx - r - 3.5, ty - r - 3.5, tile + 2 * r + 7, tile + 2 * r + 7, fill=BG, rx=4)
    # 841st point
    sx, sy = 450, 104
    for k in over:
        x, y = pos[k]
        doc.line(sx, sy, x, y, NET_C, 0.7, opacity=0.55)
    for k, (x, y) in pos.items():
        side, tag = labels[k][0], labels[k][1]
        if side == 'bridge':
            fill = CORE
        elif tag == 'axial':
            fill = AXIAL
        else:
            fill = NET_A if side == 'A' else NET_B
        doc.circle(x, y, r, fill=fill, stroke=PANEL, width=0.9)
    for k in over:
        x, y = pos[k]
        doc.circle(x, y, r + 1.6, fill='none', stroke=FG, width=1.1)
    doc.circle(sx, sy, 9, fill=NET_C, stroke=PANEL, width=2)
    halo = f'paint-order="stroke" stroke="{PANEL}" stroke-width="4" stroke-linejoin="round"'
    doc.text(sx - 18, sy - 14, [('sans-m', 'the 841st point at the start')], size=13, fill=FG, anchor='end', extra=halo)
    doc.text(sx - 18, sy + 2, [('serif', '(±1, …, ±1)/√12'), ('sans', ' overlaps 47 points:')], size=12, fill=MUTED,
             anchor='end', extra=halo)
    doc.text(sx - 18, sy + 18, [('sans', 'one in every tile and one in each block')], size=12, fill=MUTED, anchor='end',
             extra=halo)
    # labels
    fy = y_start + 5 * (tile + tgap) - tgap + r + 24
    doc.text(450, fy, [('sans-m', '720 bridges, held fixed')], size=13, fill=FG, anchor='middle')
    doc.text(450, fy + 16, [('sans', '45 tiles of 16; one row per colour class of K₆')], size=12, fill=MUTED, anchor='middle')
    for c in range(5):
        ty = y_start + c * (tile + tgap) + tile / 2
        doc.rect(x_start - 20, ty - 10, 5, 20, fill=CLASS_COLOURS[c], rx=1)
    for side, x_c, anchor, dx in (('A', 118, 'end', -34), ('B', 782, 'start', 34)):
        doc.text(x_c, 110, [('sans-m', f'block {side}')], size=13, fill=FG, anchor='middle')
        doc.text(x_c, 126, [('mono', '48 + 12')], size=11.5, fill=MUTED, anchor='middle')
        doc.text(x_c, 404, [('sans', 'first ℝ⁶' if side == 'A' else 'second ℝ⁶')], size=12, fill=MUTED, anchor='middle')
        for yy, t in ((150, 'axis'), (190, 'x₁ = ½'), (250, 'x₁ = 0'), (285, 'axes'), (330, 'x₁ = −½'), (362, 'axis')):
            doc.text(x_c + dx, yy + 4, [('sans', t)], size=11.5, fill=MUTED, anchor=anchor)
    doc.text(450, 486, [('sans', 'Riesz-energy optimisation then moves all 841 points; the best run ends with largest '
                                 'inner product '), ('mono-m', '0.499999937751')], size=12, fill=MUTED, anchor='middle')
    return doc, over, labels


def fig_b_equator():
    doc = Doc(460, 230, 'The equator of a 48-system: angles before and after the skew',
              'Two rows of angle marks. Top: the 16 equator points in the tesseract position, with angles 60, 90, 120 '
              'and 180 degrees. Bottom: the skewed Clebsch position of the paper, with angles 70.53, 83.62, 123.75 and '
              '141.06 degrees. Dotted curves join corresponding pairs; the numbers are pairs per equator point.')
    x0, x1 = 16, 444
    lo, hi = 50, 185
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    y1, y2 = 76, 158
    classical = [(0.5, 4), (0.0, 6), (-0.5, 4), (-1.0, 1)]
    skewed = [(1 / 3, 4), (1 / 9, 6), (-5 / 9, 4), (-7 / 9, 1)]
    doc.text(x0, 18, [('sans-m', 'tesseract position'), ('mono', '  q₅ = 0')], size=12, fill=FG)
    doc.text(x1, 18, [('sans-m', 'skewed Clebsch'), ('mono', '  q₅ = 1/9')], size=12, fill=NET_A, anchor='end')
    doc.line(x0, y1, x1, y1, FG, 1)
    doc.line(x0, y2, x1, y2, FG, 1)
    for (a, n), (b, m) in zip(classical, skewed):
        A, B = math.degrees(math.acos(a)), math.degrees(math.acos(b))
        doc.path(f'M{fmt(X(A))} {y1} C{fmt(X(A))} {(y1 + y2) / 2 - 6} {fmt(X(B))} {(y1 + y2) / 2 + 6} {fmt(X(B))} {y2 - 18}',
                 stroke=MUTED, width=1, dash='2 3')
        doc.line(X(A), y1, X(A), y1 - 18, FG, 2.4 if a == 0.5 else 1.3)
        doc.line(X(B), y2, X(B), y2 - 18, NET_A, 2.2)
        anchor = 'end' if A > 170 else 'middle'
        dx = 2 if anchor == 'end' else 0
        doc.text(X(A) + dx, y1 - 38, [('mono', f'{A:.0f}°')], size=10.5, fill=FG, anchor=anchor)
        doc.text(X(A) + dx, y1 - 25, [('sans', f'×{n}')], size=10.5, fill=MUTED, anchor=anchor)
        doc.text(X(B), y2 + 15, [('mono', f'{B:.2f}°')], size=10.5, fill=NET_A, anchor='middle')
        doc.text(X(B), y2 + 28, [('sans', f'×{m}')], size=10.5, fill=MUTED, anchor='middle')
    doc.text(x0, 220, [('sans', 'per equator point: the 4 contacts at 60° open to 70.53°')], size=11.5, fill=MUTED)
    return doc


def fig_b_turn():
    doc = Doc(460, 220, 'Largest inner product as one 48-system turns',
              'A curve of the largest inner product among the 840 points against the turning angle theta of one '
              '48-system in a coordinate plane. It stays exactly one half for theta between minus and plus 3.59 '
              'degrees and grows outside that interval.')
    lim = data.rotation_limit_deg()
    x0, x1, yb, yt = 46, 440, 172, 40
    tlo, thi = -8, 8
    vlo, vhi = 0.495, 0.535
    X = lambda t: x0 + (t - tlo) / (thi - tlo) * (x1 - x0)
    Y = lambda v: yb - (v - vlo) / (vhi - vlo) * (yb - yt)
    doc.rect(X(-lim), yt, X(lim) - X(-lim), yb - yt, fill=BG)
    doc.line(x0, Y(0.5), x1, Y(0.5), MUTED, 1, dash='3 3')
    doc.text(x0 - 6, Y(0.5) + 4, [('mono', '½')], size=11, fill=MUTED, anchor='end')
    doc.text(x0 - 6, Y(0.53) + 4, [('mono', '0.53')], size=10.5, fill=MUTED, anchor='end')
    doc.line(x0, yb, x1, yb, FG, 1)
    for t in (-8, -4, 0, 4, 8):
        doc.line(X(t), yb, X(t), yb + 4, FG, 1)
        doc.text(X(t), yb + 17, [('mono', f'{t:+d}°'.replace('+0°', '0°').replace('-', '−'))], size=10.5, fill=MUTED, anchor='middle')
    ts = np.linspace(tlo, thi, 161)
    vals = []
    for t in ts:
        th = math.radians(t)
        A = np.eye(4)
        A[0, 0] = A[1, 1] = math.cos(th)
        A[0, 1], A[1, 0] = -math.sin(th), math.sin(th)
        Xr, _ = data.arrangement_841_start(A_left=A)
        G = Xr @ Xr.T
        np.fill_diagonal(G, -2)
        vals.append(float(G.max()))
    for t, v in zip(ts, vals):        # the formula of the bound, checked against the computed values
        th = math.radians(abs(t))
        assert abs(v - max(0.5, math.sqrt(2) / 3 * (math.cos(th) + math.sin(th)))) < 1e-9, (t, v)
    doc.polyline([(X(t), Y(v)) for t, v in zip(ts, vals)], stroke=NET_A, width=2.2)
    for s in (-1, 1):
        doc.line(X(s * lim), yt, X(s * lim), yb, FG, 1)
        doc.text(X(s * lim) + (5 if s > 0 else -5), yt + 12, [('mono-m', f'{s * lim:+.2f}°'.replace('-', '−'))],
                 size=11, fill=FG, anchor='start' if s > 0 else 'end')
    doc.text(X(0), Y(0.5) - 10, [('sans', 'still a kissing arrangement')], size=11.5, fill=FG, anchor='middle')
    doc.text(x0 - 30, 18, [('sans-m', 'largest inner product'), ('sans', ' of the 840 points')], size=12, fill=FG)
    doc.text(x0, 210, [('sans', 'turning angle θ in one coordinate plane; the other block stays fixed')], size=11.5, fill=MUTED)
    return doc


# ==========================================================================
# Plate C: the quaternionic model
# ==========================================================================
C_COLOURS = {'E1': CORE, 'E2': AXIAL, 'E3': NET_C, 'M1': NET_A, 'M2': NET_B}
C_NAMES = {'E1': 'E₁', 'E2': 'E₂', 'E3': 'E₃', 'M1': 'M₁', 'M2': 'M₂'}


def sunflower(n, spacing):
    """n points on a Vogel spiral: a round patch of nearly even density."""
    golden = math.pi * (3 - math.sqrt(5))
    return [(spacing * math.sqrt(k + 0.5) * math.cos(k * golden), spacing * math.sqrt(k + 0.5) * math.sin(k * golden))
            for k in range(n)]


def dome(doc, cx, cy, n, colour, r=2.6, spacing=2.92):
    """A patch of n caps, shaded like a small dome so it reads as a cluster of caps."""
    from capdraw import shade
    pts = sunflower(n, spacing)
    rad = max(math.hypot(x, y) for x, y in pts) + r
    for x, y in sorted(pts, key=lambda p: (p[0] ** 2 + p[1] ** 2)):
        nx, ny = x / (rad * 1.08), -y / (rad * 1.08)
        nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        doc.circle(cx + x, cy + y, r, fill=shade(colour, np.array([nx, ny, nz])), stroke=SEAM, width=0.55)
    return rad


def fig_c_hero():
    X, lab = data.quaternionic_model()
    prof = np.stack([(X[:, 4 * k:4 * k + 4] ** 2).sum(1) for k in range(3)], 1)
    doc = Doc(900, 500, 'Norm profiles of the quaternionic 840-point model',
              'A triangle whose corners stand for the three quaternionic factors. Each of the 840 points is placed at '
              'the share of its squared length in each factor: the three axial 24-cells at the corners, the 384 points '
              'of M1 at one half, one quarter, one quarter and the 384 of M2 at one quarter, one half, one quarter. '
              'Bars at right give the squared length carried by each factor in total.')
    V = [np.array([108.0, 440.0]), np.array([578.0, 440.0])]
    V.append(np.array([(V[0][0] + V[1][0]) / 2, V[0][1] - (V[1][0] - V[0][0]) * math.sqrt(3) / 2]))
    P = lambda w: w[0] * V[0] + w[1] * V[1] + w[2] * V[2]
    doc.path('M' + ' L'.join(f'{fmt(v[0])} {fmt(v[1])}' for v in V) + 'Z', fill=BG, stroke=RULE, width=1.2)
    for t in (0.25, 0.5, 0.75):
        for k in range(3):
            a = [0.0, 0.0, 0.0]
            b = [0.0, 0.0, 0.0]
            a[k] = b[k] = t
            a[(k + 1) % 3] = 1 - t
            b[(k + 2) % 3] = 1 - t
            pa, pb = P(a), P(b)
            doc.line(pa[0], pa[1], pb[0], pb[1], RULE, 0.8, dash='2 4')
    groups = {}
    for name in ('E1', 'E2', 'E3', 'M1', 'M2'):
        w = prof[lab == name]
        assert np.allclose(w, w[0])
        groups[name] = (w[0], int((lab == name).sum()))
    rads = {name: dome(doc, *P(w), n, C_COLOURS[name]) for name, (w, n) in groups.items()}
    frac = {1.0: '1', 0.5: '½', 0.25: '¼', 0.0: '0'}
    def label(name, x, y, anchor, extra=None):
        w, n = groups[name]
        wtxt = '(' + ', '.join(frac[round(float(v), 2)] for v in w) + ')'
        doc.text(x, y, [('sans-m', C_NAMES[name] + '  '), ('mono', str(n))], size=13, fill=FG, anchor=anchor)
        doc.text(x, y + 16, [('serif', wtxt)], size=12.5, fill=MUTED, anchor=anchor)
        if extra:
            doc.text(x, y + 32, [('sans', extra)], size=12, fill=MUTED, anchor=anchor)
    pM1, pM2 = P(groups['M1'][0]), P(groups['M2'][0])
    label('M1', pM1[0] - rads['M1'] - 10, pM1[1] - 6, 'end')
    label('M2', pM2[0] + rads['M2'] + 10, pM2[1] - 6, 'start')
    label('E1', V[0][0] - 6, V[0][1] + 38, 'start')
    label('E2', V[1][0] + 6, V[1][1] + 38, 'end')
    p3 = P(groups['E3'][0])
    doc.circle(p3[0], p3[1], rads['E3'] + 7, fill='none', stroke=FG, width=1.1, dash='4 3')
    label('E3', p3[0] + rads['E3'] + 16, p3[1] - 6, 'start', 'touches only 24 points;')
    doc.text(p3[0] + rads['E3'] + 16, p3[1] + 42, [('sans', 'it moves in the 841-point arrangement')], size=12, fill=MUTED)
    doc.text(V[0][0] - rads['E1'] - 8, V[0][1] + 6, [('serif', 'ℍ₁')], size=18, fill=FG, anchor='end')
    doc.text(V[1][0] + rads['E2'] + 8, V[1][1] + 6, [('serif', 'ℍ₂')], size=18, fill=FG, anchor='start')
    doc.text(p3[0] - rads['E3'] - 12, p3[1] + 5, [('serif', 'ℍ₃')], size=18, fill=FG, anchor='end')
    # squared length per factor
    mass = [float(prof[:, k].sum()) for k in range(3)]
    x0, y0 = 668, 120
    doc.text(x0, y0 - 44, [('sans-sb', 'Squared length per factor')], size=13.5, fill=FG)
    doc.text(x0, y0 - 27, [('sans', 'summed over the 840 points')], size=11.5, fill=MUTED)
    bar0, unit = x0 + 34, 0.5
    for k, m in enumerate(mass):
        yy = y0 + k * 44
        doc.text(x0, yy + 6, [('serif', f'ℍ{"₁₂₃"[k]}')], size=16, fill=FG)
        doc.rect(bar0, yy - 10, m * unit, 20, fill=NET_C if k == 2 else CORE, rx=2)
        doc.text(bar0 + m * unit + 8, yy + 5, [('mono-m', f'{m:.0f}')], size=12.5, fill=FG)
    mean = 280 * unit + bar0
    doc.line(mean, y0 - 16, mean, y0 + 2 * 44 + 16, FG, 1, dash='3 3')
    doc.text(mean, y0 + 2 * 44 + 30, [('mono', '280 = 840/3')], size=11, fill=MUTED, anchor='middle')
    doc.text(x0, y0 + 158, [('sans', 'frame operator')], size=12, fill=MUTED)
    doc.text(x0, y0 + 176, [('mono', '78 I₄ ⊕ 78 I₄ ⊕ 54 I₄')], size=12.5, fill=FG)
    doc.text(x0, y0 + 214, [('sans', 'both mixed families put ¼ of')], size=12, fill=MUTED)
    doc.text(x0, y0 + 230, [('sans', 'their squared length in ℍ₃;')], size=12, fill=MUTED)
    doc.text(x0, y0 + 246, [('sans', 'ℍ₃ is where room is left')], size=12, fill=MUTED)
    return doc


def fig_c_contacts():
    X, lab = data.quaternionic_model()
    G = X @ X.T
    C = np.abs(G - 0.5) < 1e-9
    parts = ['E1', 'E2', 'E3', 'M1', 'M2']
    table = {}
    for a in parts:
        rows = C[np.ix_(lab == a, lab == a)]
        per = {b: C[np.ix_(lab == a, lab == b)].sum(1) for b in parts}
        for b in parts:
            assert len(set(per[b].tolist())) == 1, (a, b)
        table[a] = {b: int(per[b][0]) for b in parts}
    doc = Doc(460, 236, 'Contacts per point in the quaternionic model, by the part touched',
              'Five stacked bars, one per part. E1 and E2 points each touch 120 others, mostly in the mixed families; '
              'E3 points touch only 24: eight in E3 and sixteen in M1; M1 and M2 points touch 78 and 77.')
    x0, x1 = 54, 430
    scale = (x1 - x0) / 120
    y = 34
    doc.text(16, 18, [('sans', 'each bar is split by the part on the other side of the contact')], size=11.5, fill=MUTED)
    for a in ['E1', 'E2', 'M1', 'M2', 'E3']:
        doc.text(16, y + 5, [('sans-m', C_NAMES[a])], size=13, fill=FG)
        xx = x0
        for b in parts:
            v = table[a][b]
            if v == 0:
                continue
            w = v * scale
            doc.rect(xx, y - 9, w - 1, 18, fill=C_COLOURS[b], rx=1.5)
            if w > 22:
                doc.text(xx + w / 2, y + 4, [('mono', str(v))], size=10.5, fill=FG if b != 'E2' else '#ffffff', anchor='middle')
            xx += w
        doc.text(xx + 6, y + 4, [('mono-m', str(sum(table[a].values())))], size=11.5, fill=FG)
        y += 34
    lx = 54
    for b in parts:
        doc.circle(lx + 5, 212, 5, fill=C_COLOURS[b], stroke=PANEL, width=1)
        doc.text(lx + 14, 216, [('sans', C_NAMES[b])], size=11.5, fill=MUTED)
        lx += 62
    return doc, table


def fig_c_fingerprint():
    X, lab = data.quaternionic_model()
    G = X @ X.T
    iu = np.triu_indices(len(X), 1)
    vals = sorted(set(np.round(G[iu], 9).tolist()))
    quat = [math.degrees(math.acos(v)) for v in vals if v > -0.999]
    johnson = [math.degrees(math.acos(v)) for v in (0.5, 0.25, 0.0, -0.25, -0.5, -0.75)]
    doc = Doc(460, 200, 'Angles that occur in the quaternionic model and in the Johnson-graph arrangements',
              'Two rows of marks between 55 and 145 degrees. Top: the six angles available to all 1579 signed '
              'Johnson graph arrangements. Bottom: the eleven angles of the quaternionic model; six of them have '
              'irrational cosines and occur in no Johnson-graph arrangement.')
    x0, x1 = 16, 444
    lo, hi = 55, 145
    Xf = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    y1, y2 = 56, 132
    doc.line(x0, y1, x1, y1, FG, 1)
    doc.line(x0, y2, x1, y2, FG, 1)
    doc.text(x0, y1 - 30, [('sans-m', 'all 1579 signed Johnson arrangements')], size=12, fill=FG)
    doc.text(x0, y2 - 30, [('sans-m', 'quaternionic model')], size=12, fill=FG)
    for a in johnson:
        if a <= hi:
            doc.line(Xf(a), y1, Xf(a), y1 - 14, FG, 1.6)
    new = []
    for a in quat:
        shared = any(abs(a - b) < 1e-6 for b in johnson)
        if a <= hi:
            doc.line(Xf(a), y2, Xf(a), y2 - 14, FG if shared else NET_A, 1.6 if shared else 2.4)
        if not shared:
            new.append(a)
    tiers = [0, 1, 0, 1, 0, 1]
    for k, a in enumerate(new):
        doc.text(Xf(a), y2 + 16 + 13 * tiers[k], [('mono', f'{a:.2f}°')], size=10.5, fill=NET_A, anchor='middle')
    for v in (60, 90, 120):
        doc.text(Xf(v), y1 + 15, [('mono', f'{v}°')], size=10.5, fill=MUTED, anchor='middle')
    doc.text(x0, 190, [('sans', 'orange: cosines ±(2 ± √2)/8 and ±√2/4, in no Johnson arrangement')], size=11.5, fill=MUTED)
    return doc, new
