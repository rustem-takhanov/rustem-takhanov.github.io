#!/usr/bin/env python3
"""Build Rustem Takhanov's portable static academic website (Python standard library)."""
from pathlib import Path
from html import escape
from urllib.parse import quote
from collections import defaultdict
import json, math, shutil, zipfile, re
from illustrations import build_illustrations

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
PUBS=json.loads((ROOT/'content/publications.json').read_text(encoding='utf-8'))
GITHUB_SITE_URL=json.loads((ROOT/'content/site.json').read_text(encoding='utf-8'))['github_pages_url'].rstrip('/')+'/'
BY_SLUG={p['slug']:p for p in PUBS}
FIGURES=build_illustrations()
if set(FIGURES)!=set(BY_SLUG):
 raise ValueError('Every publication must have exactly one illustration: '+str(set(FIGURES)^set(BY_SLUG)))
E=escape
R='@ROOT@'

ICONS={
 'arrow':'<path d="M5 12h14m-5-5 5 5-5 5"/>',
 'external':'<path d="M14 4h6v6M20 4l-9 9M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/>',
 'back':'<path d="M19 12H5m5-5-5 5 5 5"/>',
 'mail':'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
 'pin':'<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/>',
 'scholar':'<path d="m2 9 10-5 10 5-10 5L2 9Zm4 2v6c4 3 8 3 12 0v-6m4-2v8"/>',
 'code':'<path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-14-2 16"/>',
 'building':'<path d="m3 7 9-5 9 5H3Zm0 14h18M6 10v8m6-8v8m6-8v8M3 18h18"/>',
 'file':'<path d="M14 2H5v20h14V7l-5-5Zm0 0v6h5M8 12h8m-8 4h8"/>',
 'key':'<circle cx="8" cy="9" r="4"/><path d="m11 12 8 8m-3-3 3-3m-6 0 3-3"/>',
 'search':'<circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6"/>',
 'play':'<path d="m9 5 11 7-11 7Z"/>',
 'close':'<path d="m6 6 12 12M6 18 18 6"/>'
}
def icon(name):return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'+ICONS.get(name,ICONS['external'])+'</svg>'
def internal(slug):return R+'publications/'+slug+'/'
def authors(p):return ', '.join('<strong>'+E(a)+'</strong>' if a=='Rustem Takhanov' else E(a) for a in p['authors'])
def external(url,label,cls='resource-link',ico='external',aria_label=None):
 return '<a class="'+cls+'" href="'+E(url,quote=True)+'"'+(' aria-label="'+E(aria_label,quote=True)+'"' if aria_label else '')+' target="_blank" rel="noopener noreferrer">'+E(label)+icon(ico)+'</a>'
def resource_links(p,detail=True):
 selected=[l for l in p['resources'] if l['label']!='arXiv'][:5]
 result=''.join(external(l['url'],l['label'],ico='code' if l['label']=='Code' else 'external') for l in selected)
 if detail:result+='<a class="resource-link detail" href="'+internal(p['slug'])+'">About this paper '+icon('arrow')+'</a>'
 return '<div class="resource-links">'+result+'</div>'
def paper_actions(p):
 return '<div class="paper-actions">'+''.join(external(l['url'],l['label'],'button primary' if i==0 else 'button','file' if i==0 else 'external') for i,l in enumerate(p['resources']))+'</div>'

def cell_svg():
 pts=[]
 for a in range(4):
  for s in [-1,1]:v=[0]*4;v[a]=s;pts.append(v)
 pts += [[.5 if (i>>k)&1 else -.5 for k in range(4)] for i in range(16)]
 edges=[(i,j) for i in range(24) for j in range(i) if abs(sum(x*y for x,y in zip(pts[i],pts[j]))-.5)<1e-9]
 assert len(edges)==96
 proj=[]
 for p in pts:
  v=p.copy()
  for a,b,t in [(0,3,.72),(1,2,.758),(0,2,.55),(1,3,.35)]:
   x,y=v[a],v[b];v[a]=x*math.cos(t)-y*math.sin(t);v[b]=x*math.sin(t)+y*math.cos(t)
  proj.append((110+98*v[0],110+98*v[1]))
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220"><title>Orthogonal projection of a regular 24-cell</title><circle cx="110" cy="110" r="98" fill="none" stroke="#cddcd1" stroke-width=".5"/>']
 for i,j in edges:
  x,y=proj[i];a,b=proj[j];svg.append(f'<path d="M{x:.3f} {y:.3f}L{a:.3f} {b:.3f}" stroke="#56806a" stroke-opacity=".42" stroke-width=".7"/>')
 for i,(x,y) in enumerate(proj):svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3" fill="'+('#af8854' if i<8 else '#2f6956')+'" stroke="#edf3ee" stroke-width=".9"/>')
 return ''.join(svg)+'</svg>'

def layout(body,path,title='Rustem Takhanov',active='',description=None):
 prefix='../'*(len(Path(path).parts)-1) or './'
 nav=''.join('<a href="'+R+route+'/"'+(' aria-current="page"' if active==route else '')+'>'+label+'</a>' for route,label in [('publications','Publications'),('talks','Talks'),('teaching','Teaching'),('miscellaneous','Miscellaneous'),('links','Links')])
 social=''.join('<a href="'+E(url,quote=True)+'"'+(' target="_blank" rel="noopener noreferrer"' if url.startswith('https') else '')+'>'+icon(ico)+label+'</a>' for ico,label,url in [
  ('mail','Email','mailto:rustem.takhanov@nu.edu.kz'),('scholar','Google Scholar','https://scholar.google.com/citations?user=DjIrpP8AAAAJ&hl=en'),('code','GitHub','https://github.com/k-nic'),('building','University profile','https://research.nu.edu.kz/en/persons/rustem-takhanov/')])
 description=description or 'Rustem Takhanov, Assistant Professor of Mathematics at Nazarbayev University. Research in machine learning, kernel methods, constraint satisfaction, and kissing arrangements.'
 doc='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#fbfaf7">
<title>'''+E(title)+'''</title><meta name="description" content="'''+E(description,quote=True)+'''"><meta property="og:title" content="'''+E(title,quote=True)+'''"><meta property="og:description" content="'''+E(description,quote=True)+'''"><meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="@ROOT@assets/favicon.svg"><link rel="stylesheet" href="@ROOT@assets/style.css"><script src="@ROOT@assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="header-inner"><a class="brand" href="@ROOT@" aria-label="Rustem Takhanov home"><span class="monogram">RT</span><span>Rustem Takhanov</span></a><nav class="nav" aria-label="Main navigation">'''+nav+'''</nav></div></header>
<div class="layout"><aside class="sidebar" aria-label="Profile"><img class="portrait" src="@ROOT@assets/portrait.jpg" width="142" height="142" alt="Rustem Takhanov"><h2 class="profile-name">Rustem Takhanov</h2><p class="profile-role"><strong>Assistant Professor</strong><br>Department of Mathematics<br>Nazarbayev University</p><p class="profile-location">'''+icon('pin')+'''Astana, Kazakhstan</p><div class="profile-links">'''+social+'''</div><div class="profile-note">Mathematics &amp; discovery</div></aside>
<main id="main">'''+body+'''</main></div><footer class="site-footer"><p><span class="footer-mark">RT</span> © 2026 Rustem Takhanov</p><p>Nazarbayev University · Astana, Kazakhstan &nbsp; / &nbsp; <a href="@ROOT@links/">Contact &amp; resources</a></p></footer></body></html>'''
 out=DIST/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(doc.replace(R,prefix), encoding='utf-8')

def recent_row(slug):
 p=BY_SLUG[slug]
 return '<article class="recent-row"><span class="recent-year">'+str(p['year'])+'</span><div><h3><a href="'+internal(slug)+'">'+E(p['title'])+'</a></h3><div class="recent-meta"><span>'+E(p['venue'])+'</span> &nbsp;·&nbsp; '+E(' · '.join(p['authors']))+'</div></div></article>'

def home():
 p=BY_SLUG['quaternionic-kissing']
 research=[('Machine learning theory','Other ML'),('Kissing arrangements & discrete geometry','Kissing numbers'),('Dimension reduction & PCA','Other ML'),('Constraint satisfaction & optimization','Constraint satisfaction'),('Kernel methods','Kernel methods'),('Conditional random fields & prediction','Language modeling')]
 return '''<section class="hero"><p class="eyebrow">Mathematics · Nazarbayev University</p><h1>Mathematics, computation<br>&amp; <em>machine learning.</em></h1><p class="intro">I am an Assistant Professor in the Department of Mathematics at <a href="https://nu.edu.kz/" target="_blank" rel="noopener noreferrer">Nazarbayev University</a> in Astana, Kazakhstan.</p><p class="intro">My research explores the mathematical foundations of learning and optimization, from kernel methods and dimension reduction to constraint satisfaction. My recent work also investigates kissing arrangements and the geometry of high-dimensional spaces.</p></section>
<section class="section" aria-labelledby="research-title"><div class="section-top"><h2 id="research-title">Research interests</h2></div><ul class="research-list">'''+''.join('<li><a href="'+R+'publications/?topic='+quote(topic)+'">'+E(label)+'</a></li>' for label,topic in research)+'''</ul></section>
<section class="section" aria-labelledby="recent-title"><div class="section-top"><h2 id="recent-title">Recent work</h2><a class="text-link" href="@ROOT@publications/">All publications '''+icon('arrow')+'''</a></div>
<article class="feature"><div><div class="feature-label">Featured research &nbsp; / &nbsp; 2026</div><h3><a href="'''+internal(p['slug'])+'">'+E(p['title'])+'''</a></h3><p>Three quaternionic factors offer a new perspective on kissing arrangements in twelve dimensions.</p><a class="text-link" href="'''+internal(p['slug'])+'">Explore the paper '+icon('arrow')+'''</a></div><figure class="feature-figure"><img src="@ROOT@assets/cell.svg" width="220" height="220" alt="A two-dimensional projection of a regular 24-cell"><figcaption>A 24-cell, projected</figcaption></figure></article>'''+recent_row('conditional-krr')+recent_row('intrinsic-dimensions')+'''</section>
<section class="section" aria-labelledby="education-title"><div class="section-top"><h2 id="education-title">Education</h2></div><div class="education-row"><div class="education-degree">Ph.D.</div><div><div class="education-title">Computer Science</div><div class="education-place">Dorodnitsyn Computing Center, Russian Academy of Sciences</div><p class="education-thesis">“Predicate description of supplementary constraints in pattern recognition problems”</p></div></div><div class="education-row"><div class="education-degree">M.A.</div><div><div class="education-title">Applied Mathematics and Physics</div><div class="education-place">Moscow Institute of Physics and Technology</div><p class="education-thesis">“Some estimations of generalization capabilities of learning algorithms”</p></div></div></section>'''

def pub_row(p):
 search=' '.join([p['title'],str(p['year']),p['venue'],p['topic'],p['summary'],*p['authors']]).lower()
 return '<article class="pub-row" data-topic="'+p['topic']+'" data-search="'+E(search,quote=True)+'"><div class="pub-topline"><span class="pub-topic">'+p['topic']+'</span><span>·</span><span>'+E(p['venue'])+'</span></div><h3><a href="'+internal(p['slug'])+'">'+E(p['title'])+'</a></h3><p class="authors">'+authors(p)+'</p><p class="pub-summary">'+E(p['summary'])+'</p>'+resource_links(p)+'</article>'

def publications():
 groups=defaultdict(list)
 for p in reversed(PUBS):groups[p['year']].append(p)
 return '''<header class="page-head"><p class="eyebrow">Research &amp; writing</p><h1>Publications</h1><p>Selected papers on kissing numbers, kernel methods, constraint satisfaction, language modeling, and other machine learning topics. Explore each paper for a short overview and accompanying resources.</p></header><div class="search-box">'''+icon('search')+'''<label class="sr-only" for="publication-search" style="position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)">Search publications</label><input id="publication-search" type="search" placeholder="Search by title, author, keyword, or year…" autocomplete="off"><button class="search-clear" aria-label="Clear search" hidden>'''+icon('close')+'''</button></div><div class="filter-line"><div class="filters" role="group" aria-label="Filter publications by topic">'''+''.join('<button class="filter" data-topic="'+t+'" aria-pressed="'+str(t=='All').lower()+'">'+label+'</button>' for t,label in [('All','All research'),('Kissing numbers','Kissing numbers'),('Kernel methods','Kernel methods'),('Constraint satisfaction','Constraint satisfaction'),('Language modeling','Language modeling'),('Other ML','Other ML')])+'''</div><span id="result-count" class="results-count" role="status" aria-live="polite">'''+str(len(PUBS))+''' publications</span></div><div id="publication-list">'''+''.join('<section class="year-group" aria-label="Publications from '+str(y)+'"><h2 class="year-heading">'+str(y)+'</h2>'+''.join(pub_row(p) for p in groups[y])+'</section>' for y in sorted(groups,reverse=True))+'''</div><div id="no-results" class="no-results" hidden><h2>No matching publications</h2><p>Try another title, author, or research topic.</p><button class="button" id="reset-filters">Clear all filters</button></div>'''

def video_block(p):
 return '<button class="video-cover" data-video="'+p['video']+'" data-title="'+E(p['title'],quote=True)+'"><span class="play-icon">'+icon('play')+'</span><strong>Watch the recorded presentation</strong><small>Load video from YouTube</small></button><p class="media-note">'+external('https://www.youtube.com/watch?v='+p['video'],'Open on YouTube instead')+'</p>'

def bibtex(p):
 # Minimal records deliberately omit unverified volume, pages, and DOI fields.
 venue=p['venue'];kind='misc' if venue in ['Preprint','Manuscript'] else ('inproceedings' if re.match(r'^(STACS|COCOON|ICML|ISAAC|SOFSEM|ICONIP|NAACL|EMNLP|COLING|UAI|AISTATS)',venue) else 'article')
 fields=[('title',p['title']),('author',' and '.join(', '.join(a.rsplit(' ',1)[::-1]) for a in p['authors'])),('year',str(p['year']))]
 if kind!='misc':fields.append(('booktitle' if kind=='inproceedings' else 'journal',venue))
 if p.get('arxiv'):
  fields+=[('eprint',p['arxiv']),('archivePrefix','arXiv')]
 fields.append(('url',p['resources'][0]['url']))
 return '@'+kind+'{takhanov'+str(p['year'])+p['slug'].replace('-','')+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields)+'\n}'

def paper_illustration(p):
 f=FIGURES[p['slug']]
 if 'plate' in f:return plate_html(f['plate'])
 src=R+'assets/papers/'+p['slug']+'.svg'
 return '<figure class="paper-visual"><a class="paper-visual-image" href="'+src+'" target="_blank" rel="noopener" aria-label="View full-size illustration for '+E(p['title'],quote=True)+'"><img src="'+src+'" width="1000" height="480" alt="'+E(f['alt'],quote=True)+'" decoding="async"></a><figcaption><div class="paper-visual-meta"><span>'+E(f['kind'])+'</span><a href="'+src+'" target="_blank" rel="noopener">View full size '+icon('external')+'</a></div><p>'+E(f['caption'])+' <a class="visual-source" href="'+E(f['source_url'],quote=True)+'" target="_blank" rel="noopener noreferrer">Research source '+icon('external')+'</a></p></figcaption></figure>'

def plate_image(fig,label,lazy=True):
 src=R+'assets/papers/'+fig['file']
 return '<a class="plate-image" href="'+src+'" target="_blank" rel="noopener" aria-label="View full size: '+E(label,quote=True)+'"><img src="'+src+'" width="'+str(fig['w'])+'" height="'+str(fig['h'])+'" alt="'+E(fig['alt'],quote=True)+'" decoding="async"'+(' loading="lazy"' if lazy else '')+'></a>'

def swatches(colours):
 return '<span class="plate-swatches" aria-hidden="true">'+''.join('<span class="sw" style="background:'+c+'"></span>' for c in colours)+'</span>'

def plate_html(pl):
 hero=pl['hero']
 full=R+'assets/papers/'+hero['file']
 h='<section class="plate" aria-labelledby="plate-title"><header class="plate-head"><p class="plate-eyebrow">'+E(pl['eyebrow'])+'</p><h2 class="plate-title" id="plate-title">'+E(pl['title'])+'</h2><p class="plate-lede">'+E(pl['lede'])+'</p></header>'
 h+='<figure class="plate-hero">'+plate_image(hero,pl['title'],lazy=False)+'<figcaption>'+E(hero['caption'])+' <a class="plate-link" href="'+full+'" target="_blank" rel="noopener">View full size'+icon('external')+'</a></figcaption></figure>'
 h+='<div class="plate-ledger'+(' cols-2' if len(pl['ledger'])==4 else '')+'">'+''.join('<div class="plate-part">'+swatches(part['swatches'])+'<div><h3>'+E(part['name'])+' <span class="num">'+E(part['count'])+'</span></h3><p>'+E(part['text'])+'</p></div></div>' for part in pl['ledger'])+'</div>'
 if pl.get('census'):
  c=pl['census'];total=sum(n for n,_,_ in c['parts'])
  h+='<figure class="plate-census"><figcaption>'+E(c['label'])+'</figcaption><div class="census-bar" role="img" aria-label="'+E(', '.join(str(n)+' '+name for n,_,name in c['parts']),quote=True)+'">'+''.join('<span style="flex:'+str(n)+' 1 0;background:'+col+'"></span>' for n,col,_ in c['parts'])+'</div><ul class="census-key">'+''.join('<li>'+swatches([col])+'<span class="num">'+'{:,}'.format(n)+'</span> '+E(name)+'</li>' for n,col,name in c['parts'])+'<li class="census-total"><span class="num">'+'{:,}'.format(total)+'</span> in all</li></ul></figure>'
 if pl.get('table'):
  t=pl['table']
  h+='<div class="plate-table-wrap"><table class="plate-table"><caption>'+E(t['caption'])+'</caption><thead><tr>'+''.join('<th scope="col"'+(' class="n"' if i in (1,2,3) else '')+'>'+E(x)+'</th>' for i,x in enumerate(t['head']))+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row" class="n">' if i==0 else '<td'+(' class="n"' if i in (1,2,3) else '')+'>')+E(x)+('</th>' if i==0 else '</td>') for i,x in enumerate(row))+'</tr>' for row in t['rows'])+'</tbody></table></div>'
 figs=''.join('<figure class="plate-fig"><h3>'+E(fig['title'])+'</h3>'+plate_image(fig,fig['title'])+'<figcaption>'+E(fig['caption'])+'</figcaption></figure>' for fig in pl['figs'])
 notes='<div class="plate-notes"><h3>Reading the drawings</h3><ul>'+''.join('<li><b>'+E(a)+'</b> '+E(b)+'</li>' for a,b in pl['notes'])+'</ul></div>'
 if len(pl['figs'])==1:h+='<div class="plate-figs single">'+figs+notes+'</div>'
 else:h+='<div class="plate-figs">'+figs+'</div>'+notes
 h+='<p class="plate-source">All drawings are original and computed from the definitions in the paper. <a class="visual-source" href="'+E(pl['source_url'],quote=True)+'" target="_blank" rel="noopener noreferrer">Research source '+icon('external')+'</a></p></section>'
 return h

def publication_detail(p):
 body='<a class="back-link" href="'+R+'publications/">'+icon('back')+' All publications</a><article><header class="article-head"><div class="article-meta"><span>'+str(p['year'])+'</span><span>·</span><span>'+E(p['venue'])+'</span><span class="tag">'+p['topic']+'</span></div><h1 class="article-title">'+E(p['title'])+'</h1><p class="authors">'+authors(p)+'</p>'+paper_actions(p)+'</header>'+paper_illustration(p)+'<section class="article-text"><h2>About this paper</h2><p class="lead">'+E(p['summary'])+'</p><p>'+E(p['detail'])+'</p></section>'
 if p.get('interactive'):
  body+='''<section class="article-section"><h2>A building block in four dimensions</h2><div class="geometry-panel"><div class="geometry-top"><strong>The regular 24-cell</strong><span>24 vertices &nbsp;·&nbsp; 96 edges</span></div><canvas id="cell-canvas" role="img" aria-label="An adjustable two-dimensional orthogonal projection of a regular 24-cell in four dimensions. Gold points are the eight signed coordinate vectors; green points are the sixteen half-integer vertices."></canvas><div class="geometry-controls"><label for="rotation">Rotation <input id="rotation" type="range" min="0" max="360" value="41" aria-label="Four-dimensional rotation in degrees"></label><button id="play-rotation" aria-pressed="false">Play</button><button id="reset-rotation">Reset</button></div></div><p class="geometry-caption">Rotate a 2D orthogonal projection of the 24-cell in ℝ⁴. Gold vertices are the eight signed coordinate vectors; green vertices are the sixteen vectors (±½, ±½, ±½, ±½). The projection illustrates one four-dimensional building block of the paper’s construction.</p></section>'''
 if p.get('video'):body+='<section class="article-section"><h2>Recorded presentation</h2>'+video_block(p)+'</section>'
 if p.get('poster'):body+='<section class="article-section"><h2>Poster &amp; presentation</h2><p class="article-text">The AISTATS poster and presentation slides are available in the resource links above.</p><details class="poster-details" data-src="https://drive.google.com/file/d/'+p['poster']+'/preview"><summary>Preview the research poster</summary></details><p class="media-note">The preview loads from Google Drive when opened.</p></section>'
 body+='<section class="article-section"><h2>Citation</h2><div class="citation"><div class="citation-head"><span>BibTeX</span><button class="copy-citation">Copy BibTeX</button></div><pre>'+E(bibtex(p))+'</pre><p class="citation-status" role="status" aria-live="polite"></p></div></section>'
 related=[q for q in reversed(PUBS) if q['topic']==p['topic'] and q['slug']!=p['slug']][:2]
 body+='<section class="article-section"><h2>Related work</h2><ul class="related-list">'+''.join('<li><a href="'+internal(q['slug'])+'">'+E(q['title'])+icon('arrow')+'</a></li>' for q in related)+'</ul></section></article>'
 return body

def talks():
 body='''<header class="page-head"><p class="eyebrow">Presentations &amp; discussion</p><h1>Talks</h1><p>Conference and seminar talks, posters, and recorded presentations.</p></header>'''
 for talk in json.loads((ROOT/'content/talks.json').read_text(encoding='utf-8')):
  url=talk.get('url') or 'https://www.youtube.com/watch?v='+talk['video']
  when=' · <time datetime="'+E(talk['date'],quote=True)+'">'+E(talk['date_label'])+'</time>' if talk.get('date') else ''
  actions=external(talk['venue_url'],talk.get('venue_label','Event page'),'button')
  if talk.get('video'):actions+=external('https://www.youtube.com/watch?v='+talk['video'],'Video','button')
  body+='<article class="talk-row" id="'+E(talk['slug'],quote=True)+'"><div class="talk-date">'+str(talk['year'])+'</div><div><div class="talk-venue"><a href="'+E(talk['venue_url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+E(talk['venue'])+'</a> · '+E(talk['type'])+when+'</div><h2><a href="'+E(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+E(talk['title'])+'</a></h2><p>'+E(talk['description'])+'</p><div class="paper-actions">'+actions+'</div>'
  if talk.get('video'):body+=video_block(talk)
  body+='</div></article>'
 for slug,desc in [('conditional-krr','Conference materials for work with Zhenisbek Assylbekov on conditional kernel ridge regression.'),('intrinsic-dimensions','A presentation on intrinsic dimension, kernel geometry, and learning guarantees. Slides and the research poster are available.'),('induced-fixed-template-csps','A recorded presentation on algebraic approaches to fixed-template constraint satisfaction problems.')]:
  p=BY_SLUG[slug]
  keep=['Video','Slides','Poster','ICML 2026']
  resources=[l for l in p['resources'] if l['label'] in keep]
  body+='<article class="talk-row"><div class="talk-date">'+str(p['year'])+'</div><div><div class="talk-venue">'+E(p['venue'])+'</div><h2><a href="'+internal(slug)+'">'+E(p['title'])+'</a></h2><p>'+desc+'</p><div class="paper-actions">'+''.join(external(l['url'],'Conference page' if l['label']=='ICML 2026' else l['label'],'button') for l in resources)+'<a class="button" href="'+internal(slug)+'">About the paper '+icon('arrow')+'</a></div>'
  if p.get('video'):body+=video_block(p)
  body+='</div></article>'
 return body

def link_row(label,description,url,ext=True):
 return '<a class="link-row" href="'+E(url,quote=True)+'"'+(' target="_blank" rel="noopener noreferrer"' if ext else '')+'><div><strong>'+E(label)+'</strong><p>'+E(description)+'</p></div>'+icon('external' if ext else 'arrow')+'</a>'

def links():
 return '''<header class="page-head"><p class="eyebrow">Elsewhere &amp; resources</p><h1>Links</h1><p>Research profiles, teaching materials, and useful resources.</p></header><section class="resource-group"><h2>Find me online</h2>'''+link_row('Google Scholar','Publications and citations.','https://scholar.google.com/citations?user=DjIrpP8AAAAJ&hl=en')+link_row('GitHub','Code, computational experiments, and research materials.','https://github.com/k-nic')+link_row('Nazarbayev University','My institutional profile and research activity.','https://research.nu.edu.kz/en/persons/rustem-takhanov/')+'''</section><section class="resource-group"><h2>Teaching</h2>'''+link_row('Course materials','Data Analysis and Statistical Learning; Optimization Methods and Techniques. Spring 2019.',R+'teaching/',False)+'''</section><section class="resource-group"><h2>On my reading list</h2>'''+link_row('Off the Convex Path','Perspectives on optimization and machine learning.','https://www.offconvex.org/')+link_row('Alpha Vantage','Financial market data and APIs.','https://www.alphavantage.co/')+link_row('Digital library genlibrusec','A digital library catalog.','http://gen.lib.rus.ec/')+'''</section><section class="resource-group"><h2>Get in touch</h2>'''+link_row('Email','rustem.takhanov@nu.edu.kz','mailto:rustem.takhanov@nu.edu.kz',False)+link_row('PGP public key','Public key for encrypted correspondence.','https://drive.google.com/file/d/1xEQizYiVIZcfARuZACGXgnUNblOkgNZV/view?usp=sharing')+'</section>'

def teaching():
 rows=json.loads((ROOT/'content/teaching.json').read_text(encoding='utf-8'))
 videos=json.loads((ROOT/'content/lecture_videos.json').read_text(encoding='utf-8'))
 body='''<header class="page-head"><p class="eyebrow">Lectures &amp; learning</p><h1>Teaching</h1><p>Recorded lectures and course materials on machine learning, mathematics, and optimization.</p></header><section class="recordings" aria-labelledby="recordings-title"><h2 id="recordings-title">Video recordings of online lectures <span class="heading-note">(given during COVID)</span></h2><p class="section-intro">Browse by topic. The recordings open on YouTube.</p><ol class="lecture-list">'''
 for n,topic in enumerate(videos,1):
  badge='<span class="language-badge">In '+E(topic['language'])+'</span>' if topic.get('language') else ''
  actions=''.join(external(v['url'],v['label'],'button lecture-button','play',v['label']+' — '+topic['title']+' (YouTube)') for v in topic['videos'])
  body+='<li class="lecture-row" id="'+E(topic['slug'],quote=True)+'"><span class="lecture-number" aria-hidden="true">'+f'{n:02d}'+'</span><div><div class="lecture-heading"><h3>'+E(topic['title'])+'</h3>'+badge+'</div><div class="lecture-actions">'+actions+'</div></div></li>'
 body+='''</ol></section><section class="section course-materials" aria-labelledby="course-materials-title"><div class="section-top"><h2 id="course-materials-title">Course materials</h2><span class="archive-term">Spring 2019</span></div><details class="course-archive"><summary>Data Analysis and Statistical Learning</summary><ul class="teaching-list">'''
 for row in rows:
  body+='<li><h3>'+E(row['title'])+'</h3><div class="resource-links">'+''.join(external(l['url'],l['label'].strip()) for l in row['links'])+'</div></li>'
 body+='</ul></details><details class="course-archive"><summary>Optimization Methods and Techniques</summary><ul class="syllabus">'
 topics=['Nonlinear programming: maxima and minima; first- and second-order conditions.','Numerical methods for unconstrained optimization: Newton and quasi-Newton methods.','Constrained optimization: optimality conditions for equality and inequality constraints.','Gradient projection, Lagrangian relaxation, and penalty methods.','Linear programming: polyhedra, extreme points, vertices, and basic feasible solutions.','The simplex method, sensitivity analysis, and strong and weak duality.','Network flows, the network simplex algorithm, maximum flows, assignment, and shortest paths.','Integer programming: exact and approximate methods, relaxation, and branch and bound.','Multi-objective optimization: partial orders, efficiency, scalarization, and applications.','Goal programming: principal results and applications.']
 return body+''.join('<li>'+E(t)+'</li>' for t in topics)+'</ul></details></section>'

def miscellaneous():
 items=json.loads((ROOT/'content/press.json').read_text(encoding='utf-8'))
 body='''<header class="page-head"><p class="eyebrow">Media &amp; interviews</p><h1>Miscellaneous</h1><p>News coverage and conversations about mathematics, research, and artificial intelligence.</p></header><section aria-labelledby="press-title"><h2 id="press-title">In Press</h2><p class="section-intro">Selected articles and interviews in the media.</p><ul class="press-list">'''
 for item in items:
  publisher='<span class="press-publisher"'+(' lang="'+E(item['publisher_lang'],quote=True)+'"' if item.get('publisher_lang') else '')+'>'+E(item['publisher'])+'</span>'
  body+='<li><article class="press-row"><div class="press-meta">'+publisher+'<time datetime="'+E(item['date'],quote=True)+'">'+E(item['date_label'])+'</time><span class="language-badge">'+E(item['language'])+'</span></div><h3 lang="'+E(item['lang'],quote=True)+'"><a href="'+E(item['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+E(item['title'])+' '+icon('external')+'</a></h3><p>'+E(item['description'])+'</p></article></li>'
 return body+'</ul></section>'

def main():
 # dist is generated output. Rebuild it so removed pages, old figures, and
 # temporary preview files cannot leak into the deployment or the ZIP.
 DIST.mkdir(exist_ok=True)
 for old in DIST.iterdir():
  if old.is_dir() and not old.is_symlink():shutil.rmtree(old)
  else:old.unlink()
 (DIST/'assets').mkdir()
 for f in (ROOT/'assets').iterdir():shutil.copy2(f,DIST/'assets'/f.name)
 (DIST/'assets/papers').mkdir(exist_ok=True)
 for slug,figure in FIGURES.items():
  if 'plate' in figure:
   for f in figure['files']:shutil.copy2(f,DIST/'assets/papers'/f.name)
  else:(DIST/'assets/papers'/f'{slug}.svg').write_text(figure['svg'], encoding='utf-8')
 (DIST/'assets/cell.svg').write_text(cell_svg(), encoding='utf-8')
 (DIST/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#246c67"/><text x="32" y="41" text-anchor="middle" fill="#fbfaf7" font-family="Georgia,serif" font-size="29">RT</text></svg>', encoding='utf-8')
 layout(home(),'index.html')
 layout(publications(),'publications/index.html','Publications — Rustem Takhanov','publications')
 layout(talks(),'talks/index.html','Talks — Rustem Takhanov','talks','Research talks, seminars, posters, and recorded presentations by Rustem Takhanov.')
 layout(links(),'links/index.html','Links — Rustem Takhanov','links')
 layout(teaching(),'teaching/index.html','Teaching — Rustem Takhanov','teaching','Online lecture recordings and course materials on autoencoders, low-rank optimization, structured prediction, and distances between distributions.')
 layout(miscellaneous(),'miscellaneous/index.html','Miscellaneous — Rustem Takhanov','miscellaneous','Press coverage and interviews with Rustem Takhanov about mathematics, kissing arrangements, and artificial intelligence.')
 for p in PUBS:layout(publication_detail(p),'publications/'+p['slug']+'/index.html',p['title']+' — Rustem Takhanov','publications',p['summary'])
 (DIST/'.nojekyll').touch()
 download=DIST/'downloads';download.mkdir(exist_ok=True)
 with zipfile.ZipFile(download/'rustem-takhanov-github-pages.zip','w',zipfile.ZIP_DEFLATED) as z:
  page_urls=[]
  for f in sorted(DIST.rglob('*')):
   relative=f.relative_to(DIST)
   if not f.is_file() or 'downloads' in relative.parts:continue
   if f.suffix=='.html':
    url=GITHUB_SITE_URL+relative.as_posix().removesuffix('index.html')
    page_urls.append(url)
    metadata='<link rel="canonical" href="'+E(url,quote=True)+'"><meta property="og:url" content="'+E(url,quote=True)+'">'
    z.writestr(relative.as_posix(),f.read_text(encoding='utf-8').replace('</head>',metadata+'</head>'))
   else:z.write(f,relative)
  z.writestr('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+E(url)+'</loc></url>\n' for url in page_urls)+'</urlset>\n')
  z.writestr('robots.txt','User-agent: *\nAllow: /\nDisallow: /_source/\n\nSitemap: '+GITHUB_SITE_URL+'sitemap.xml\n')
  for f in [ROOT/'build.py',ROOT/'README.md',ROOT/'SOURCE_NOTES.md',ROOT/'GITHUB_PAGES.md',*sorted((ROOT/'content').glob('*.json')),*sorted((ROOT/'assets').glob('*')),*sorted((ROOT/'illustrations').glob('*.py')),*sorted((ROOT/'illustrations/kissing_svg').glob('*.svg')),*sorted((ROOT/'tools/kissing_figures').glob('*.py')),*sorted((ROOT/'tools/kissing_figures').glob('*.md'))]:
   if f.exists():z.write(f,'_source/'+str(f.relative_to(ROOT)))
  z.writestr('README.md',(ROOT/'GITHUB_PAGES.md').read_text(encoding='utf-8'))
 print('Built',len(list(DIST.rglob('*.html'))),'HTML pages and GitHub Pages download.')

if __name__=='__main__':
 main()
