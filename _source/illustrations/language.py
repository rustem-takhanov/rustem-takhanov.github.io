"""Original, paper-specific diagrams for the language-modeling papers."""
from .common import Canvas, figure, TEAL, GOLD, BLUE, MUTED, LINE, PALE, PAPER, WHITE, INK, ROSE


def pattern_crf():
    c = Canvas('Repeated local patterns contribute to a sequence model', 'Pattern-based inference')
    xs = [108 + i * 112 for i in range(8)]
    for a, b in [(0, 2), (4, 6)]:
        c.rect(xs[a]-38, 210, xs[b]-xs[a]+76, 100, '#ece5d4', radius=18)
        c.path(f'M{xs[a]} 194 V168 H{xs[b]} V194', GOLD, 3)
        c.text((xs[a]+xs[b])/2, 145, 'A · B · A', 26, GOLD, 'middle', 600)
    for i in range(7):
        c.line(xs[i], 260, xs[i+1], 260, MUTED, 3)
    for i, char in enumerate('ABACABAC'):
        c.node(xs[i], 260, char, TEAL if char != 'C' else BLUE, 28)
        c.text(xs[i], 340, str(i+1), 20, MUTED, 'middle')
    c.text(500, 400, 'Local pattern costs → global sequence inference', 26, INK, 'middle')
    return figure(c,
        'A chain labeled A B A C A B A C highlights two occurrences of the pattern A B A.',
        'Repeated substrings contribute local costs to a sequence model. The highlighted occurrences illustrate the pattern structure used by algorithms for partition functions, marginals, MAP inference, and sampling; no fitted model is shown.',
        'https://arxiv.org/abs/1210.0508')


def grammar_crf():
    c = Canvas('A grammar tree and local sequence potentials act together', 'Local patterns + grammatical structure')
    root = (500, 102)
    mids = [(280, 205), (720, 205)]
    leaves = [(150, 340), (370, 340), (630, 340), (850, 340)]
    for x, y in mids:c.line(*root, x, y, TEAL, 3)
    for i, (x, y) in enumerate(leaves):c.line(*mids[i//2], x, y, TEAL, 3)
    c.node(*root, 'S', TEAL, 29)
    for label, xy in zip(['A', 'B'], mids):c.node(*xy, label, TEAL, 25)
    c.rect(331, 305, 338, 72, '#ece5d4', radius=15)
    for i in range(3):c.line(*leaves[i], *leaves[i+1], BLUE, 3)
    for label, xy in zip('abcd', leaves):c.node(*xy, label, BLUE, 24)
    c.path('M370 391 V410 H630 V391', GOLD, 3)
    c.text(500, 447, 'Local pattern', 23, GOLD, 'middle')
    c.text(95, 108, 'Long-range structure', 22, TEAL)
    return figure(c,
        'A branching parse tree joins a four-symbol sequence, with the central two-symbol pattern highlighted.',
        'The tree represents the non-local structure of a weighted context-free grammar, while the highlighted substring represents a local pattern potential. The paper combines these complementary interactions in a grammatical pattern-based CRF.',
        'https://arxiv.org/abs/1404.5475')


def patterns_characters():
    c = Canvas('Overlapping subword patterns become a word representation', 'Subwords as learned patterns')
    xs = [84+i*73 for i in range(8)]
    for x, char in zip(xs, 'learning'):
        c.rect(x, 98, 57, 64, WHITE, LINE, radius=9)
        c.text(x+28.5, 139, char, 30, INK, 'middle')
    patterns = [(0, 4, 205, 'learn', TEAL), (1, 3, 273, 'ear', BLUE), (5, 7, 341, 'ing', GOLD)]
    for start, end, y, label, col in patterns:
        left, right = xs[start], xs[end]+57
        c.rect(left, y-27, right-left, 52, col, radius=8)
        c.text((left+right)/2, y+8, label, 26, WHITE, 'middle', 600)
        c.arrow(right+9, y, 751, y, col, 2.5, 8)
    c.rect(773, 178, 156, 217, WHITE, LINE, radius=13)
    c.text(851, 219, 'Σ', 41, TEAL, 'middle', family='Georgia, serif')
    for i, h in enumerate([54, 90, 69, 105, 46, 76]):
        c.rect(796+i*19, 365-h, 12, h, [TEAL,BLUE,GOLD][i%3], radius=3)
    c.text(851, 432, 'Word vector', 22, INK, 'middle')
    c.text(84, 432, 'Illustrative overlapping patterns', 22, MUTED)
    return figure(c,
        'The word learning is split into characters, with overlapping patterns learn, ear, and ing feeding a summed word-vector representation.',
        'Overlapping subword patterns provide an alternative to individual characters. This schematic illustrates how pattern embeddings can be combined into a word representation; the example substrings are illustrative rather than extracted from a trained model.',
        'https://arxiv.org/abs/1709.00541')


def syllables():
    c = Canvas('Character and syllable segmentation offer two representations of one word', 'Two ways to represent a word')
    c.text(500, 108, 'banana', 48, INK, 'middle', family='Georgia, serif')
    c.arrow(430, 133, 267, 172, BLUE, 2.5)
    c.arrow(570, 133, 733, 172, GOLD, 2.5)
    c.text(265, 206, 'Characters', 24, BLUE, 'middle')
    c.text(735, 206, 'Syllables', 24, GOLD, 'middle')
    for i, char in enumerate('banana'):
        x = 78+i*63
        c.rect(x, 233, 53, 63, BLUE, radius=9)
        c.text(x+26.5, 274, char, 29, WHITE, 'middle')
    for i, token in enumerate(['ba','na','na']):
        x = 566+i*118
        c.rect(x, 233, 102, 63, GOLD, radius=9)
        c.text(x+51, 274, token, 29, WHITE, 'middle')
    for x, col in [(265,BLUE), (735,GOLD)]:
        c.arrow(x, 308, x, 350, col, 2.5)
        c.rect(x-164, 365, 328, 61, WHITE, LINE, radius=11)
        c.text(x, 404, 'Word-level prediction', 23, col, 'middle')
    return figure(c,
        'Banana is segmented either into six characters or into the three syllables ba, na, na, followed by word-level prediction.',
        'Character and syllable segmentation give different input units for predicting whole words. The paper compares their language-modeling quality and computational cost; the diagram illustrates the representation choice without displaying experimental measurements.',
        'https://aclanthology.org/D17-1199/')


def weight_reuse():
    c = Canvas('Input and output embedding models reuse consecutive lower layers', 'Sharing parameters from the bottom up')
    c.text(270, 98, 'Input representation', 24, INK, 'middle')
    c.text(730, 98, 'Output scoring', 24, INK, 'middle')
    stages = [(158, 'Upper layer', BLUE), (265, 'Composition', TEAL), (372, 'Subword embeddings', GOLD)]
    for y, label, col in stages:
        if y != 158:
            for x in [270,730]:c.arrow(x, y-40, x, y-67, col, 2.5, 8)
        for x in [270,730]:
            c.rect(x-153, y-32, 306, 65, WHITE, col, radius=10, width=2)
            c.text(x, y+8, label, 23, col, 'middle')
        if y != 158:
            c.line(437, y, 563, y, col, 3)
            c.rect(475, y-21, 50, 42, PAPER, radius=8)
            c.text(500, y+9, '=', 31, col, 'middle', 600)
    c.text(500, 220, 'tied', 22, MUTED, 'middle')
    c.text(500, 444, 'Reuse embeddings, then consecutive composition layers', 23, INK, 'middle')
    return figure(c,
        'Parallel input and output towers share subword embeddings and the next composition layer, while their upper layers remain separate.',
        'Shared subword embeddings and composition layers connect input representations with output scoring. The illustrated bottom-up tying pattern reflects the paper’s principle of reusing consecutive lower layers in a multilayer embedding model.',
        'https://aclanthology.org/N18-1128/')


def scrn():
    c = Canvas('Slow context states and fast hidden states unfold through a recurrent sequence', 'Two timescales of recurrent memory')
    xs = [250, 500, 750]
    c.text(65, 140, 'Slow', 23, GOLD)
    c.text(65, 167, 'context', 23, GOLD)
    c.text(65, 276, 'Fast', 23, TEAL)
    c.text(65, 303, 'hidden', 23, TEAL)
    for i, x in enumerate(xs):
        suffix = ['t−1', 't', 't+1'][i]
        if i < 2:
            c.arrow(x+48, 148, xs[i+1]-48, 148, GOLD, 4, 10)
            c.arrow(x+48, 284, xs[i+1]-48, 284, TEAL, 3, 10)
        c.arrow(x, 187, x, 244, GOLD, 2.5, 9)
        c.arrow(x, 370, x, 324, BLUE, 2.5, 9)
        c.path(f'M{x-25} 383 C{x-105} 368 {x-105} 177 {x-47} 155', BLUE, 2, dash='5 6')
        c.arrow(x-65, 166, x-47, 155, BLUE, 2, 7)
        c.rect(x-48, 109, 96, 78, '#eee5d2', GOLD, radius=14)
        c.text(x, 157, 's', 37, GOLD, 'middle', family='Georgia, serif')
        c.rect(x-48, 245, 96, 78, '#e1ebe2', TEAL, radius=14)
        c.text(x, 294, 'h', 37, TEAL, 'middle', family='Georgia, serif')
        c.text(x, 402, 'x('+suffix+')', 23, BLUE, 'middle')
    c.text(500, 453, 'Dropout · Variational dropout · Weight tying', 23, MUTED, 'middle')
    return figure(c,
        'Three time steps show a slowly changing context state s above a faster hidden state h, each driven by the input x.',
        'SCRN separates a slowly evolving context state from a faster hidden state. This simplified unrolling shows the two interacting memories; the paper investigates how dropout and parameter sharing affect the model’s performance.',
        'https://aclanthology.org/C18-1145.pdf')


def context_reflection():
    c = Canvas('A two-dimensional reflection preserves one coordinate and reverses the other', 'Geometry of word and context vectors')
    ox, oy = 296, 250
    c.circle(ox, oy, 166, WHITE, LINE, 1.5)
    c.line(82, oy, 513, oy, MUTED, 1.5)
    c.line(ox, 61, ox, 438, LINE, 1.5)
    points = [(129,-91),(-86,-133),(50,-141)]
    for i, (dx,dy) in enumerate(points):
        c.line(ox+dx, oy+dy, ox+dx, oy-dy, LINE, 1.5, '5 6')
        c.arrow(ox,oy,ox+dx,oy+dy,TEAL,3,10)
        c.arrow(ox,oy,ox+dx,oy-dy,GOLD,3,10)
        c.circle(ox+dx,oy+dy,4,TEAL)
        c.circle(ox+dx,oy-dy,4,GOLD)
    c.circle(ox,oy,5,INK)
    c.text(95, 91, 'Word vectors', 23, TEAL)
    c.text(95, 432, 'Context vectors', 23, GOLD)
    c.text(728, 145, 'c = Qw', 41, INK, 'middle', family='Georgia, serif')
    c.rect(623, 183, 89, 75, '#dce8df', radius=8)
    c.rect(722, 183, 89, 75, WHITE, radius=8)
    c.rect(623, 268, 89, 75, WHITE, radius=8)
    c.rect(722, 268, 89, 75, '#eee5d2', radius=8)
    for x,y,label,col in [(667,230,'+1',TEAL),(766,230,'0',MUTED),(667,315,'0',MUTED),(766,315,'−1',GOLD)]:
        c.text(x,y,label,31,col,'middle')
    c.text(728, 396, 'One coordinate reflected', 23, INK, 'middle')
    return figure(c,
        'Three word vectors above a horizontal axis reflect to context vectors below it, alongside a diagonal matrix with entries plus one and minus one.',
        'A two-dimensional example makes the reflection relation visible: one coordinate is preserved and the other changes sign. Under the paper’s assumptions, the analogous transformation reflects approximately half of the embedding dimensions.',
        'https://jair.org/index.php/jair/article/view/11368', 'Original mathematical illustration')


def build_figures():
    return {
        'pattern-based-crfs': pattern_crf(),
        'crfs-and-grammars': grammar_crf(),
        'patterns-versus-characters': patterns_characters(),
        'syllable-aware-language-models': syllables(),
        'reusing-subword-weights': weight_reuse(),
        'regularizing-scrn': scrn(),
        'context-and-word-vectors': context_reflection(),
    }
