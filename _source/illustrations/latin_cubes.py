"""Exact combinatorial schematic for the Latin-cube construction in R16."""
from .common import Canvas, figure, INK, TEAL, GOLD, BLUE, ROSE, MUTED, LINE, WHITE


def build_figures():
    c = Canvas('Latin cubes and four quaternionic blocks give 4320-point kissing arrangements',
               'Latin cubes · quaternionic geometry')
    c.text(44, 79, 'A family of 4,320-point arrangements in ℝ¹⁶', 29, INK,
           family='Georgia, serif')
    c.rect(44, 106, 382, 226, WHITE, LINE, radius=10, width=1)
    c.text(235, 137, 'One Latin cube, four slices', 22, TEAL, 'middle')
    colours = [TEAL, GOLD, BLUE, ROSE]
    for layer in range(4):
        x = 66 + layer*88
        for row in range(4):
            for col in range(4):
                value = row ^ col ^ layer
                c.rect(x+col*18, 167+row*18, 17, 17, colours[value],
                       radius=2, opacity=.19)
                c.text(x+col*18+8.5, 167+row*18+12.8, value, 12, INK, 'middle')
        c.text(x+35, 264, 'c = '+str(layer), 16, MUTED, 'middle')
    c.text(235, 299, 'Example: F(a, b, c) = a ⊕ b ⊕ c', 17, INK, 'middle')

    c.text(523, 171, 'Choose', 16, MUTED, 'middle')
    c.text(523, 198, '3 Latin cubes', 19, TEAL, 'middle', 600)
    c.arrow(451, 223, 596, 223, TEAL, 2)
    c.text(523, 255, '6 permutations', 18, GOLD, 'middle', 600)
    c.text(523, 279, 'of the 3 levels', 16, MUTED, 'middle')

    vertices = [(686, 158), (873, 158), (686, 266), (873, 266)]
    for i, (x, y) in enumerate(vertices):
        for a, b in vertices[:i]:
            c.line(x, y, a, b, GOLD, 2, opacity=.65)
    for label, (x, y) in zip(['ℍ₀', 'ℍ₁', 'ℍ₂', 'ℍ₃'], vertices):
        c.rect(x-27, y-23, 54, 46, WHITE, TEAL, radius=9, width=1.6)
        c.text(x, y+8, label, 25, TEAL, 'middle', family='Georgia, serif')
    c.text(779, 315, 'Four quaternionic blocks: ℍ⁴ ≅ ℝ¹⁶', 18, INK, 'middle')

    for x, width, number, label, colour in [
        (44, 170, '96', 'AXIAL POINTS', TEAL),
        (251, 190, '1,152', 'TWO BLOCKS', GOLD),
        (478, 201, '3,072', 'FOUR BLOCKS', BLUE),
        (730, 226, '4,320', 'UNIT VECTORS', TEAL),
    ]:
        c.rect(x, 354, width, 84, WHITE, LINE, radius=7, width=1)
        c.text(x+width/2, 377, label, 12, MUTED, 'middle', 600, spacing='1')
        c.text(x+width/2, 418, number, 31, colour, 'middle', family='Georgia, serif')
    for x, symbol in [(232, '+'), (459, '+'), (705, '=')]:
        c.text(x, 409, symbol, 27, MUTED, 'middle')
    c.text(500, 467, '4,072,728,621 isometry classes · all infinitesimally jammed',
           19, TEAL, 'middle')
    return {'latin-cubes-4320': figure(c,
        'Four coloured slices of the Latin cube F(a,b,c)=a XOR b XOR c, alongside four '
        'quaternionic blocks with six pairwise links. The point count is 96 axial plus '
        '1152 two-block plus 3072 four-block vectors, totalling 4320.',
        'The grids show a sample order-4 Latin cube over the Klein four-group; ⊕ denotes '
        'bitwise XOR. Three independently chosen Latin cubes determine the four-block '
        'layers, while six permutations match levels between pairs of quaternionic '
        'blocks. This is a schematic of the construction, not a projection of its points.',
        'https://arxiv.org/abs/2611.00927', 'Original mathematical schematic')}
