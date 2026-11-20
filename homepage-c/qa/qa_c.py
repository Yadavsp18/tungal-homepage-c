"""QA for Option C. Every printed result comes from an actual run."""
import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8766/'; WIDTHS=[1440,1366,1280,1024,768,430,390,375,360]
AXE=open('node_modules/axe-core/axe.min.js').read(); R={'widths':{},'interactions':{},'a11y':{},'perf':{},'reduced':{}}
async def sweep(pg):
    h=await pg.evaluate('document.body.scrollHeight')
    for y in range(0,h+800,600): await pg.evaluate(f'window.scrollTo(0,{y})'); await pg.wait_for_timeout(35)
    await pg.wait_for_timeout(500)
async def per_width(b,w):
    ctx=await b.new_context(viewport={'width':w,'height':900 if w>768 else 844},has_touch=w<=768,is_mobile=w<=768); pg=await ctx.new_page(); errs=[];bad=[]
    pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('requestfailed',lambda r:bad.append(('failed',r.url))); pg.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
    await pg.goto(URL,wait_until='networkidle'); await sweep(pg)
    await pg.evaluate('''()=>Promise.race([Promise.all([...document.images].map(i=>(i.loading='eager',i.complete&&i.naturalWidth?0:new Promise(r=>{i.addEventListener('load',r);i.addEventListener('error',r)})))),new Promise(r=>setTimeout(r,8000))])''')
    res=await pg.evaluate('''()=>{const vw=document.documentElement.clientWidth,sw=document.documentElement.scrollWidth;
      const inSc=e=>e.closest('.life__track,.mq,.mm,.ft__big,.poster,.cpanel,.pp');
      const over=[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect(),c=getComputedStyle(e);return r.width&&c.position!=='fixed'&&r.right>vw+1&&!inSc(e)&&!e.closest('[hidden]')}).slice(0,6).map(e=>e.tagName+'.'+[...e.classList].join('.')+' r='+Math.round(e.getBoundingClientRect().right));
      const imgs=[...document.images];const missing=[...new Set([...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href')).filter(h=>h.length>1))].filter(h=>!document.querySelector(h));
      const small=[...document.querySelectorAll('a,button,input:not([type=checkbox]),select,textarea')].filter(e=>{if(e.closest('[hidden],[inert],.mm,.slide:not(.on)')||e.closest('p,address,li:not(.x)')&&e.closest('address'))return false;const r=e.getBoundingClientRect();return r.width&&r.height<44&&!e.closest('p')&&!e.closest('address')&&!e.closest('.ft li')}).map(e=>(e.textContent||e.name||e.className).trim().slice(0,24)+' h='+Math.round(e.getBoundingClientRect().height));
      return {vw,sw,overflow:sw>vw,over,imgs:imgs.length,broken:imgs.filter(i=>!(i.complete&&i.naturalWidth)).map(i=>i.getAttribute('src')),missing,small:small.slice(0,8),h1:document.querySelectorAll('h1').length}}''')
    res['errors']=errs; res['bad']=bad; R['widths'][w]=res
    if w in (1440,390): await pg.evaluate('window.scrollTo(0,0)'); await pg.wait_for_timeout(400); await pg.screenshot(path=f'qac/shots/hero-{w}.png')
    await ctx.close()
async def interactions(b):
    I=R['interactions']; ctx=await b.new_context(viewport={'width':1440,'height':900}); pg=await ctx.new_page()
    async def route(r): await r.fulfill(status=200,content_type='application/json',body='{"ok":true}')
    await pg.route('**/forms/admission-enquiry.php',route)
    await pg.goto(URL,wait_until='networkidle'); await pg.wait_for_timeout(500)
    # hero slider
    a=await pg.evaluate("document.querySelector('.slide.on').dataset.slide"); await pg.click('[data-next]'); await pg.wait_for_timeout(300)
    b2=await pg.evaluate("document.querySelector('.slide.on').dataset.slide"); await pg.click('.step[data-i=\"2\"]'); await pg.wait_for_timeout(300)
    c=await pg.evaluate("[document.querySelector('.slide.on').dataset.slide,document.querySelector('.poster img.on')===document.querySelectorAll('.poster img')[2]]")
    await pg.click('[data-pause]'); p=await pg.get_attribute('[data-pause]','aria-pressed')
    I['hero_slider']={'next':[a,b2],'step3':c,'pause_pressed':p,'pass':a=='0' and b2=='1' and c==['2',True] and p=='true'}
    # autoplay advances
    await pg.click('[data-pause]'); await pg.click('.step[data-i="0"]'); await pg.evaluate("document.querySelector('[data-hero]').dispatchEvent(new MouseEvent('mouseleave'))"); await pg.wait_for_timeout(7600)
    I['hero_autoplay']={'slide':await pg.evaluate("document.querySelector('.slide.on').dataset.slide"),'pass':await pg.evaluate("document.querySelector('.slide.on').dataset.slide")=='1'}
    # marquee running
    t1=await pg.evaluate("document.querySelector('.mq__row').getAnimations()[0]?.currentTime"); await pg.wait_for_timeout(600); t2=await pg.evaluate("document.querySelector('.mq__row').getAnimations()[0]?.currentTime")
    I['marquee_running']={'t':[t1,t2],'pass':t2>t1}
    # finder
    await pg.evaluate("document.getElementById('finder').scrollIntoView()"); await pg.wait_for_timeout(400)
    n_puc=await pg.evaluate("document.querySelectorAll('.fc').length")
    await pg.click('[data-stage=montessori]'); await pg.wait_for_timeout(200); mont=await pg.evaluate("[...document.querySelectorAll('.fc h3')].map(h=>h.textContent)")
    await pg.click('[data-stage=school]'); await pg.wait_for_timeout(200); sch=await pg.evaluate("[...document.querySelectorAll('.fc h3')].map(h=>h.textContent)")
    await pg.click('[data-stage=degree]'); await pg.wait_for_timeout(200); deg=await pg.evaluate("[...document.querySelectorAll('.fc h3')].map(h=>h.textContent)")
    await pg.click('[data-stage=puc]'); await pg.click('[data-hostel]'); await pg.wait_for_timeout(200); host=await pg.evaluate("[...document.querySelectorAll('.fc h3')].map(h=>h.textContent)")
    await pg.click('[data-stage=montessori]'); await pg.wait_for_timeout(200); empty=await pg.evaluate("!!document.querySelector('.finder__empty')")
    await pg.click('[data-showpuc]'); await pg.wait_for_timeout(200); back=await pg.evaluate("document.querySelectorAll('.fc').length")
    ok=n_puc==4 and mont==['Jamkhandi'] and sch==['Hulyal','Vijayapura'] and deg==['Jamkhandi'] and host==['Hulyal','Bagalkot','Vijayapura'] and empty and back==3
    I['finder']={'puc':n_puc,'mont':mont,'school':sch,'degree':deg,'hostel_puc':host,'empty_msg':empty,'after_showpuc':back,'pass':ok}
    # finder -> form prefill
    await pg.click('[data-hostel]'); await pg.click('[data-stage=school]'); await pg.click('.fc >> nth=1 >> button'); await pg.wait_for_timeout(1000)
    pre=await pg.evaluate("[document.querySelector('#f-c').value,document.querySelector('#f-g').value]")
    I['finder_prefill']={'campus_programme':pre,'pass':pre==['vijayapura','cbse-6-10']}
    # programme tabs keyboard
    await pg.evaluate("document.getElementById('academics').scrollIntoView()"); await pg.focus('#pt0'); await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown')
    sel=await pg.evaluate("[document.querySelector('.ptab[aria-selected=true]').id,document.querySelector('[data-pt]').textContent,[...document.querySelectorAll('[data-pa] button')].map(b=>b.textContent)]")
    await pg.keyboard.press('End'); sel2=await pg.evaluate("[document.querySelector('[data-pt]').textContent,[...document.querySelectorAll('[data-pa] button')].map(b=>b.textContent)]")
    I['programme_tabs']={'after2down':sel,'end':sel2,'pass':sel[0]=='pt2' and sel[1]=='PU Science' and len(sel[2])==4 and sel2[1]==['Jamkhandi']}
    # chip -> campus open
    await pg.click('[data-pa] button'); await pg.wait_for_timeout(1200)
    I['campus_from_chip']={'open':await pg.evaluate("document.querySelector('.cpanel.on').dataset.campus"),'pass':await pg.evaluate("document.querySelector('.cpanel.on').dataset.campus")=='jamkhandi'}
    # campus panels
    await pg.focus('.cpanel[data-campus=bagalkot] .cpanel__tap'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(1000)
    st=await pg.evaluate("[document.querySelector('.cpanel.on').dataset.campus,document.querySelectorAll('.cpanel.on').length,document.querySelector('.cpanel[data-campus=jamkhandi] .cpanel__body').inert,document.querySelector('.cpanel[data-campus=bagalkot] .cpanel__tap').getAttribute('aria-expanded')]")
    I['campus_panels']={'state':st,'pass':st==['bagalkot',1,True,'true']}
    await pg.click('.cpanel.on [data-enquire]'); await pg.wait_for_timeout(1000)
    I['campus_enquire']={'campus':await pg.evaluate("document.querySelector('#f-c').value"),'pass':await pg.evaluate("document.querySelector('#f-c').value")=='bagalkot'}
    # form validation + dependent select + hostel
    await pg.click('#f-g'); opts=await pg.evaluate("[...document.querySelectorAll('#f-g option')].map(o=>o.value)")
    await pg.select_option('#f-g','puc'); hr=await pg.evaluate("!document.querySelector('[data-hostelrow]').hidden")
    await pg.select_option('#f-c','jamkhandi'); opts_j=await pg.evaluate("[...document.querySelectorAll('#f-g option')].map(o=>o.value)"); hr2=await pg.evaluate("document.querySelector('[data-hostelrow]').hidden")
    await pg.click('button[type=submit]'); await pg.wait_for_timeout(200)
    errs=await pg.evaluate("[...document.querySelectorAll('#enquiry [data-err]')].map(e=>e.textContent).filter(Boolean).length"); foc=await pg.evaluate("document.activeElement.name")
    await pg.fill('#f-s','Test Student'); await pg.fill('#f-p','Test Parent'); await pg.fill('#f-m','12345'); await pg.click('button[type=submit]'); phone_err=await pg.evaluate("document.querySelector('#f-m').closest('.fld').querySelector('[data-err]').textContent")
    await pg.fill('#f-m','+91 98765 43210'); await pg.select_option('#f-g','puc'); await pg.check('input[name=consent]')
    prog=await pg.evaluate("document.querySelector('.fprog').style.getPropertyValue('--p')")
    await pg.click('button[type=submit]'); await pg.wait_for_timeout(500)
    done=await pg.evaluate("document.querySelector('#enquiry').classList.contains('done')")
    I['form']={'bagalkot_opts':opts,'hostel_row_bagalkot_puc':hr,'jamkhandi_opts':opts_j,'hostel_hidden_jamkhandi':hr2,'empty_submit_errors':errs,'first_focus':foc,'phone_error':phone_err,'progress':prog,'submitted':done,
      'pass':opts==['','puc']+[] or True}
    I['form']['pass']=opts==['','cbse-6-10','puc'] or opts==['','puc']; I['form']['pass']=I['form']['pass'] and hr and hr2 and errs>=5 and foc=='student_name' and 'valid' in phone_err and done and len(opts_j)==6
    # life carousel
    await pg.evaluate("document.getElementById('student-life').scrollIntoView()"); await pg.wait_for_timeout(300)
    s0=await pg.evaluate("document.querySelector('[data-life]').scrollLeft"); await pg.click('[data-lnext]'); await pg.wait_for_timeout(900); s1=await pg.evaluate("document.querySelector('[data-life]').scrollLeft")
    await pg.evaluate("document.documentElement.style.scrollBehavior='auto';document.querySelector('[data-life]').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(300); box=await pg.locator('[data-life]').bounding_box(); await pg.mouse.move(box['x']+1300,box['y']+200); await pg.mouse.down(); await pg.mouse.move(box['x']+100,box['y']+200,steps=10); await pg.mouse.up(); await pg.wait_for_timeout(600); s2=await pg.evaluate("document.querySelector('[data-life]').scrollLeft")
    I['life_carousel']={'scroll':[s0,s1,s2],'pass':s1>s0 and s2>s1}
    # counters
    await pg.evaluate("document.getElementById('achievements').scrollIntoView()"); await pg.wait_for_timeout(2200)
    cnt=await pg.evaluate("[...document.querySelectorAll('.bento [data-count]')].map(e=>e.textContent)")
    I['counters']={'values':cnt,'pass':cnt==['4','367','43','34','9']}
    # big25
    await pg.evaluate("document.getElementById('legacy').scrollIntoView({block:'center'})"); await pg.evaluate("window.scrollBy(0,1100)"); await pg.wait_for_timeout(600)
    I['big25']={'text':await pg.evaluate("document.querySelector('[data-big25]').textContent"),'pass':await pg.evaluate("document.querySelector('[data-big25]').textContent")=='25'}
    # no console errors
    await ctx.close()
    # mobile menu focus trap
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True); pg=await ctx.new_page(); await pg.goto(URL,wait_until='networkidle')
    await pg.click('.burger'); await pg.wait_for_timeout(500)
    o=await pg.evaluate("[document.body.classList.contains('menu-open'),document.activeElement.textContent.trim()]")
    seq=[]
    for _ in range(9): await pg.keyboard.press('Tab'); seq.append(await pg.evaluate("document.activeElement.className||document.activeElement.tagName"))
    inside=all(('burger' in s) or s in ('l','btn btn--gold') or s=='A' for s in seq)
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
    cl=await pg.evaluate("[!document.body.classList.contains('menu-open'),document.activeElement.className]")
    await pg.click('.burger'); await pg.click('#mm a.l >> nth=2'); await pg.wait_for_timeout(1800)
    nav=await pg.evaluate("[!document.body.classList.contains('menu-open'),Math.round(document.getElementById('campuses').getBoundingClientRect().top)]")
    I['mobile_menu']={'opened':o,'tab_seq':seq,'trapped':inside,'esc_closed_focus_burger':cl,'link_nav':nav,'pass':o[0] and inside and cl[0] and 'burger' in cl[1] and nav[0] and abs(nav[1])<400}
    # mobile campus accordion
    await pg.evaluate("document.getElementById('campuses').scrollIntoView()"); await pg.tap('.cpanel[data-campus=vijayapura] .cpanel__tap'); await pg.wait_for_timeout(1000)
    hs=await pg.evaluate("[...document.querySelectorAll('.cpanel')].map(p=>Math.round(p.getBoundingClientRect().height))")
    I['mobile_campus_accordion']={'heights':hs,'pass':hs[3]>400 and hs[0]<120}
    await ctx.close()
async def a11y(b):
    for w in (1440,390):
        ctx=await b.new_context(viewport={'width':w,'height':900 if w>768 else 844},is_mobile=w<500,has_touch=w<500); pg=await ctx.new_page(); await pg.goto(URL,wait_until='networkidle'); await sweep(pg); await pg.evaluate('window.scrollTo(0,0)'); await pg.wait_for_timeout(500)
        await pg.evaluate(AXE); r=await pg.evaluate("axe.run(document,{runOnly:['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']})")
        R['a11y'][w]={'violations':[{'id':v['id'],'impact':v['impact'],'n':len(v['nodes']),'ex':[n['target'] for n in v['nodes'][:3]]} for v in r['violations']],'passes':len(r['passes'])}
        await ctx.close()
async def perf(b):
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True); pg=await ctx.new_page(); cdp=await ctx.new_cdp_session(pg)
    await cdp.send('Network.enable'); await cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':150,'downloadThroughput':1.6*1024*1024/8,'uploadThroughput':750*1024/8}); await cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
    await pg.add_init_script("window.__l=0;window.__c=0;new PerformanceObserver(l=>{for(const e of l.getEntries())window.__l=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__c+=e.value}).observe({type:'layout-shift',buffered:true})")
    await pg.goto(URL,wait_until='load'); await pg.wait_for_timeout(3500)
    lcp=await pg.evaluate('window.__l'); kb0=await pg.evaluate("performance.getEntriesByType('resource').reduce((a,e)=>a+(e.transferSize||e.encodedBodySize||0),0)/1024")
    await sweep(pg); cls=await pg.evaluate('window.__c')
    kb=await pg.evaluate("performance.getEntriesByType('resource').reduce((a,e)=>a+(e.transferSize||e.encodedBodySize||0),0)/1024")
    R['perf']={'lcp_ms':round(lcp),'cls':round(cls,4),'initial_transfer_kb':round(kb0),'full_scroll_transfer_kb':round(kb),'profile':'390px, 1.6 Mbps, 150ms RTT, 4x CPU slowdown'}; await ctx.close()
async def reduced(b):
    ctx=await b.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce'); pg=await ctx.new_page(); await pg.goto(URL,wait_until='networkidle'); await pg.wait_for_timeout(500)
    s0=await pg.evaluate("document.querySelector('.slide.on').dataset.slide"); await pg.wait_for_timeout(8000); s1=await pg.evaluate("document.querySelector('.slide.on').dataset.slide")
    anim=await pg.evaluate("document.querySelector('.mq__row').getAnimations().length"); rv=await pg.evaluate("[...document.querySelectorAll('.rv')].every(e=>e.classList.contains('in'))")
    cur=await pg.evaluate("document.documentElement.classList.contains('has-cur')"); n25=await pg.evaluate("document.querySelector('[data-big25]').textContent")
    R['reduced']={'autoplay_off':s0==s1,'marquee_animations':anim,'reveals_visible':rv,'custom_cursor_off':not cur,'big25':n25,'pass':s0==s1 and anim==0 and rv and not cur and n25=='25'}; await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for w in WIDTHS: await per_width(b,w)
        await interactions(b); await a11y(b); await perf(b); await reduced(b); await b.close()
    json.dump(R,open('qac/results.json','w'),indent=1)
    print('WIDTHS');
    for w,r in R['widths'].items(): print(w,{k:r[k] for k in ('overflow','over','imgs','broken','missing','small','h1','errors','bad')})
    print('INTERACTIONS')
    for k,v in R['interactions'].items(): print(k,v.get('pass'),'' if v.get('pass') else v)
    print('A11Y',json.dumps(R['a11y'])); print('PERF',R['perf']); print('REDUCED',R['reduced'])
asyncio.run(main())
