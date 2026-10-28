"""Original illustrations of signed codes, quaternionic factors, and lifting.

The illustrations deliberately distinguish exact small mathematical objects
from schematics of configurations in higher-dimensional spaces.
"""
import math
from itertools import combinations, product

from .common import Canvas, figure, INK, TEAL, GOLD, BLUE, MUTED, LINE, PALE, PAPER, WHITE, ROSE


def _rotate(v, rotations):
    v = list(v)
    for a, b, angle in rotations:
        x, y = v[a], v[b]
        v[a] = x*math.cos(angle)-y*math.sin(angle)
        v[b] = x*math.sin(angle)+y*math.cos(angle)
    return v


def _cell_vertices():
    vertices = []
    for axis in range(4):
        for sign in [-1, 1]:
            p = [0.0]*4
            p[axis] = sign
            vertices.append(p)
    vertices += [list(signs) for signs in product([-.5, .5], repeat=4)]
    return vertices


def _draw_cell(c, cx, cy, radius, angle=0, color=TEAL):
    vertices = _cell_vertices()
    edges = [(i,j) for i,j in combinations(range(24),2)
             if abs(sum(a*b for a,b in zip(vertices[i],vertices[j]))-.5)<1e-9]
    assert len(edges) == 96
    projected = [_rotate(p,[(0,3,.72+angle),(1,2,.758),(0,2,.55),(1,3,.35)]) for p in vertices]
    points = [(cx+radius*p[0],cy+radius*p[1]) for p in projected]
    assert len({(round(x,6),round(y,6)) for x,y in points}) == 24
    c.circle(cx,cy,radius+10,WHITE,LINE,1,opacity=.6)
    for i,j in edges:
        c.line(*points[i],*points[j],color,1.3,opacity=.43)
    for i,(x,y) in enumerate(points):
        c.circle(x,y,4.3,GOLD if i<8 else color,WHITE,1.3)


def _signed_graph():
    c=Canvas('A small signed Johnson graph and an independent set','Signed supports · independent sets')
    vertices=[]
    for support in combinations(range(3),2):
        for signs in product([-1,1],repeat=2):
            v=[0,0,0]
            for i,sgn in zip(support,signs):v[i]=sgn
            vertices.append(v)
    edges=[(i,j) for i,j in combinations(range(12),2) if sum(a*b for a,b in zip(vertices[i],vertices[j]))==1]
    selected={i for i,v in enumerate(vertices) if v[2]==0}
    assert len(edges)==24 and len(selected)==4
    assert all(not(i in selected and j in selected) for i,j in edges)
    projected=[_rotate(v,[(0,2,.6),(1,2,.4),(0,1,-.15)]) for v in vertices]
    points=[(285+118*v[0],237+118*v[1]) for v in projected]
    for i,j in edges:c.line(*points[i],*points[j],LINE,2.8)
    for i,(x,y) in enumerate(points):
        c.circle(x,y,12 if i in selected else 8.5,TEAL if i in selected else WHITE,TEAL if i in selected else MUTED,2)
        if i in selected:c.circle(x,y,19,'none',GOLD,2)
    c.text(285,435,'J±(3, 2)',27,INK,'middle',family='Georgia, serif')
    c.arrow(490,238,565,238,GOLD,2.5)
    c.rect(615,99,290,277,WHITE,LINE,12)
    c.text(760,139,'Independent set',25,TEAL,'middle',600)
    for row,i in enumerate(sorted(selected)):
        y=185+row*51
        c.circle(647,y-7,6,TEAL)
        for col,value in enumerate(vertices[i]):
            x=704+col*54
            c.text(x,y,'+' if value==1 else '−' if value==-1 else '0',28,TEAL if value else MUTED,'middle',500)
    c.text(760,435,'u · v = 1 defines an edge',21,MUTED,'middle')
    return figure(c,
        'Twelve vertices of the signed Johnson graph J±(3,2), with four mutually nonadjacent vertices highlighted and their signed coordinate vectors shown at right.',
        'A small signed Johnson graph illustrates the independent-set viewpoint: the four highlighted signed vectors have no edges between them. The paper studies the richer case J±(n,4), where independent sets produce kissing arrangements.',
        'https://arxiv.org/abs/2606.03299', 'Original mathematical illustration')


def _block(c,cx,cy,color,phase=0):
    # A schematic, not a projection of the paper's sixty actual coordinates.
    c.circle(cx,cy,109,WHITE,LINE,1.5)
    for ring in [0,1]:
        for i in range(24):
            a=2*math.pi*i/24+phase+ring*.09
            radius=86+ring*12+4*math.sin(3*a+phase)
            c.circle(cx+radius*math.cos(a),cy+.83*radius*math.sin(a),3.4,color,WHITE,.7)
    for i in range(12):
        a=2*math.pi*i/12+phase
        c.line(cx,cy,cx+44*math.cos(a),cy+36*math.sin(a),GOLD,1.1,opacity=.45)
        c.circle(cx+44*math.cos(a),cy+36*math.sin(a),4,GOLD)
    c.path(f'M {cx-65} {cy+116} Q {cx-4} {cy+150} {cx+61} {cy+116}',color,2.4)
    c.arrow(cx+49,cy+127,cx+63,cy+116,color,2.4,8)


def _extra_sphere():
    c=Canvas('Flexible blocks and fixed bridges in the search for an 841st sphere','Structure-guided geometric search')
    for i in range(13):
        y=155+i*14
        c.path(f'M 296 {y} C 411 {y-35} 591 {340-i*13} 704 {340-i*13}',LINE,1.2,opacity=.7)
    _block(c,210,250,TEAL,.15)
    _block(c,790,250,BLUE,.53)
    c.text(210,104,'ℝ⁶ × {0}',27,INK,'middle',family='Georgia, serif')
    c.text(790,104,'{0} × ℝ⁶',27,INK,'middle',family='Georgia, serif')
    c.rect(386,203,228,102,PAPER,None,12)
    c.text(500,247,'720',43,TEAL,'middle',500,family='Georgia, serif')
    c.text(500,281,'fixed bridges',22,MUTED,'middle')
    c.circle(500,110,27,PALE,None)
    c.circle(500,110,15,GOLD,WHITE,2)
    c.text(546,119,'+1',28,GOLD,weight=600)
    c.arrow(500,197,500,149,GOLD,2.5,10,dash='5 7')
    c.text(210,435,'60-point block',25,TEAL,'middle',500)
    c.text(790,435,'60-point block',25,BLUE,'middle',500)
    c.text(500,404,'840 → 841',28,INK,'middle',family='Georgia, serif')
    return figure(c,
        'Schematic of two flexible sixty-point blocks in complementary six-dimensional spaces, coupled by 720 fixed bridge vectors, with an additional point marking the optimization target.',
        'Two 60-point blocks can move while 720 bridge vectors remain fixed. This flexibility supplies structured starting configurations for the paper’s optimization toward 841 points. The drawing shows the decomposition, not the final twelve-dimensional coordinates.',
        'https://arxiv.org/abs/2606.18984')


def _quaternionic():
    c=Canvas('Three exact 24-cell projections in a quaternionic construction','Three quaternionic coordinate factors')
    c.text(500,92,'ℝ¹² ≅ ℍ ⊕ ℍ ⊕ ℍ',33,INK,'middle',family='Georgia, serif')
    for i,(x,color,angle) in enumerate([(181,TEAL,0),(500,BLUE,.18),(819,TEAL,-.2)]):
        _draw_cell(c,x,235,112,angle,color)
        c.text(x,382,'ℍ'+['₁','₂','₃'][i],28,color,'middle',family='Georgia, serif')
    c.rect(148,405,704,50,WHITE,LINE,8)
    c.text(500,439,'3 × 24  +  384  +  384  =  840',28,INK,'middle',family='Georgia, serif')
    return figure(c,
        'Three orthogonal projections of the regular 24-cell, one for each quaternionic coordinate factor, above the decomposition three times 24 plus 384 plus 384 equals 840.',
        'Each picture is an exact two-dimensional projection of a regular 24-cell. Three orthogonal quaternionic factors, together with two 384-point families, form the paper’s 840-point structural model for the numerical 841-point arrangement.',
        'https://arxiv.org/abs/2609.09179', 'Original mathematical illustration')


def _lifting():
    c=Canvas('Leech lifting and the paper’s certified kissing-number lower bounds','Leech lifting · higher dimensions')
    # A qualitative two-axis schematic of the 24-dimensional and auxiliary factors.
    c.path('M 60 308 L 326 226 L 571 303 L 305 388 Z',LINE,1.5,PALE,opacity=.6)
    c.arrow(305,310,558,386,MUTED,2,9)
    c.arrow(305,310,92,377,MUTED,2,9)
    c.arrow(305,310,305,90,MUTED,2,9)
    c.text(334,99,'ℝᵏ',26,INK,family='Georgia, serif')
    c.text(548,424,'ℝ²⁴',26,INK,'end',family='Georgia, serif')
    c.path('M 102 302 C 128 251 461 244 519 296 C 555 340 189 378 102 302 Z',TEAL,2,'none',.3)
    for i in range(34):
        a=2*math.pi*i/34
        x=305+190*math.cos(a)
        y=309+48*math.sin(a)+17*math.cos(a)
        c.circle(x,y,3.3,TEAL,WHITE,.6)
    base_points=[(175,293),(226,275),(372,280),(443,308)]
    for i,(x,y) in enumerate(base_points):
        c.circle(x,y,6,WHITE,TEAL,2)
        for sign in [-1,1]:
            nx=305+.77*(x-305)+sign*10
            ny=y-92+sign*24
            c.line(x,y,nx,ny,GOLD,1.5,dash='4 5',opacity=.8)
            c.circle(nx,ny,5.6,GOLD,WHITE,1)
    c.circle(305,135,8,BLUE,WHITE,2)
    c.circle(305,180,6.5,BLUE,WHITE,2)
    c.text(85,438,'Leech shell + auxiliary directions',21,TEAL)
    c.line(620,87,620,445,LINE,1.5)
    c.text(799,106,'Bounds in this paper',23,INK,'middle',500)
    c.text(686,151,'d',24,MUTED,'middle',family='Georgia, serif')
    c.text(841,151,'τ(d) ≥',24,MUTED,'middle',family='Georgia, serif')
    bounds=[(25,197583),(26,199868),(27,201589),(29,209970),(31,238666)]
    for i,(dimension,count) in enumerate(bounds):
        y=185+i*52
        c.rect(653,y-21,291,44,WHITE,None,6)
        c.text(687,y+9,str(dimension),25,TEAL,'middle',600)
        c.text(842,y+9,f'{count:,}',27,INK,'middle',family='Georgia, serif')
    return figure(c,
        'Schematic of points lifted from a Leech-lattice shell into additional coordinates, alongside the paper’s certified lower bounds in dimensions 25, 26, 27, 29, and 31.',
        'Leech lifting combines a 24-dimensional lattice shell with additional coordinate directions. This schematic introduces the geometry behind the constructions; the values at right are the paper’s certified lower bounds, not estimates read from the drawing.',
        'https://github.com/k-nic/kissing_d25-31/blob/main/paper.pdf')


def build_figures():
    return {
        'signed-johnson-graphs':_signed_graph(),
        '841st-sphere':_extra_sphere(),
        'quaternionic-kissing':_quaternionic(),
        'kissing-dimensions-25-31':_lifting(),
    }
