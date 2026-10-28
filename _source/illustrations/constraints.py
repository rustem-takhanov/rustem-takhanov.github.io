"""Original, paper-specific mathematical schematics for constraint satisfaction."""
import itertools
import math

from .common import Canvas, figure, INK, TEAL, GOLD, BLUE, MUTED, LINE, PALE, PAPER, WHITE, ROSE


def _graph(canvas, points, edges, fills=None, labels=None, r=20, color=TEAL, width=3):
    for i, j in edges:
        canvas.line(*points[i], *points[j], color, width)
    for i, (x, y) in enumerate(points):
        canvas.node(x, y, labels[i] if labels else None, fills[i] if fills else TEAL, r)


def _minimum_cost():
    c = Canvas('A cycle mapped to a two-value constraint template', 'Feasible assignments and their cost')
    points = [(245 + 130 * math.cos(t), 240 + 130 * math.sin(t))
              for t in [math.pi/6 + k*math.pi/3 for k in range(6)]]
    edges = [(i, (i+1) % 6) for i in range(6)]
    # This is a genuine homomorphism from C6 to the edge K2.
    mapping = [i % 2 for i in range(6)]
    assert all(mapping[a] != mapping[b] for a, b in edges)
    _graph(c, points, edges, [TEAL if i == 0 else GOLD for i in mapping],
           [str(i+1) for i in range(6)], r=25, color=MUTED, width=3)
    c.text(245, 425, 'Variables and constraints', 24, INK, 'middle')
    c.arrow(435, 240, 580, 240, TEAL, 3, 13)
    c.text(508, 206, 'f', 34, TEAL, 'middle', family='Georgia, serif')
    c.line(690, 240, 875, 240, MUTED, 4)
    c.node(690, 240, 'a', TEAL, 39)
    c.node(875, 240, 'b', GOLD, 39)
    c.text(783, 334, 'Allowed values', 24, INK, 'middle')
    c.text(783, 160, 'a ≠ b', 30, MUTED, 'middle', family='Georgia, serif')
    c.text(783, 425, 'minimize  Σᵥ cᵥ,f(v)', 27, TEAL, 'middle', family='Georgia, serif')
    return figure(c,
        'Six variables on a cycle alternate between two colors and map to the corresponding values of a two-vertex template; assignment costs are minimized.',
        'A six-cycle mapped to a two-value template illustrates a feasible homomorphism. Minimum cost homomorphism adds a cost to each variable–value choice and seeks the least expensive assignment that preserves every constraint.',
        'https://arxiv.org/abs/0708.3226', 'Original mathematical illustration')


def _extensions():
    c = Canvas('Several unary cost functions combined in one objective', 'Beyond a single cost function')
    profiles = [(150, [0, 2, 4], 'r₁', TEAL), (500, [4, 1, 0], 'r₂', GOLD),
                (850, [8, 4, 4], 'r₁ + 2r₂', BLUE)]
    for center, values, name, color in profiles:
        c.text(center, 110, name, 32, color, 'middle', family='Georgia, serif')
        c.line(center-100, 343, center+100, 343, LINE, 2)
        for i, value in enumerate(values):
            x = center - 75 + i * 75
            height = value * 23
            c.rect(x-23, 340-height, 46, max(height, 3), color, radius=5)
            c.text(x, 320-height, str(value), 24, color, 'middle', 600)
            c.text(x, 379, 'abc'[i], 26, INK, 'middle', family='Georgia, serif')
        c.text(center, 428, 'Toy costs on D = {a, b, c}' if center == 500 else '', 21, MUTED, 'middle')
    c.text(325, 258, '+ 2 ×', 31, MUTED, 'middle', family='Georgia, serif')
    c.text(675, 258, '=', 38, MUTED, 'middle', family='Georgia, serif')
    assert [a + 2*b for a,b in zip([0,2,4],[4,1,0])] == [8,4,4]
    return figure(c,
        'Three bar profiles on domain values a, b, c show unary costs r1 = (0,2,4), r2 = (4,1,0), and their weighted sum (8,4,4).',
        'An illustrative pair of unary cost functions combines into a weighted objective on three possible values. The extended problem allows a family of such costs while requiring the assignment to satisfy a fixed constraint language.',
        'https://arxiv.org/abs/1210.2260')


def _structural():
    c = Canvas('A structural restriction and a fixed relation constrain opposite sides of a CSP', 'The hybrid constraint satisfaction setting')
    c.text(250, 103, 'Restrict the input', 28, INK, 'middle', family='Georgia, serif')
    points = [(250,162),(152,252),(348,252),(95,345),(203,345),(297,345),(405,345)]
    edges = [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]
    fills = [TEAL,GOLD,GOLD,TEAL,TEAL,TEAL,TEAL]
    _graph(c,points,edges,fills,r=22,color=MUTED,width=3)
    c.text(250, 426, 'Example: tree-shaped instances', 23, MUTED, 'middle')
    c.arrow(470, 260, 565, 260, TEAL, 3, 12)
    c.text(518, 219, 'R → Γ', 26, TEAL, 'middle', family='Georgia, serif')
    c.text(785, 103, 'Fix the relations', 28, INK, 'middle', family='Georgia, serif')
    colors=[TEAL,GOLD,BLUE]
    startx,starty,step=684,170,64
    for i,col in enumerate(colors):
        c.circle(startx+i*step+27,138,10,col)
        c.circle(651,starty+i*step+27,10,col)
    for row in range(3):
        for col in range(3):
            x,y=startx+col*step,starty+row*step
            c.rect(x,y,54,54,WHITE,LINE,radius=5,width=1)
            if row != col:
                c.circle(x+27,y+27,10,TEAL)
            else:
                c.line(x+18,y+18,x+36,y+36,ROSE,2.5)
                c.line(x+18,y+36,x+36,y+18,ROSE,2.5)
    c.text(785, 426, 'Example: unequal colors', 23, MUTED, 'middle')
    return figure(c,
        'A tree-shaped instance is shown next to a three-color inequality relation whose diagonal combinations are forbidden, illustrating restrictions on both sides of a CSP.',
        'A toy coloring problem separates the shape of an input instance from its allowed relations. Hybrid CSPs restrict both sides; the paper studies which structural restrictions can change the complexity of the resulting problem.',
        'https://arxiv.org/abs/1504.07067')


def _lifted():
    c = Canvas('Lifting a two-value domain into one fiber per input variable', 'A separate domain above each variable')
    centers=[170,500,830]
    for i in range(2):c.line(centers[i],110,centers[i+1],110,MUTED,3)
    for i,x in enumerate(centers):
        c.node(x,110,'x'+str(i+1),TEAL,26)
        c.arrow(x,148,x,188,MUTED,2,8,dash='5 5')
        c.rect(x-92,200,184,194,WHITE,LINE,radius=17,width=1.5)
    # The path uses inequality. Lifted edges connect (v, a) to (w, b) only for a != b.
    for left,right in zip(centers,centers[1:]):
        c.line(left,250,right,345,TEAL,2.5,opacity=.65)
        c.line(left,345,right,250,GOLD,2.5,opacity=.65)
    for i,x in enumerate(centers):
        c.node(x,250,'0',TEAL,24)
        c.node(x,345,'1',GOLD,24)
        c.text(x,439,'{x'+str(i+1)+'} × D',25,INK,'middle',family='Georgia, serif')
    return figure(c,
        'A three-variable path is lifted to three fibers, each containing a copy of the values zero and one. Crossed edges between adjacent fibers encode inequality.',
        'For a path with a two-value inequality relation, lifting creates one copy of the domain per variable. The lifted language is the bridge between structural restrictions and the algebraic study of hybrid crisp and valued CSPs.',
        'https://arxiv.org/abs/1506.06540')


def _induced():
    c = Canvas('A Boolean solution set closed under a coordinatewise algebraic operation', 'Algebra inside a solution space')
    points={v:(155+160*v[0]-65*v[2],345-160*v[1]-65*v[2]) for v in itertools.product([0,1],repeat=3)}
    subset=[v for v in points if v[0]==v[1]]
    corners=[points[v] for v in [(0,0,0),(0,0,1),(1,1,1),(1,1,0)]]
    c.polyline(corners+[corners[0]],TEAL,1,fill=PALE,opacity=.7)
    for a in points:
        for b in points:
            if a < b and sum(x!=y for x,y in zip(a,b))==1:
                c.line(*points[a],*points[b],LINE,2.5)
    for v, (x,y) in points.items():
        c.circle(x,y,13,TEAL if v in subset else WHITE,TEAL if v in subset else LINE,2)
        if v in subset:
            dx,dy=(-18,26) if v[0]==0 else (19,-18)
            if v == (1,1,1):dx,dy=45,7
            c.text(x+dx,y+dy,''.join(map(str,v)),22,TEAL,'middle',600)
    c.text(216,93,'x₁ = x₂',30,TEAL,'middle',family='Georgia, serif')
    c.text(216,430,'A subset of {0,1}³',24,INK,'middle',family='Georgia, serif')
    c.line(435,105,435,390,LINE,1)
    c.text(708,103,'Closed under coordinatewise ∧',25,INK,'middle',family='Georgia, serif')
    columns=[575,710,845]
    rows=[(183,[1,1,0],TEAL),(268,[0,0,1],GOLD),(373,[0,0,0],BLUE)]
    for y,values,color in rows:
        for x,value in zip(columns,values):
            c.rect(x-34,y-33,68,58,WHITE,color,radius=8,width=2)
            c.text(x,y+7,str(value),29,color,'middle',600)
    for x in columns:
        c.text(x,232,'∧',24,MUTED,'middle')
        c.line(x-40,315,x+40,315,LINE,2)
    c.text(710,435,'solution ∧ solution = solution',22,TEAL,'middle')
    assert all(tuple(x & y for x,y in zip(a,b)) in subset for a in subset for b in subset)
    return figure(c,
        'The four Boolean triples satisfying x1 equals x2 form a highlighted plane in a cube. Coordinatewise AND of solutions 110 and 001 produces the solution 000.',
        'In this Boolean example, the solutions of x₁ = x₂ are closed under coordinatewise AND. Such closure makes a solution set a subalgebra of a product—the structure investigated through the paper’s induced CSP construction.',
        'https://arxiv.org/abs/1708.08292', 'Original mathematical illustration')


def _densification():
    c = Canvas('A sparse equality system and its dense closure have the same solutions', 'More constraints, the same solution set')
    left=[(145,165),(315,165),(315,325),(145,325)]
    right=[(685,165),(855,165),(855,325),(685,325)]
    sparse=[(0,1),(1,2),(2,3)]
    dense=list(itertools.combinations(range(4),2))
    for edge in dense:
        i,j=edge
        c.line(*right[i],*right[j],TEAL if edge in sparse else GOLD,3,
               None if edge in sparse else '8 7')
    _graph(c,left,sparse,labels=['x₁','x₂','x₃','x₄'],r=26,color=TEAL,width=3)
    for i,p in enumerate(right):c.node(*p,['x₁','x₂','x₃','x₄'][i],TEAL,26)
    c.text(230,99,'Sparse basis',29,INK,'middle',family='Georgia, serif')
    c.text(770,99,'Pairwise closure',29,INK,'middle',family='Georgia, serif')
    c.arrow(420,202,582,202,TEAL,3,12)
    c.text(500,176,'densify',23,TEAL,'middle')
    c.arrow(582,290,420,290,GOLD,3,12)
    c.text(500,332,'sparsify',23,GOLD,'middle')
    c.text(230,381,'3 equalities',23,MUTED,'middle')
    c.text(770,381,'6 equalities',23,MUTED,'middle')
    c.text(500,445,'Same solutions: (a, a, a, a)',28,TEAL,'middle',family='Georgia, serif')
    def solutions(edges):
        return {v for v in itertools.product(range(3),repeat=4) if all(v[i]==v[j] for i,j in edges)}
    assert solutions(sparse)==solutions(dense)
    return figure(c,
        'A path of three equality constraints on four variables expands into all six pairwise equalities. Added constraints are gold dashed edges; both systems have exactly the same solutions.',
        'Three equalities connecting four variables imply all six pairwise equalities. Densification adds the implied constraints; sparsification keeps a sufficient basis. This toy example preserves exactly the assignments in which all four values agree.',
        'https://arxiv.org/abs/2104.05065', 'Original mathematical illustration')


def _semiring():
    c = Canvas('Overlapping contiguous constraints on an ordered sequence', 'Local patterns, global aggregation')
    xs=[100+114*i for i in range(8)]
    c.text(500,105,'Z = ⊕ₓ  ⊗ₚ wₚ(xₚ)',34,TEAL,'middle',family='Georgia, serif')
    # Segment bands depict consecutive variables, including their common variable x4.
    c.rect(xs[1]-36,151,xs[3]-xs[1]+72,55,PALE,TEAL,radius=9,width=1.5)
    c.text((xs[1]+xs[3])/2,187,'ρ₁ on [2, 4]',24,TEAL,'middle')
    c.line(xs[1],206,xs[1],239,TEAL,2,dash='4 4')
    c.line(xs[3],206,xs[3],239,TEAL,2,dash='4 4')
    c.rect(xs[3]-36,327,xs[6]-xs[3]+72,55,'#eee5d6',GOLD,radius=9,width=1.5)
    c.text((xs[3]+xs[6])/2,363,'ρ₂ on [4, 7]',24,GOLD,'middle')
    c.line(xs[3],291,xs[3],327,GOLD,2,dash='4 4')
    c.line(xs[6],291,xs[6],327,GOLD,2,dash='4 4')
    c.line(xs[0],265,xs[-1],265,LINE,4)
    for i,x in enumerate(xs):
        c.node(x,265,'x'+str(i+1),TEAL if i==3 else (GOLD if 4<=i<=6 else MUTED),25)
    c.text(500,440,'⊗ combines local weights     ·     ⊕ aggregates assignments',23,INK,'middle')
    return figure(c,
        'Eight ordered variables carry overlapping constraints on segments two through four and four through seven; a semiring expression combines weights and aggregates over assignments.',
        'Two overlapping intervals illustrate generalized pattern constraints on consecutive variables. Semiring operations combine local weights and aggregate over assignments, providing a common language for partition-function computations and related optimization problems.',
        'https://arxiv.org/abs/2305.17526')


def build_figures():
    return {
        'minimum-cost-homomorphism': _minimum_cost(),
        'extensions-minimum-cost-homomorphism': _extensions(),
        'hybrid-csp-structural-restrictions': _structural(),
        'hybrid-vcsps': _lifted(),
        'induced-fixed-template-csps': _induced(),
        'csp-densification-sparsification': _densification(),
        'generalized-pattern-partition': _semiring(),
    }
