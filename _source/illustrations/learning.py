"""Original illustrations for papers on learning, geometry, and gradient information.

The coordinates below are illustrative examples, never reported experimental data.
"""
import math
import random
from .common import Canvas, figure, INK, TEAL, GOLD, BLUE, MUTED, LINE, PALE, PAPER, WHITE, ROSE


def _axes(c, x, y, w, h):
    c.arrow(x, y, x+w, y, MUTED, 1.8, 7)
    c.arrow(x, y, x, y-h, MUTED, 1.8, 7)


def _monotonization():
    c=Canvas('Selecting a largest monotone subsample', 'Order and consistent samples')
    c.text(245, 100, 'Training sample', 25, INK, 'middle')
    c.text(755, 100, 'Retain 6 of 8', 25, INK, 'middle')
    vals=[1,3,2,4,6,5,7,8]
    keep={0,2,3,5,6,7}
    # The longest increasing subsequences have length six.
    lengths=[1]*len(vals)
    for i in range(len(vals)):
        lengths[i]=1+max([lengths[j] for j in range(i) if vals[j]<=vals[i]] or [0])
    assert max(lengths)==len(keep)
    for ox, selected in [(80,False),(590,True)]:
        _axes(c, ox-18, 365, 365, 235)
        pts=[(ox+42*i,352-25*y) for i,y in enumerate(vals)]
        if selected:
            c.polyline([pts[i] for i in sorted(keep)],TEAL,3)
        else:
            for a,b in [(1,2),(4,5)]:
                c.line(*pts[a],*pts[b],ROSE,3,dash='6 5')
        for i,(x,y) in enumerate(pts):
            if selected and i not in keep:
                c.circle(x,y,9,WHITE,ROSE,2,opacity=.65)
                c.line(x-5,y-5,x+5,y+5,ROSE,1.5)
                c.line(x-5,y+5,x+5,y-5,ROSE,1.5)
            else:
                c.circle(x,y,9,ROSE if not selected and i in [1,4] else TEAL,WHITE,2)
        c.text(ox+332,393,'x',22,MUTED,'middle')
        c.text(ox-26,130,'y',22,MUTED,'middle')
    c.arrow(457,252,543,252,GOLD,3,12)
    c.text(500,442,'x ≤ x′  implies  y ≤ y′',26,TEAL,'middle',family='Georgia, serif')
    return figure(c,
        'Two scatterplots show eight ordered sample points and a largest six-point subsample with nondecreasing answers. Two excluded points are crossed out.',
        'A one-dimensional example: retain six of eight sample pairs so that increasing inputs have nondecreasing answers. The paper studies the largest consistent subsample under more general partial orders, rather than changing the observed answers.',
        'https://www.mathnet.ru/eng/zvmmf4912', 'Original mathematical illustration')


def _distributions():
    c=Canvas('Approximating data by a distribution supported on a subspace', 'Dimension reduction through distributions')
    c.text(247,98,'Empirical distribution',25,INK,'middle')
    c.text(755,98,'Support on a subspace',25,INK,'middle')
    for ox in [247,755]:
        _axes(c,ox-155,365,320,235)
    for a,b in [(146,72),(117,57),(85,40)]:
        c.raw(f'<ellipse cx="247" cy="245" rx="{a}" ry="{b}" fill="none" stroke="{LINE}" stroke-width="1.4" transform="rotate(-25 247 245)"/>')
    rng=random.Random(19)
    pts=[]
    for i in range(75):
        t=rng.gauss(0,68);n=rng.gauss(0,28)
        if abs(t)>137: t*=.75
        x=t*.906+n*.423;y=-t*.423+n*.906
        pts.append((t,x,y))
        c.circle(247+x,245+y,3.5,TEAL,opacity=.65)
    c.arrow(460,245,540,245,GOLD,3,12)
    c.line(605,315,905,175,TEAL,3)
    for i,(t,x,y) in enumerate(pts):
        tx=755+t*.906;ty=245-t*.423
        if i%5==0:
            c.circle(755+x,245+y,3.5,GOLD,opacity=.45)
            c.line(755+x,245+y,tx,ty,GOLD,1.1,dash='3 4',opacity=.65)
        c.circle(tx,ty,3.5,TEAL,opacity=.65)
    c.text(912,175,'L',26,TEAL,family='Georgia, serif')
    c.text(500,436,'supp(T) ⊆ L     ·     dim L = k',27,TEAL,'middle',family='Georgia, serif')
    return figure(c,
        'A cloud of sample points is contrasted with a model distribution whose points lie on a straight subspace. Dashed lines suggest the reduction in support.',
        'A schematic two-dimensional cloud and a model supported on a line. The paper represents dimension reduction through tempered distributions, using a penalty to encourage low-dimensional support and an alternating scheme to find the model.',
        'https://arxiv.org/abs/1903.05083')


def _autoencoder():
    c=Canvas('A correcting map and a rank-controlled autoencoder', 'Geometry of a learned manifold')
    c.text(260,98,'A correcting map',25,INK,'middle')
    c.text(750,98,'An autoencoder',25,INK,'middle')
    # A smooth illustrative curve with off-manifold observations.
    curve=lambda t:(80+350*t,255-86*math.sin(2*math.pi*t))
    c.polyline([curve(i/160) for i in range(161)],TEAL,5)
    rng=random.Random(23)
    for i in range(52):
        t=(i+.5)/52;x,y=curve(t)
        dx=rng.gauss(0,10);dy=rng.choice([-1,1])*rng.uniform(16,57)
        c.circle(x+dx,y+dy,3.7,GOLD,opacity=.55)
        if i%7==2:
            c.arrow(x+dx,y+dy,x,y,GOLD,1.8,7)
            c.circle(x,y,4.5,TEAL,WHITE,1)
    x,y=curve(.47)
    c.text(x-8,y+54,'f(x)',25,TEAL,family='Georgia, serif')
    layers=[(575,[165,220,275,330]),(655,[205,290]),(735,[247.5]),(815,[205,290]),(895,[165,220,275,330])]
    for (x,ys),(xx,yys) in zip(layers,layers[1:]):
        for y in ys:
            for yy in yys:c.line(x,y,xx,yy,LINE,1.8)
    for j,(x,ys) in enumerate(layers):
        for y in ys:c.circle(x,y,13,GOLD if j==2 else TEAL,WHITE,2)
    c.rect(701,211,68,74,'none',GOLD,12,1.4)
    c.text(735,368,'code',22,GOLD,'middle')
    c.text(260,438,'Nearby points → learned manifold',23,MUTED,'middle')
    c.text(750,438,'rank Jf ≤ k',28,TEAL,'middle',family='Georgia, serif')
    return figure(c,
        'Noisy observations are mapped onto a smooth curve. Beside them, an hourglass-shaped autoencoder highlights its code layer and a Jacobian rank constraint.',
        'An illustrative correcting map sends nearby observations onto a curve. The autoencoder sketch highlights two controls on dimensionality: its code space and the rank of its Jacobian. The paper also penalizes curvature of the learned map.',
        'https://arxiv.org/abs/2306.14194')


def _high_frequency():
    c=Canvas('Oscillatory targets and modular multiplication', 'When gradients reveal little about a target')
    c.text(255,98,'Oscillatory targets',25,INK,'middle')
    c.text(755,98,'Modular multiplication',25,INK,'middle')
    for row,freq,color in [(0,8,TEAL),(1,16,BLUE),(2,32,GOLD)]:
        cy=164+82*row
        c.line(80,cy,438,cy,LINE,1.2)
        pts=[(80+358*j/900,cy-26*math.sin(freq*2*math.pi*j/900)) for j in range(901)]
        c.polyline(pts,color,2.2)
        c.text(463,cy+7,'ω = '+str(freq),22,color)
    center=(760,255);r=108
    c.circle(*center,r,'none',LINE,1.4)
    xy=lambda j:(center[0]+r*math.cos(-math.pi/2+2*math.pi*j/13),center[1]+r*math.sin(-math.pi/2+2*math.pi*j/13))
    for j in range(1,13):
        k=5*j%13;x,y=xy(j);xx,yy=xy(k)
        d=math.hypot(xx-x,yy-y)
        c.arrow(x+(xx-x)*9/d,y+(yy-y)*9/d,xx-(xx-x)*9/d,yy-(yy-y)*9/d,TEAL if j%2 else GOLD,1.4,6)
    for j in range(13):
        x,y=xy(j);c.circle(x,y,6,GOLD if j==0 else TEAL,WHITE,1.2)
        a=-math.pi/2+2*math.pi*j/13
        c.text(center[0]+132*math.cos(a),center[1]+132*math.sin(a)+7,str(j),21,INK,'middle')
    c.text(255,434,'sin(ωx)',29,TEAL,'middle',family='Georgia, serif')
    c.text(760,434,'x ↦ 5x mod 13',29,TEAL,'middle',family='Georgia, serif')
    return figure(c,
        'Three exact sine waves have frequencies eight, sixteen and thirty-two. A circular diagram on the right connects each nonzero residue to five times that residue modulo thirteen.',
        'Three illustrative periodic targets and multiplication by five modulo thirteen. The paper connects these kinds of oscillatory structure to target classes whose learning gradients can carry very little information under the analyzed assumptions.',
        'https://arxiv.org/abs/2310.12660','Original mathematical illustration')


def _pairwise():
    c=Canvas('Pairwise-independent outputs from two fair bits', 'Pairwise independence and learning')
    c.text(290,96,'Every pair is independent',25,INK,'middle')
    nodes=[(160,193,'A',TEAL),(420,193,'B',BLUE),(290,355,'A ⊕ B',GOLD)]
    for a,b in [(0,1),(0,2),(1,2)]:
        c.line(nodes[a][0],nodes[a][1],nodes[b][0],nodes[b][1],LINE,3)
    for x,y,label,color in nodes:
        c.circle(x,y,48,WHITE,color,3)
        c.text(x,y+8,label,27,color,'middle',600)
    c.text(754,96,'Four equally likely states',25,INK,'middle')
    xs=[625,750,875]
    for x,t in zip(xs,['A','B','A ⊕ B']):c.text(x,146,t,24,INK,'middle',600)
    states=[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]
    for i,row in enumerate(states):
        y=187+54*i
        for j,(x,v) in enumerate(zip(xs,row)):
            fill=[TEAL,BLUE,GOLD][j] if v else PALE
            c.rect(x-32,y-24,64,42,fill,radius=6)
            c.text(x,y+5,str(v),25,WHITE if v else INK,'middle',600)
    # Every pair has all four binary outcomes exactly once.
    for a,b in [(0,1),(0,2),(1,2)]:assert len({(r[a],r[b]) for r in states})==4
    c.text(500,443,'Pairwise independence does not require joint independence',24,MUTED,'middle')
    return figure(c,
        'A triangle labels three bits A, B, and their exclusive-or. A four-row table shows that any pair takes all four binary combinations equally often.',
        'A, B, and A ⊕ B give an exact toy example of pairwise-independent outputs: every pair is uniform, although the triple is constrained. This illustrates the independence property behind the paper’s analysis of gradient information.',
        'https://cic.iacr.org/p/1/3/32','Original mathematical illustration')


def _gradient_information():
    c=Canvas('Input collision entropy and variation of gradients across targets', 'What information survives in a gradient?')
    c.text(242,98,'Input collisions',25,INK,'middle')
    c.text(752,98,'Variation across targets',25,INK,'middle')
    # Exact uniform four-point distribution; matched pairs are the collision event.
    left=108;top=137;size=57
    for i in range(4):
        for j in range(4):
            c.rect(left+j*size,top+i*size,size-6,size-6,TEAL if i==j else PALE,radius=5)
    c.text(227,398,'P(X = X′) = 1/4',24,TEAL,'middle',family='Georgia, serif')
    c.text(227,435,'Ec = −log Σ pᵢ²',25,TEAL,'middle',family='Georgia, serif')
    c.arrow(400,250,554,250,GOLD,2.8,12)
    c.text(478,218,'ε, Ec',26,GOLD,'middle',family='Georgia, serif')
    ox=630;oy=355
    _axes(c,ox,oy,285,215)
    # Schematic nearby vectors, not a simulation or experimental claim.
    tips=[(828,176),(835,186),(842,181),(826,190),(837,174),(846,192)]
    c.raw(f'<path d="M630 355 L819 160 Q859 166 865 201 Z" fill="{PALE}"/>')
    for i,(x,y) in enumerate(tips):
        c.arrow(ox,oy,x,y,TEAL if i%2==0 else GOLD,2,8)
        c.circle(x,y,4,TEAL if i%2==0 else GOLD)
    c.circle(ox,oy,6,INK)
    c.text(754,398,'Different targets, similar gradients',22,MUTED,'middle')
    c.text(754,435,'variance depends on ε and Ec',24,TEAL,'middle',family='Georgia, serif')
    return figure(c,
        'The diagonal of a four-by-four grid marks collisions between independent draws from a uniform four-point distribution. Nearby arrows schematically represent similar learning gradients for different target functions.',
        'The diagonal marks matching independent inputs in a uniform four-point example. The paper bounds variation of the learning gradient across target functions using collision entropy and a parameter measuring pairwise dependence. Gradient arrows are schematic, not experimental results.',
        'https://arxiv.org/abs/2505.22158')


def build_figures():
    return {
        'sample-monotonization':_monotonization(),
        'dimension-reduction-distributions':_distributions(),
        'autoencoders-jacobian-rank':_autoencoder(),
        'gradient-descent-high-frequency':_high_frequency(),
        'pairwise-independence':_pairwise(),
        'gradient-informativeness':_gradient_information(),
    }
