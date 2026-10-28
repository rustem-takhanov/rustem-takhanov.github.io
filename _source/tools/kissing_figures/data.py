"""Exact constructions behind the kissing-number figure plates.

Every configuration drawn in the plates is rebuilt here from the definitions
in the papers and checked (unit norms, largest inner product 1/2, counts).
"""
from __future__ import annotations

import itertools as it
import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np

TOL = 1e-9


def gram_report(X):
    G = X @ X.T
    n = len(X)
    iu = np.triu_indices(n, 1)
    vals = G[iu]
    return {
        'n': n,
        'norm_err': float(np.abs(np.diag(G) - 1).max()),
        'max_ip': float(vals.max()),
        'contacts': int((np.abs(vals - 0.5) < TOL).sum()),
        'gram': G,
    }


def check_kissing(X, name, n_expected=None):
    r = gram_report(X)
    assert r['norm_err'] < 1e-9, (name, r['norm_err'])
    assert r['max_ip'] <= 0.5 + 1e-9, (name, r['max_ip'])
    if n_expected is not None:
        assert r['n'] == n_expected, (name, r['n'])
        distinct = len({tuple(np.round(x, 9)) for x in X})
        assert distinct == n_expected, (name, distinct)
    return r


# ==========================================================================
# K6, its 1-factorisation and Construction 1 (n = 12)
# ==========================================================================
def gk6():
    """The 1-factorisation GK6 of K6: vertex 5 is the hub, vertices 0..4 a pentagon.
    Colour c contains the spoke {c, 5} and the chords {c+1, c-1}, {c+2, c-2} (mod 5)."""
    classes = []
    for c in range(5):
        classes.append([tuple(sorted((c, 5))),
                        tuple(sorted(((c + 1) % 5, (c - 1) % 5))),
                        tuple(sorted(((c + 2) % 5, (c - 2) % 5)))])
    edges = [e for cls in classes for e in cls]
    assert len(set(edges)) == 15
    return classes


def bridge_blocks(classes):
    """45 blocks {x, y, z', t'}: an edge in each copy of [6], of the same colour."""
    out = []
    for c, cls in enumerate(classes):
        for e in cls:
            for f in cls:
                out.append((c, e, f))
    assert len(out) == 45
    return out


def signed_block(support, signs, scale=0.5):
    v = np.zeros(12)
    for i, s in zip(support, signs):
        v[i] = s * scale
    return v


def axial(offset):
    pts = []
    for i in range(6):
        for s in (1, -1):
            v = np.zeros(12)
            v[offset + i] = s
            pts.append(v)
    return np.array(pts)


def construction1(free_left, free_right):
    """free_*: list of (block, allowed sign predicate) for the free zones (blocks inside [6])."""
    classes = gk6()
    pts, lab = [], []
    for off, tag in ((0, 'axialL'), (6, 'axialR')):
        for v in axial(off):
            pts.append(v)
            lab.append(tag)
    for off, zone, tag in ((0, free_left, 'freeL'), (6, free_right, 'freeR')):
        for block, ok in zone:
            for signs in it.product((1, -1), repeat=4):
                if ok(block, signs):
                    pts.append(signed_block([off + i for i in block], signs))
                    lab.append(tag)
    for c, e, f in bridge_blocks(classes):
        for signs in it.product((1, -1), repeat=4):
            pts.append(signed_block([e[0], e[1], 6 + f[0], 6 + f[1]], signs))
            lab.append('bridge%d' % c)
    return np.array(pts), np.array(lab)


def matching_code(matching):
    """Blocks = complements of a perfect matching of [6] (an optimal (6,4,4) code)."""
    return [tuple(sorted(set(range(6)) - set(e))) for e in matching]


def classical_zone(matching):
    return [(b, lambda b, s: True) for b in matching_code(matching)]


def glued_zone(M, Mp, m):
    """Lemma 3 gluing: code C from matching M on x_m = +1, code C' from M' on x_m = -1.
    M and M' must share the edge through m (so C, C' agree on blocks avoiding m)."""
    C, Cp = matching_code(M), matching_code(Mp)
    common = [b for b in C if m not in b]
    assert common == [b for b in Cp if m not in b]
    zone = [(b, lambda b, s: True) for b in common]
    for b in C:
        if m in b:
            zone.append((b, lambda b, s, m=m: s[b.index(m)] == 1))
    for b in Cp:
        if m in b:
            zone.append((b, lambda b, s, m=m: s[b.index(m)] == -1))
    return zone, C, Cp


# ==========================================================================
# The 48-system of the 841 paper (Example 1, skewed Clebsch)
# ==========================================================================
EVEN5 = [np.array(e, float) for e in it.product((1, -1), repeat=5) if np.prod(e) == 1]
assert len(EVEN5) == 16


def clebsch_neighbours(i):
    return [j for j in range(16) if int(np.sum(EVEN5[i] != EVEN5[j])) == 4]


def system48(q):
    """Equator x_eps = (sqrt(q_k) eps_k) and floor vectors b_i = 1/2 X_i Gamma_i^{-1} 1."""
    X = np.array([np.sqrt(q) * e for e in EVEN5])
    B = []
    for i in range(16):
        Xi = X[clebsch_neighbours(i)].T
        Gi = Xi.T @ Xi
        B.append(0.5 * Xi @ np.linalg.solve(Gi, np.ones(5)))
    return X, np.array(B)


Q_EXAMPLE1 = np.array([2 / 9, 2 / 9, 2 / 9, 2 / 9, 1 / 9])
Q_CLASSICAL = np.array([1 / 4, 1 / 4, 1 / 4, 1 / 4, 0.0])


def block60(offset, A=None):
    """12 axial vectors and the Example-1 48-system, optionally turned by diag(1, A, 1)."""
    X, Bf = system48(Q_EXAMPLE1)
    if A is not None:
        Q = np.eye(5)
        Q[:4, :4] = A
        X, Bf = X @ Q.T, Bf @ Q.T
    pts, lab = [], []
    for v in axial(offset):
        pts.append(v)
        lab.append('axial')
    for x in X:
        v = np.zeros(12)
        v[offset + 1:offset + 6] = x
        pts.append(v)
        lab.append('equator')
    for h, tag in ((0.5, 'upper'), (-0.5, 'lower')):
        for b in Bf:
            v = np.zeros(12)
            v[offset] = h
            v[offset + 1:offset + 6] = b
            pts.append(v)
            lab.append(tag)
    return np.array(pts), lab


def bridges_only():
    pts, lab = [], []
    for c, e, f in bridge_blocks(gk6()):
        for signs in it.product((1, -1), repeat=4):
            pts.append(signed_block([e[0], e[1], 6 + f[0], 6 + f[1]], signs))
            lab.append((c, e, f, signs))
    return np.array(pts), lab


def arrangement_841_start(A_left=None, A_right=None):
    XA, la = block60(0, A_left)
    XB, lb = block60(6, A_right)
    XBr, lbr = bridges_only()
    X = np.vstack([XA, XB, XBr])
    labels = [('A', t) for t in la] + [('B', t) for t in lb] + [('bridge', t) for t in lbr]
    return X, labels


def rotation_limit_deg():
    """Largest angle a 48-system may turn in one coordinate plane (Theorem 2 bound)."""
    return math.degrees(math.asin(0.75)) - 45.0


# ==========================================================================
# The quaternionic 840-point model
# ==========================================================================
def qmul(p, q):
    a1, b1, c1, d1 = p
    a2, b2, c2, d2 = q
    return np.array([a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2,
                     a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
                     a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2,
                     a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2])


def quaternionic_model():
    one, I, J, K = (np.eye(4)[k] for k in range(4))
    omega = np.full(4, 0.5)
    tau = np.array([1, 1, 0, 0]) / math.sqrt(2)
    Q8 = [s * u for u in (one, I, J, K) for s in (1, -1)]
    C = Q8 + [np.array(e) / 2 for e in it.product((1, -1), repeat=4)]
    rep = {(0, 0): one, (1, 0): I, (0, 1): J, (1, 1): K}

    def bhat(eta):
        out = []
        for u in rep:
            for v in rep:
                w = ((u[0] + v[0] + eta[0]) % 2, (u[1] + v[1] + eta[1]) % 2)
                for s in it.product((1, -1), repeat=3):
                    out.append((s[0] * rep[u], s[1] * rep[v], s[2] * rep[w]))
        return out
    w = [np.array([1., 0, 0, 0]), omega, qmul(omega, omega)]
    deltas = [(0, 1), (1, 0), (1, 1)]      # j, i, k
    pts, lab = [], []
    for k in range(3):
        for c in C:
            v = np.zeros(12)
            v[4 * k:4 * k + 4] = c
            pts.append(v)
            lab.append('E%d' % (k + 1))
    for r in range(3):
        g = (qmul(tau, w[r]), w[r], w[r])
        for a, b, c in bhat((0, 0)):
            pts.append(np.concatenate([qmul(g[0], a) / math.sqrt(2), qmul(g[1], b) / 2, qmul(g[2], c) / 2]))
            lab.append('M1')
    for r in range(3):
        g = (w[r], qmul(tau, w[r]), qmul(tau, w[r]))
        for a, b, c in bhat(deltas[r]):
            pts.append(np.concatenate([qmul(g[0], a) / 2, qmul(g[1], b) / math.sqrt(2), qmul(g[2], c) / 2]))
            lab.append('M2')
    return np.array(pts), np.array(lab)


QUATERNIONIC_TABLE = {  # inner product -> number of pairs, as reported in the paper
    -1.0: 420, -0.5: 32928, 0.5: 32928,
    -(2 + math.sqrt(2)) / 8: 18432, (2 + math.sqrt(2)) / 8: 18432,
    -math.sqrt(2) / 4: 2304, math.sqrt(2) / 4: 2304,
    -0.25: 43008, 0.25: 43008,
    -(2 - math.sqrt(2)) / 8: 18432, (2 - math.sqrt(2)) / 8: 18432,
    0.0: 121752,
}


# ==========================================================================
# Dimensions 25-31: the certified data (optional recomputation)
# ==========================================================================
CERT_DIR = Path(os.environ['KISSING_CERT_DIR']).expanduser() if os.environ.get('KISSING_CERT_DIR') else None

# Smallest angles (degrees) before (Kravatskiy, R = I) and after (certified rotations).
SLACK = {
    'thresholds': {'aux_tail': 30.0, 'tail_frame': math.degrees(math.acos(math.sqrt(1.5) - 0.5)),
                   'aux_frame': 45.0, 'aux_aux': 60.0},
    'before': {'aux_tail': 31.3997, 'tail_frame': 45.0, 'aux_frame': 45.0, 'aux_aux': 60.0},
    'd29': {'aux_tail': 30.0563, 'tail_frame': 43.5933, 'aux_frame': 45.0399, 'aux_aux': 60.0326},
    'd31': {'aux_tail': 30.0490, 'tail_frame': 43.5879, 'aux_frame': 45.0346, 'aux_aux': 60.0000},
}


def recompute_slack():
    """Recompute SLACK from the certificate package, if it is available locally."""
    if CERT_DIR is None:
        return None
    if not CERT_DIR.is_dir():
        raise FileNotFoundError(f'KISSING_CERT_DIR is not a directory: {CERT_DIR}')
    from fractions import Fraction
    s2, s3, s6 = math.sqrt(2), math.sqrt(3), math.sqrt(6)

    def alg(q, den):
        return (q[0] + q[1] * s2 + q[2] * s3 + q[3] * s6) / den
    deg = lambda x: math.degrees(math.acos(max(-1.0, min(1.0, x))))

    def stats(T, A, W, R):
        RT = T @ R.T
        G = A @ A.T
        np.fill_diagonal(G, -2)
        return {'aux_aux': deg(G.max()), 'aux_tail': deg((A @ RT.T).max()),
                'aux_frame': deg(np.abs(A @ W.T).max()), 'tail_frame': deg(np.abs(RT @ W.T).max())}
    out = {}
    g = json.loads((CERT_DIR / 'd29/data/geom29.json').read_text(encoding='utf-8'))
    c = json.loads((CERT_DIR / 'd29/axis34_rotated_caps.json').read_text(encoding='utf-8'))
    den = g['denominator']
    T = np.array([[alg(q, den) for q in v] for v in g['directions']])
    A0 = np.array([[alg(q, den) for q in v] for v in g['axis']])
    W = np.array([[alg(q, den) for q in v] for v in g['frame']])
    R = np.array([[float(Fraction(x)) for x in row] for row in c['R']])
    A = np.array([[float(Fraction(x)) for x in row] for row in c['axis']])
    out['before29'] = stats(T, A0, W, np.eye(5))
    out['d29'] = stats(T, A, W, R)
    out['n29'] = (len(A0), len(A))
    g = json.loads((CERT_DIR / 'd31/data/geom31.json').read_text(encoding='utf-8'))
    c = json.loads((CERT_DIR / 'd31/axis122_d31.json').read_text(encoding='utf-8'))
    den = g['denominator']
    T = np.array([[alg(q, den) for q in v] for v in g['directions']])
    A0 = np.array([[alg(q, den) for q in v] for v in g['axis']])
    W = np.array([[alg(q, den) for q in v] for v in g['frame']])
    D = float(c['D'])
    I7 = np.eye(7)
    Q = (I7 - np.array(c['K_Q'], float) / D) @ np.linalg.inv(I7 + np.array(c['K_Q'], float) / D)
    R = (I7 - np.array(c['K_R'], float) / D) @ np.linalg.inv(I7 + np.array(c['K_R'], float) / D)
    out['before31'] = stats(T, A0, W, np.eye(7))
    out['d31'] = stats(T, T[c['kept']] @ Q.T, W, R)
    out['n31'] = (len(A0), len(c['kept']))
    return out


HEIGHTS = {  # angle (degrees) out of R^24 of each block type, from the definitions
    'bulk': 0.0,
    'moved_bulk_d25': math.degrees(math.asin((math.sqrt(6) - 2) / 8)),
    'caps_30': 30.0,
    'lifted': math.degrees(math.asin(1 / math.sqrt(3))),
    'frame': 45.0,
    'auxiliary': 90.0,
}


def lifting_slice():
    """Exact 3-D slice of Lemma II.1 with k = 2: owner pair +-u (model z axis),
    a zero-sum triangle of tail directions at 30, 150, 270 degrees and the
    auxiliary hexagon at 0, 60, ..., 300 degrees in the tail plane."""
    a = math.sqrt(1 / 3)
    lifted = []
    for lon in (30, 150, 270):
        L = math.radians(lon)
        for s in (1, -1):
            lifted.append(np.array([a * math.cos(L), a * math.sin(L), s * math.sqrt(2 / 3)]))
    hexagon = [np.array([math.cos(math.radians(l)), math.sin(math.radians(l)), 0.0]) for l in range(0, 360, 60)]
    owners = [np.array([0, 0, 1.0]), np.array([0, 0, -1.0])]
    P = np.array(lifted + hexagon)
    G = P @ P.T
    np.fill_diagonal(G, -2)
    assert G.max() <= 0.5 + 1e-12
    contacts = [(i, j) for i in range(12) for j in range(i + 1, 12) if abs(G[i, j] - 0.5) < 1e-12]
    assert len(contacts) == 24
    for o in owners:   # each owner overlaps its three lifted points
        assert sum((P @ o) > 0.5 + 1e-9) == 3
    return lifted, hexagon, owners, contacts


def summary():
    out = {}
    # Construction 1, classical free zones from the matching of colour 0
    classes = gk6()
    X, lab = construction1(classical_zone(classes[0]), classical_zone(classes[0]))
    r = check_kissing(X, 'construction1-classical', 840)
    out['c1_classical_contacts'] = r['contacts']
    # glued free zone (Lemma 3) on the left half
    M = [(0, 1), (2, 3), (4, 5)]
    Mp = [(0, 1), (2, 4), (3, 5)]
    zone, C, Cp = glued_zone(M, Mp, m=0)
    X, lab = construction1(zone, classical_zone(classes[0]))
    r = check_kissing(X, 'construction1-glued', 840)
    # Theorem 1: every orthant copy of J(12, 4) meets the independent set in exactly 51 vertices
    V = 2 * X[[l not in ('axialL', 'axialR') for l in lab]]
    rng = np.random.default_rng(0)
    for _ in range(2048):
        s = rng.choice([-1, 1], 12)
        assert int(np.all((V == 0) | (V == s), axis=1).sum()) == 51
    G = X @ X.T
    iu = np.triu_indices(840, 1)
    out['c1_glued_ips'] = sorted(Counter(np.round(G[iu], 9)).items())
    # Example-1 start of the 841 search
    X, lab = arrangement_841_start()
    r = check_kissing(X, 'example1-840', 840)
    out['ex1_contacts'] = r['contacts']
    # quaternionic model
    X, lab = quaternionic_model()
    r = check_kissing(X, 'quaternionic', 840)
    G = r['gram']
    iu = np.triu_indices(840, 1)
    got = Counter(np.round(G[iu], 9))
    for k, v in QUATERNIONIC_TABLE.items():
        assert got[round(k, 9) + 0.0] == v, (k, got[round(k, 9)], v)
    lifting_slice()
    return out


if __name__ == '__main__':
    s = summary()
    for k, v in s.items():
        print(k, v)
    print('rotation limit', rotation_limit_deg())
    print('heights', HEIGHTS)
    print('slack recomputed', recompute_slack())
