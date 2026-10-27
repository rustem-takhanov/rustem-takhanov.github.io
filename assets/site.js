'use strict';
(() => {
  const search=document.querySelector('#publication-search');
  if(search){
    let topic=new URLSearchParams(location.search).get('topic')||'All';
    const buttons=[...document.querySelectorAll('.filter')];
    if(!buttons.some(b=>b.dataset.topic===topic)) topic='All';
    search.value=new URLSearchParams(location.search).get('q')||'';
    const rows=[...document.querySelectorAll('.pub-row')];
    const clear=document.querySelector('.search-clear');
    function update(){
      const query=search.value.trim().toLocaleLowerCase();let count=0;
      rows.forEach(row=>{const match=(topic==='All'||row.dataset.topic===topic)&&row.dataset.search.includes(query);row.hidden=!match;if(match)count++});
      document.querySelectorAll('.year-group').forEach(group=>group.hidden=![...group.querySelectorAll('.pub-row')].some(r=>!r.hidden));
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.topic===topic)));
      document.querySelector('#result-count').textContent=count+' of '+rows.length+' publications';
      document.querySelector('#no-results').hidden=count!==0;clear.hidden=!query;
      const url=new URL(location.href);if(topic!=='All')url.searchParams.set('topic',topic);else url.searchParams.delete('topic');
      if(query)url.searchParams.set('q',search.value);else url.searchParams.delete('q');
      history.replaceState(null,'',url);
    }
    buttons.forEach(b=>b.addEventListener('click',()=>{topic=b.dataset.topic;update()}));
    search.addEventListener('input',update);
    clear.addEventListener('click',()=>{search.value='';update();search.focus()});
    document.querySelector('#reset-filters').addEventListener('click',()=>{topic='All';search.value='';update();search.focus()});
    update();
  }
  document.querySelectorAll('.copy-citation').forEach(button=>button.addEventListener('click',async()=>{
    const block=button.closest('.citation');const text=block.querySelector('pre').textContent;
    try{await navigator.clipboard.writeText(text);button.textContent='Copied';block.querySelector('.citation-status').textContent='Citation copied to clipboard.';setTimeout(()=>button.textContent='Copy BibTeX',2500)}
    catch(e){const selection=getSelection(),range=document.createRange();range.selectNodeContents(block.querySelector('pre'));selection.removeAllRanges();selection.addRange(range);block.querySelector('.citation-status').textContent='Citation selected. Press Ctrl+C or ⌘C to copy.'}
  }));
  document.querySelectorAll('[data-video]').forEach(button=>button.addEventListener('click',()=>{
    const frame=document.createElement('iframe');frame.className='video-embed';frame.src='https://www.youtube-nocookie.com/embed/'+button.dataset.video+'?autoplay=1';frame.title='Recorded presentation: '+button.dataset.title;frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';button.replaceWith(frame);
  }));
  document.querySelectorAll('.poster-details').forEach(details=>details.addEventListener('toggle',()=>{
    if(details.open&&!details.querySelector('iframe')){const frame=document.createElement('iframe');frame.src=details.dataset.src;frame.title='Research poster preview';frame.loading='lazy';details.append(frame)}
  }));
  const canvas=document.querySelector('#cell-canvas');
  if(canvas){
    const ctx=canvas.getContext('2d');const points=[];
    for(let axis=0;axis<4;axis++)for(const s of [-1,1]){const v=[0,0,0,0];v[axis]=s;points.push(v)}
    for(let i=0;i<16;i++)points.push([0,1,2,3].map(k=>((i>>k)&1)?0.5:-0.5));
    const edges=[];for(let i=0;i<24;i++)for(let j=0;j<i;j++)if(Math.abs(points[i].reduce((s,x,k)=>s+x*points[j][k],0)-0.5)<1e-8)edges.push([i,j]);
    let angle=0.72,playing=false,last=0,frameId=null;
    const slider=document.querySelector('#rotation');const play=document.querySelector('#play-rotation');
    function rot(v,i,j,a){const c=Math.cos(a),s=Math.sin(a),x=v[i],y=v[j];v[i]=x*c-y*s;v[j]=x*s+y*c}
    function draw(){
      const dpr=Math.min(devicePixelRatio||1,2),w=canvas.clientWidth,h=canvas.clientHeight;
      if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
      ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
      const scale=Math.min(w*.33,h*.38);
      const p=points.map((v,i)=>{v=[...v];rot(v,0,3,angle);rot(v,1,2,0.47+angle*.4);rot(v,0,2,.55);rot(v,1,3,.35);return{x:w/2+v[0]*scale,y:h/2+v[1]*scale,z:v[2],depth:v[3],i}});
      ctx.strokeStyle='rgba(66,108,87,.08)';ctx.lineWidth=1;ctx.beginPath();ctx.arc(w/2,h/2,scale,0,Math.PI*2);ctx.stroke();
      for(const [i,j] of edges){const alpha=.14+(p[i].depth+p[j].depth+2)*.08;ctx.strokeStyle='rgba(42,105,81,'+alpha+')';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(p[i].x,p[i].y);ctx.lineTo(p[j].x,p[j].y);ctx.stroke()}
      p.sort((a,b)=>a.depth-b.depth).forEach(v=>{ctx.beginPath();ctx.arc(v.x,v.y,3.1+(v.depth+1)*.8,0,Math.PI*2);ctx.fillStyle=v.i<8?'#b58a54':'#346e59';ctx.fill();ctx.strokeStyle='#edf3ee';ctx.lineWidth=1.3;ctx.stroke()});
    }
    function loop(t){if(!playing)return;if(last)angle+=Math.min(t-last,40)*.00017;last=t;slider.value=String(Math.round((angle%(Math.PI*2))/(Math.PI*2)*360));draw();frameId=requestAnimationFrame(loop)}
    function pause(){playing=false;last=0;if(frameId)cancelAnimationFrame(frameId);play.textContent='Play';play.setAttribute('aria-pressed','false')}
    slider.addEventListener('input',()=>{pause();angle=Number(slider.value)/360*Math.PI*2;draw()});
    play.addEventListener('click',()=>{if(playing){pause()}else{playing=true;play.textContent='Pause';play.setAttribute('aria-pressed','true');frameId=requestAnimationFrame(loop)}});
    document.querySelector('#reset-rotation').addEventListener('click',()=>{pause();angle=.72;slider.value=String(Math.round(angle/(Math.PI*2)*360));draw()});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});new ResizeObserver(draw).observe(canvas);draw();
  }
})();
