"""Small SVG drawing helpers for the site's original research illustrations."""
from html import escape
import math

INK = '#263f3b'
TEAL = '#246c67'
GOLD = '#b08a54'
BLUE = '#6987a0'
MUTED = '#74867d'
LINE = '#ccd7ce'
PALE = '#e2ebe3'
PAPER = '#f3f5ee'
WHITE = '#fdfdf8'
ROSE = '#b57569'

def fmt(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.') if isinstance(x, (int, float)) else str(x)

class Canvas:
    width = 1000
    height = 480

    def __init__(self, title, subtitle=None):
        self.title = title
        self.parts = [f'<rect width="1000" height="480" fill="{PAPER}"/>']
        if subtitle:
            self.text(44, 40, subtitle.upper(), 14, MUTED, weight=600, spacing='2')

    def raw(self, markup):
        self.parts.append(markup)

    def line(self, x1, y1, x2, y2, color=LINE, width=2, dash=None, opacity=1):
        self.parts.append(f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')

    def path(self, d, color=TEAL, width=3, fill='none', opacity=1, dash=None):
        self.parts.append(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')

    def polyline(self, points, color=TEAL, width=3, fill='none', opacity=1, dash=None):
        self.path('M'+' L'.join(f'{fmt(x)},{fmt(y)}' for x,y in points),color,width,fill,opacity,dash)

    def circle(self, x, y, r, fill=TEAL, stroke=None, width=2, opacity=1):
        self.parts.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}" opacity="{opacity}"/>')

    def rect(self, x, y, w, h, fill=WHITE, stroke=None, radius=8, width=2, opacity=1):
        self.parts.append(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}" opacity="{opacity}"/>')

    def text(self, x, y, text, size=22, color=INK, anchor='start', weight=400, family='Arial, sans-serif', spacing=None):
        self.parts.append(f'<text x="{fmt(x)}" y="{fmt(y)}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}"'+(f' letter-spacing="{spacing}"' if spacing else '')+'>'+escape(str(text))+'</text>')

    def arrow(self, x1, y1, x2, y2, color=TEAL, width=2.5, head=10, dash=None):
        self.line(x1,y1,x2,y2,color,width,dash)
        angle=math.atan2(y2-y1,x2-x1)
        points=[(x2-head*math.cos(angle-.45),y2-head*math.sin(angle-.45)),(x2,y2),(x2-head*math.cos(angle+.45),y2-head*math.sin(angle+.45))]
        self.polyline(points,color,width)

    def node(self, x, y, label=None, fill=TEAL, r=18, color=WHITE):
        self.circle(x,y,r,fill)
        if label is not None:self.text(x,y+7,label,20,color,'middle',600)

    def svg(self):
        return '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="480" viewBox="0 0 1000 480" role="img" aria-labelledby="title"><title id="title">'+escape(self.title)+'</title>'+''.join(self.parts)+'</svg>'

def figure(canvas, alt, caption, source_url, kind='Original conceptual illustration'):
    return {'svg':canvas.svg(), 'alt':alt, 'caption':caption, 'source_url':source_url, 'kind':kind}
