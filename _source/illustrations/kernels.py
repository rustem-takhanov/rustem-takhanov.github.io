"""Original vector illustrations for the five kernel-method papers.

These are explanatory mathematical examples and schematics, not reproduced
experimental results. Each source URL identifies the paper motivating the image.
"""
import math

from .common import Canvas, figure, INK, TEAL, GOLD, BLUE, MUTED, LINE, PALE, PAPER, WHITE, fmt


def _axes(c, x, y, w, h):
    c.line(x, y-h, x, y, LINE, 1.5)
    c.line(x, y, x+w, y, LINE, 1.5)


def _mercer():
    c = Canvas('Successive Mercer approximations to the Brownian kernel', 'Spectral approximation')
    c.text(500, 86, 'A kernel, reconstructed one mode at a time', 27, INK, 'middle', family='Georgia, serif')
    cut = .62
    for j, n in enumerate([1, 4, 16]):
        x0, y0, w, h = 67+j*317, 320, 232, 170
        _axes(c, x0, y0, w, h)
        exact = [(x0+w*i/160, y0-h*min(i/160, cut)) for i in range(161)]
        approx = []
        for i in range(161):
            x = i/160
            value = sum(2*math.sin((k-.5)*math.pi*x)*math.sin((k-.5)*math.pi*cut)/((k-.5)*math.pi)**2 for k in range(1, n+1))
            approx.append((x0+w*x, y0-h*value))
        c.polyline(exact, MUTED, 3, dash='7 7', opacity=.65)
        c.polyline(approx, [GOLD, BLUE, TEAL][j], 4)
        c.circle(x0+w*cut, y0-h*cut, 4, MUTED)
        c.text(x0+w/2, 364, f'{n} '+('mode' if n == 1 else 'modes'), 24, [GOLD, BLUE, TEAL][j], 'middle', 600)
    c.rect(172, 400, 656, 46, WHITE, radius=6)
    c.text(500, 431, 'K(x, y) = min(x, y)     ·     fixed y = 0.62', 22, INK, 'middle')
    return figure(c,
        'Three plots compare one, four, and sixteen Mercer modes with a dashed exact slice of the Brownian kernel min(x,y).',
        'An exact toy example: successive Mercer truncations approach a slice of the Brownian kernel K(x, y) = min(x, y). Dashed curves show the exact slice. The paper studies how smoothness and spectral decay control uniform approximation error.',
        'https://arxiv.org/abs/2205.00487', 'Original mathematical illustration')


def _random_features():
    c = Canvas('Frozen random hidden layers and a trained final readout', 'Random features')
    c.rect(228, 111, 422, 259, PALE, radius=18)
    c.text(440, 88, 'Fixed random representation', 25, TEAL, 'middle')
    c.text(835, 88, 'Learned readout', 25, GOLD, 'middle')
    xs = [99, 310, 550, 839]
    ys = [[188, 240, 292], [145, 191, 237, 283, 329], [145, 191, 237, 283, 329], [237]]
    for layer in range(3):
        for i, ya in enumerate(ys[layer]):
            for j, yb in enumerate(ys[layer+1]):
                color = GOLD if layer == 2 else BLUE
                opacity = .52 if layer == 2 else .14+.08*((i+j)%3)
                c.line(xs[layer]+14, ya, xs[layer+1]-17, yb, color, 2.4 if layer==2 else 1.7, opacity=opacity)
    for layer in range(4):
        for y in ys[layer]:
            c.circle(xs[layer], y, 15 if layer<3 else 24, GOLD if layer==3 else (TEAL if layer else MUTED), WHITE, 3)
    c.arrow(868, 237, 945, 237, GOLD, 3)
    c.text(953, 245, 'f̂', 29, GOLD)
    c.text(99, 358, 'x', 31, INK, 'middle', family='Georgia, serif')
    c.text(310, 410, 'φ₁(x)', 28, TEAL, 'middle', family='Georgia, serif')
    c.text(550, 410, 'φ₂(x)', 28, TEAL, 'middle', family='Georgia, serif')
    c.text(839, 410, 'w · φ₂(x)', 28, GOLD, 'middle', family='Georgia, serif')
    c.line(270, 432, 590, 432, TEAL, 2)
    c.text(440, 460, 'hidden weights stay fixed', 19, MUTED, 'middle')
    return figure(c,
        'An input passes through two fixed random hidden layers; gold connections mark the trainable final readout.',
        'Random hidden layers construct a nonlinear representation of the input, while only the final readout is trained. The paper connects this construction to approximation in the reproducing kernel Hilbert space of the NNGP kernel.',
        'https://proceedings.mlr.press/v244/takhanov24a.html')


def _entropy():
    c = Canvas('A spectral ellipsoid covered by epsilon balls', 'Complexity of a kernel class')
    c.text(500, 85, 'How many ε-balls cover the function class?', 27, INK, 'middle', family='Georgia, serif')
    cx, cy, a, b, radius = 315, 266, 213, 97, 37
    centers = [(cx+50*i, cy+50*j) for i in range(-5, 6) for j in range(-3, 4)
               if (50*i/(a+radius))**2+(50*j/(b+radius))**2 <= 1]
    for x,y in centers:
        c.circle(x,y,radius,TEAL,TEAL,1.1,.075)
        c.circle(x,y,2.5,TEAL,opacity=.34)
    pts=[(cx+a*math.cos(i*math.tau/200),cy+b*math.sin(i*math.tau/200)) for i in range(201)]
    c.polyline(pts,TEAL,3.2)
    c.arrow(cx,cy,cx+a,cy,GOLD,2.5)
    c.arrow(cx,cy,cx,cy-b,BLUE,2.5)
    c.text(cx+106,cy-13,'√λ₁',23,GOLD,'middle')
    c.text(cx-13,cy-45,'√λ₂',23,BLUE,'end')
    c.circle(cx-150,cy+50,radius,'none',TEAL,2.2)
    c.line(cx-150,cy+50,cx-150+radius,cy+50,TEAL,2.2)
    c.text(cx-150+radius/2,cy+42,'ε',23,TEAL,'middle')
    c.text(315,422,'Covering number Nε',24,TEAL,'middle')
    c.arrow(571,266,634,266,MUTED,2.5)
    c.text(806,170,'Kernel spectrum',24,INK,'middle')
    _axes(c,674,361,267,155)
    for i,h in enumerate([136,81,48,29,17,10]):
        c.rect(692+i*39,361-h,24,h,TEAL if i<2 else BLUE,radius=3,opacity=1-.08*i)
    c.text(806,422,'Hε = log Nε',26,GOLD,'middle',family='Georgia, serif')
    # The disk grid covers the ellipse: spacing/sqrt(2) < radius, and the
    # retained grid extends beyond the boundary. Check the boundary explicitly.
    assert max(min(math.hypot(x-u,y-v) for u,v in centers) for x,y in pts) < radius
    return figure(c,
        'Overlapping epsilon balls cover an ellipse whose principal semiaxes are square roots of kernel eigenvalues; a descending spectrum appears alongside.',
        'In a finite-dimensional L² projection, an RKHS unit ball becomes a spectral ellipsoid. This schematic connects its covering by ε-balls with kernel eigenvalues—the quantities governing the entropy bounds studied in the paper.',
        'https://arxiv.org/abs/2204.04512')


def _intrinsic():
    c = Canvas('Kernel geometry and approximation reveal different notions of dimension', 'Intrinsic dimension')
    c.text(500, 82, 'Two ways to measure the same domain', 27, INK, 'middle', family='Georgia, serif')
    # A finite-stage Cantor dust, an exact illustrative fractal construction.
    intervals = [(0,1)]
    for _ in range(4):
        intervals=[q for a,b in intervals for q in [(a,a+(b-a)/3),(b-(b-a)/3,b)]]
    for ax,bx in intervals:
        for ay,by in intervals:
            c.rect(65+280*ax,127+280*ay,280*(bx-ax),280*(by-ay),TEAL,radius=.6)
    c.text(205,449,'Fractal domain Ω',23,TEAL,'middle')
    c.circle(390,267,5,GOLD)
    c.line(351,267,390,267,GOLD,2.5)
    c.path('M390 267 Q427 267 445 210 L474 169',GOLD,2.5)
    c.path('M390 267 Q427 267 445 329 L474 365',GOLD,2.5)
    c.arrow(470,173,492,150,GOLD,2.5)
    c.arrow(470,361,492,384,GOLD,2.5)
    c.rect(511,111,435,143,WHITE,LINE,10,1)
    c.rect(511,291,435,143,WHITE,LINE,10,1)
    for i in range(4):
        for j in range(3):
            c.rect(535+i*28,135+j*28,27,27,PALE if (i+j)%3 else '#d2dfd2',LINE,0,1)
    for x,y in [(544,148),(569,165),(578,203),(610,142),(619,182),(637,205)]:c.circle(x,y,3.5,TEAL)
    c.text(693,158,'dρ',34,TEAL,family='Georgia, serif')
    c.text(693,195,'Metric covering',24,INK)
    c.text(693,225,'kernel-induced distance',18,MUTED)
    for i,h in enumerate([73,51,35,24,16]):c.rect(537+i*23,402-h,14,h,BLUE,radius=2)
    c.text(693,337,'dK',34,BLUE,family='Georgia, serif')
    c.text(693,374,'Approximation widths',24,INK)
    c.text(693,404,'best low-dimensional spaces',18,MUTED)
    return figure(c,
        'A finite-stage Cantor dust branches into a covering-grid diagram for kernel-metric dimension and a spectral schematic for approximation-width dimension.',
        'A finite-stage Cantor dust illustrates a domain with nontrivial geometry. The paper distinguishes dimension measured by coverings in the kernel metric from effective dimension defined through approximation widths; these need not coincide on fractal domains.',
        'https://arxiv.org/abs/2601.16139')


def _conditional():
    c = Canvas('An unpenalized trend plus a penalized kernel residual', 'Conditional kernel ridge regression')
    c.text(500,78,'Keep the trend. Regularize the residual.',27,INK,'middle',family='Georgia, serif')
    def trend(t): return .33+.37*t
    def residual(t): return .19*math.sin(2*math.pi*t)+.075*math.sin(4*math.pi*t)
    plot_y=326
    for j in range(3):
        x=57+j*337
        _axes(c,x,plot_y,214,171)
        c.line(x,plot_y-85,x+214,plot_y-85,LINE,1,dash='4 5',opacity=.6)
        if j == 1:
            c.text(x-9,plot_y-78,'0',18,MUTED,'end')
        fn=[trend,lambda t:.5+residual(t),lambda t:trend(t)+residual(t)][j]
        points=[(x+214*i/160,plot_y-171*fn(i/160)) for i in range(161)]
        c.polyline(points,[GOLD,BLUE,TEAL][j],4)
    c.text(164,130,'Unpenalized part',22,GOLD,'middle')
    c.text(501,130,'Kernel residual',22,BLUE,'middle')
    c.text(838,130,'Prediction',22,TEAL,'middle')
    c.text(326,249,'+',40,MUTED,'middle')
    c.text(663,249,'=',40,MUTED,'middle')
    c.text(164,374,'f₀ ∈ span{1, x}',25,GOLD,'middle',family='Georgia, serif')
    c.text(501,374,'g',29,BLUE,'middle',family='Georgia, serif')
    c.text(838,374,'f = f₀ + g',28,TEAL,'middle',family='Georgia, serif')
    c.rect(365,402,272,43,WHITE,LINE,7,1)
    c.text(501,432,'penalty on g only',22,BLUE,'middle')
    return figure(c,
        'An illustrative linear trend and a curved kernel residual add to form a prediction, with only the residual marked as penalized.',
        'An illustrative prediction separates into an unpenalized linear trend and a curved kernel residual. Conditional KRR allows a chosen feature space to remain unpenalized while controlling the complexity of the residual component.',
        'https://arxiv.org/abs/2605.26067')


def build_figures():
    return {
        'mercer-uniform-convergence':_mercer(),
        'multi-layer-random-features':_random_features(),
        'kernel-entropy':_entropy(),
        'intrinsic-dimensions':_intrinsic(),
        'conditional-krr':_conditional(),
    }
