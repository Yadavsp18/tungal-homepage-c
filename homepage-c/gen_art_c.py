# Option C art: all-new abstract generated imagery. No people, no reuse of earlier photos.
from PIL import Image, ImageDraw
import numpy as np, math, random, os
OUT='sitec/assets/art'; os.makedirs(OUT,exist_ok=True)
def H(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],float)
INK=H('#080B14'); INK2=H('#101631'); IRIS=H('#7C6CFF'); CORAL=H('#FF6B4A'); GOLD=H('#FFC857'); MINT=H('#4FE0C4'); ROSE=H('#FF8FB1'); SKY=H('#5CA8FF'); BONE=H('#F3EFE6')
SS=2
def base(W,H_,top,bot):
    y=np.linspace(0,1,H_)[:,None,None]
    return np.broadcast_to(top*(1-y)+bot*y,(H_,W,3)).copy()
def glow(a,cx,cy,r,col,k=1.0):
    h,w,_=a.shape; yy,xx=np.mgrid[0:h,0:w]
    g=np.exp(-(((xx-cx)**2+(yy-cy)**2)/(r*r))*1.5)*k
    a+=g[...,None]*col[None,None,:]
def gradimg(w,h,c1,c2,ang=90):
    t=math.radians(ang); yy,xx=np.mgrid[0:h,0:w]
    p=(xx/w*math.cos(t)+yy/h*math.sin(t)); p=(p-p.min())/(p.max()-p.min()+1e-9)
    arr=c1[None,None,:]*(1-p[...,None])+c2[None,None,:]*p[...,None]
    return Image.fromarray(np.clip(arr,0,255).astype('uint8')).convert('RGB')
class L:
    def __init__(s,W,Hh): s.W,s.H=W,Hh; s.im=Image.new('RGBA',(W*SS,Hh*SS),(0,0,0,0))
    def shape(s,fn,c1,c2=None,alpha=255,ang=90,outline=None,lw=2):
        m=Image.new('L',s.im.size,0); d=ImageDraw.Draw(m); fn(d,SS)
        if c2 is None: c2=c1
        g=gradimg(s.im.width,s.im.height,c1,c2,ang).convert('RGBA')
        mm=m.point(lambda v:int(v*alpha/255)); lay=Image.new('RGBA',s.im.size,(0,0,0,0)); lay.paste(g,(0,0),mm)
        s.im=Image.alpha_composite(s.im,lay)
    def line(s,fn,col,alpha=120,w=2):
        lay=Image.new('RGBA',s.im.size,(0,0,0,0)); d=ImageDraw.Draw(lay); fn(d,SS,tuple(int(c) for c in col)+(alpha,),w*SS)
        s.im=Image.alpha_composite(s.im,lay)
    def out(s): return s.im.resize((s.W,s.H),Image.LANCZOS)
def finish(a,lay,name,grain=3.2,q=74,vig=0.35):
    h,w,_=a.shape
    img=Image.fromarray(np.clip(a,0,255).astype('uint8')).convert('RGBA'); img=Image.alpha_composite(img,lay.out()).convert('RGB')
    arr=np.asarray(img).astype(float)
    yy,xx=np.mgrid[0:h,0:w]; v=1-vig*(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)/2; arr*=v[...,None]
    rng=np.random.default_rng(3); arr+=rng.normal(0,grain,(h,w,1))
    Image.fromarray(np.clip(arr,0,255).astype('uint8')).save(f'{OUT}/{name}.webp',quality=q,method=6)
def arch(d,S,x,y,w,h):  # y=top
    r=w/2; d.pieslice([x*S,y*S,(x+w)*S,(y+w)*S],180,360,fill=255); d.rectangle([x*S,(y+r)*S,(x+w)*S,(y+h)*S],fill=255)
def circ(d,S,cx,cy,r): d.ellipse([(cx-r)*S,(cy-r)*S,(cx+r)*S,(cy+r)*S],fill=255)

# ---------- scenes ----------
def scene_arches(W,Hh,pal,name,seed=1):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.35,W*.5,pal[2],.55); glow(a,W*.85,Hh*.9,W*.5,pal[3],.35)
    l=L(W,Hh); n=5; aw=W*.2; gap=W*.012; x0=(W-(n*aw+(n-1)*gap))/2
    cols=[(pal[2],pal[3]),(pal[3],pal[4]),(pal[4],pal[2]),(pal[2],pal[4]),(pal[3],pal[2])]
    for i in range(n):
        x=x0+i*(aw+gap); top=Hh*(.32+.05*abs(i-2)); hh=Hh*.92-top
        l.shape(lambda d,S,x=x,top=top,hh=hh:arch(d,S,x,top,aw,hh),*cols[i],alpha=235,ang=80)
        l.shape(lambda d,S,x=x,top=top,hh=hh:arch(d,S,x+aw*.18,top+aw*.18,aw*.64,hh-aw*.18),pal[0],pal[1],alpha=210,ang=90)
    l.shape(lambda d,S:circ(d,S,W*.5,Hh*.2,W*.07),pal[4],pal[3],alpha=255,ang=60)
    finish(a,l,name)
def scene_hills(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.55,W*.45,pal[4],.9); glow(a,W*.5,Hh*.5,W*.2,BONE,.25)
    l=L(W,Hh); l.shape(lambda d,S:circ(d,S,W*.5,Hh*.5,W*.15),pal[4],pal[3],ang=80)
    for i in range(6):
        yb=Hh*(.56+i*.075); amp=Hh*(.05+.012*i); ph=i*1.3; f=1.2+i*.25
        pts=[(x,yb+amp*math.sin(x/W*math.pi*2*f+ph)) for x in range(0,W+8,8)]
        c1=pal[2]*(1-i*.12)+INK*(i*.12); c2=pal[1]*(1-i*.1)
        l.shape(lambda d,S,pts=pts:d.polygon([(x*S,y*S) for x,y in pts]+[(W*S,Hh*S),(0,Hh*S)],fill=255),c1,c2,alpha=240,ang=90)
    finish(a,l,name)
def scene_terraces(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.78,Hh*.18,W*.4,pal[4],.7); glow(a,W*.2,Hh*.8,W*.5,pal[2],.45)
    l=L(W,Hh); n=7; sw=W/(n+1.6)
    for i in range(n):
        x=W*.06+i*sw*1.0; hgt=Hh*(.18+i*.095); y=Hh*.94-hgt
        c=(pal[2]*(1-i/n)+pal[3]*(i/n),pal[1]*0.6+pal[2]*0.2)
        l.shape(lambda d,S,x=x,y=y,hgt=hgt:d.rectangle([x*S,y*S,(x+sw*.92)*S,(y+hgt)*S],fill=255),*c,alpha=240,ang=90)
        l.line(lambda d,S,col,w,x=x,y=y:d.line([x*S,y*S,(x+sw*.92)*S,y*S],fill=col,width=w),BONE,160,2)
    l.shape(lambda d,S:circ(d,S,W*.06+7*sw+sw*.1,Hh*.94-Hh*(.18+7*.095)-W*.04,W*.03),pal[4],pal[3])
    finish(a,l,name)
def scene_ridges(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.75,Hh*.25,W*.4,pal[4],.8); glow(a,W*.2,Hh*.8,W*.5,pal[2],.4)
    l=L(W,Hh); rnd=random.Random(11)
    l.shape(lambda d,S:circ(d,S,W*.75,Hh*.27,W*.08),pal[4],pal[3],ang=70)
    for i in range(5):
        yb=Hh*(.5+i*.11); pts=[(0,yb)]; x=0
        while x<W:
            x+=W*rnd.uniform(.08,.17); pts.append((min(x,W),yb-Hh*rnd.uniform(.05,.2)+i*Hh*.01))
        l.shape(lambda d,S,pts=pts:d.polygon([(x*S,y*S) for x,y in pts]+[(W*S,Hh*S),(0,Hh*S)],fill=255),pal[2]*(1-i*.17)+pal[3]*(.2),pal[1],alpha=245,ang=90)
    finish(a,l,name)
def scene_dome(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.4,W*.5,pal[2],.6); glow(a,W*.5,Hh*.05,W*.3,pal[4],.5)
    l=L(W,Hh); cx=W*.5; r=W*.3; by=Hh*.72
    l.shape(lambda d,S:d.pieslice([(cx-r)*S,(by-r)*S,(cx+r)*S,(by+r)*S],180,360,fill=255),pal[3],pal[2],ang=70)
    for k in range(1,6):
        rr=r*(1-k*.15)
        l.line(lambda d,S,col,w,rr=rr:d.arc([(cx-rr)*S,(by-rr)*S,(cx+rr)*S,(by+rr)*S],180,360,fill=col,width=w),BONE,150,2)
    l.shape(lambda d,S:d.rectangle([(cx-r*1.15)*S,by*S,(cx+r*1.15)*S,Hh*S],fill=255),pal[2]*.35+INK*.65,pal[1],alpha=255)
    for s_ in (-1,1):
        px=cx+s_*r*1.45
        l.shape(lambda d,S,px=px:d.rectangle([(px-W*.018)*S,(by-Hh*.2)*S,(px+W*.018)*S,Hh*S],fill=255),pal[2],pal[1],alpha=235)
        l.shape(lambda d,S,px=px:d.pieslice([(px-W*.03)*S,(by-Hh*.2-W*.03)*S,(px+W*.03)*S,(by-Hh*.2+W*.03)*S],180,360,fill=255),pal[4],pal[3])
    l.shape(lambda d,S:circ(d,S,cx,by-r-W*.055,W*.018),pal[4],pal[4])
    finish(a,l,name)
def scene_rays(W,Hh,pal,name):  # 25 rays: academic excellence
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.7,W*.55,pal[2],.8); glow(a,W*.5,Hh*.7,W*.2,pal[4],.8)
    l=L(W,Hh); cx,cy=W*.5,Hh*.7
    for i in range(25):
        t=math.pi+(i/24)*math.pi; r1=W*.12; r2=W*(.30+.1*(math.sin(i*1.7)*.5+.5))
        w=W*.011
        def f(d,S,t=t,r1=r1,r2=r2,w=w):
            p=[(cx+math.cos(t)*r1,cy+math.sin(t)*r1),(cx+math.cos(t)*r2,cy+math.sin(t)*r2)]
            d.line([(p[0][0]*S,p[0][1]*S),(p[1][0]*S,p[1][1]*S)],fill=255,width=int(w*S))
        l.shape(f,pal[4],pal[3],alpha=235,ang=90)
    l.shape(lambda d,S:d.pieslice([(cx-W*.1)*S,(cy-W*.1)*S,(cx+W*.1)*S,(cy+W*.1)*S],180,360,fill=255),pal[4],pal[3])
    for k,w_ in enumerate((.38,.5,.62)):
        l.line(lambda d,S,col,w,w_=w_:d.arc([(cx-W*w_)*S,(cy-W*w_)*S,(cx+W*w_)*S,(cy+W*w_)*S],180,360,fill=col,width=w),BONE,70-k*15,2)
    l.shape(lambda d,S:d.rectangle([0,cy*S,W*S,Hh*S],fill=255),pal[2]*.3+INK*.7,pal[1],alpha=255)
    finish(a,l,name)
def scene_steps(W,Hh,pal,name):  # student development: rising steps + figure-less beacon
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.8,Hh*.2,W*.5,pal[4],.7); glow(a,W*.1,Hh*.9,W*.5,pal[2],.5)
    l=L(W,Hh); n=6
    for i in range(n):
        x=W*(.08+i*.145); hgt=Hh*(.12+i*.12); y=Hh*.95-hgt; w=W*.13
        l.shape(lambda d,S,x=x,y=y,hgt=hgt,w=w:d.rounded_rectangle([x*S,y*S,(x+w)*S,(y+hgt+60)*S],radius=int(w*.5*S),fill=255),pal[2]*(1-i*.07)+pal[3]*(i*.07),pal[1],alpha=240)
        l.shape(lambda d,S,x=x,y=y,w=w:circ(d,S,x+w/2,y+w*.5,w*.2),pal[4],pal[3] ,alpha=230)
    finish(a,l,name)
def scene_blocks(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.3,Hh*.3,W*.5,pal[2],.6); glow(a,W*.8,Hh*.8,W*.4,pal[3],.5)
    l=L(W,Hh)
    l.shape(lambda d,S:circ(d,S,W*.34,Hh*.38,W*.2),pal[3],pal[2],ang=60)
    l.shape(lambda d,S:d.rounded_rectangle([W*.44*S,Hh*.42*S,W*.84*S,Hh*.82*S],radius=int(W*.05*S),fill=255),pal[4],pal[3],ang=60,alpha=245)
    l.shape(lambda d,S:d.polygon([(W*.12*S,Hh*.86*S),(W*.46*S,Hh*.86*S),(W*.29*S,Hh*.56*S)],fill=255),pal[2],pal[1],ang=60,alpha=245)
    finish(a,l,name)
def scene_atom(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.5,W*.5,pal[2],.6)
    l=L(W,Hh); cx,cy=W*.5,Hh*.5
    for k in range(3):
        ang=k*60
        def f(d,S,col,w,ang=ang):
            pts=[]
            for i in range(0,361,3):
                t=math.radians(i); x=math.cos(t)*W*.36; y=math.sin(t)*W*.14
                ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang)); pts.append(((cx+x*ca-y*sa)*S,(cy+x*sa+y*ca)*S))
            d.line(pts,fill=col,width=w)
        l.line(f,[pal[4],pal[3],pal[2]][k],230,4)
    l.shape(lambda d,S:circ(d,S,cx,cy,W*.07),pal[4],pal[3])
    for k,(ang,t0) in enumerate(((0,40),(60,200),(120,320))):
        t=math.radians(t0); x=math.cos(t)*W*.36; y=math.sin(t)*W*.14; ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang))
        px,py=cx+x*ca-y*sa,cy+x*sa+y*ca
        l.shape(lambda d,S,px=px,py=py:circ(d,S,px,py,W*.032),BONE,pal[4])
    finish(a,l,name)
def scene_target(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.5,W*.5,pal[3],.55)
    l=L(W,Hh); cx,cy=W*.5,Hh*.52
    for i,(r,c1,c2) in enumerate(((.38,pal[2],pal[1]),(.29,pal[3],pal[2]),(.2,pal[4],pal[3]),(.1,BONE,pal[4]))):
        l.shape(lambda d,S,r=r:circ(d,S,cx,cy,W*r),c1,c2,ang=60,alpha=240)
    l.line(lambda d,S,col,w:d.line([W*.5*S,0,W*.5*S,Hh*S],fill=col,width=w),BONE,40,2)
    l.line(lambda d,S,col,w:d.line([0,cy*S,W*S,cy*S],fill=col,width=w),BONE,40,2)
    finish(a,l,name)
def scene_layers(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.3,W*.5,pal[2],.5)
    l=L(W,Hh)
    for i in range(5):
        y=Hh*(.2+i*.13); 
        l.shape(lambda d,S,y=y:d.polygon([(W*.5*S,y*S),(W*.9*S,(y+Hh*.12)*S),(W*.5*S,(y+Hh*.24)*S),(W*.1*S,(y+Hh*.12)*S)],fill=255),[pal[4],pal[3],pal[2],pal[3],pal[2]][i],pal[1],alpha=225-i*10,ang=70)
    finish(a,l,name)
def scene_desks(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.1,W*.6,pal[4],.5); glow(a,W*.2,Hh*.9,W*.4,pal[2],.5)
    l=L(W,Hh)
    for r in range(4):
        for c in range(3):
            x=W*(.12+c*.29); y=Hh*(.34+r*.15)
            l.shape(lambda d,S,x=x,y=y:d.rounded_rectangle([x*S,y*S,(x+W*.24)*S,(y+Hh*.08)*S],radius=int(12*S),fill=255),pal[2]*(1-r*.12)+pal[3]*r*.12,pal[1],alpha=235,ang=0)
    l.shape(lambda d,S:d.rounded_rectangle([W*.12*S,Hh*.12*S,W*.88*S,Hh*.26*S],radius=int(18*S),fill=255),pal[4],pal[3],ang=0,alpha=240)
    finish(a,l,name)
def scene_book(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.45,W*.55,pal[2],.6); glow(a,W*.5,Hh*.2,W*.25,pal[4],.5)
    l=L(W,Hh); cx=W*.5; top=Hh*.42; bot=Hh*.72
    l.shape(lambda d,S:d.polygon([(cx*S,(top+Hh*.04)*S),((cx-W*.4)*S,top*S),((cx-W*.4)*S,bot*S),(cx*S,(bot+Hh*.04)*S)],fill=255),pal[3],pal[2],alpha=240,ang=20)
    l.shape(lambda d,S:d.polygon([(cx*S,(top+Hh*.04)*S),((cx+W*.4)*S,top*S),((cx+W*.4)*S,bot*S),(cx*S,(bot+Hh*.04)*S)],fill=255),pal[2],pal[1],alpha=240,ang=160)
    for i in range(5):
        y=top+Hh*(.05+i*.045)
        for sgn in (-1,1):
            l.shape(lambda d,S,y=y,sgn=sgn,i=i:d.polygon([((cx+sgn*W*.04)*S,(y+Hh*.035)*S),((cx+sgn*W*.34)*S,(y-Hh*.005)*S),((cx+sgn*W*.34)*S,(y+Hh*.01)*S),((cx+sgn*W*.04)*S,(y+Hh*.05)*S)],fill=255),BONE,BONE,alpha=150 if i%2==0 else 90)
    for i,(dx,dy,r) in enumerate(((-.2,.2,.014),(.18,.15,.02),(.05,.08,.012),(-.06,.26,.01),(.28,.28,.012))):
        l.shape(lambda d,S,dx=dx,dy=dy,r=r:circ(d,S,cx+W*dx,Hh*dy,W*r),pal[4],pal[3])
    finish(a,l,name)
def scene_flask(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.55,W*.5,pal[2],.6)
    l=L(W,Hh); cx=W*.5
    l.shape(lambda d,S:d.polygon([((cx-W*.07)*S,Hh*.18*S),((cx+W*.07)*S,Hh*.18*S),((cx+W*.07)*S,Hh*.42*S),((cx+W*.27)*S,Hh*.78*S),((cx-W*.27)*S,Hh*.78*S),((cx-W*.07)*S,Hh*.42*S)],fill=255),BONE,pal[4],alpha=60,ang=90)
    l.shape(lambda d,S:d.polygon([((cx-W*.2)*S,Hh*.62*S),((cx+W*.2)*S,Hh*.62*S),((cx+W*.27)*S,Hh*.78*S),((cx-W*.27)*S,Hh*.78*S)],fill=255),pal[3],pal[2],alpha=245)
    for i,(dx,dy,r) in enumerate(((-.08,.5,.03),(.05,.44,.022),(.1,.35,.016),(-.02,.3,.012))):
        l.shape(lambda d,S,dx=dx,dy=dy,r=r:circ(d,S,cx+W*dx,Hh*dy,W*r),pal[4],pal[3])
    finish(a,l,name)
def scene_lanes(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.9,W*.7,pal[2],.6)
    l=L(W,Hh)
    for i in range(6):
        off=i*W*.12
        l.shape(lambda d,S,off=off:d.polygon([((W*.42+off*.08)*S,Hh*.1*S),((W*.5+off*.08)*S,Hh*.1*S),((W*.18+off)*S,Hh*S),((W*.06+off)*S,Hh*S)],fill=255),[pal[2],pal[3],pal[4]][i%3],pal[1],alpha=230,ang=90)
    l.shape(lambda d,S:circ(d,S,W*.7,Hh*.24,W*.07),pal[4],pal[3])
    finish(a,l,name)
def scene_waves(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.5,W*.6,pal[3],.5)
    l=L(W,Hh)
    for i in range(9):
        r=W*(.08+i*.075)
        l.line(lambda d,S,col,w,r=r:d.ellipse([(W*.5-r)*S,(Hh*.5-r)*S,(W*.5+r)*S,(Hh*.5+r)*S],outline=col,width=w),[pal[4],pal[3],pal[2]][i%3],200-i*14,3)
    for i in range(7):
        t=i*math.pi*2/7; l.shape(lambda d,S,t=t:circ(d,S,W*.5+math.cos(t)*W*.4,Hh*.5+math.sin(t)*W*.4*.9,W*.018),pal[4],pal[3])
    l.shape(lambda d,S:circ(d,S,W*.5,Hh*.5,W*.06),pal[4],pal[3])
    finish(a,l,name)
def scene_shelves(W,Hh,pal,name):
    a=base(W,Hh,pal[0],pal[1]); glow(a,W*.5,Hh*.2,W*.5,pal[4],.45)
    l=L(W,Hh); rnd=random.Random(5)
    for r in range(4):
        y=Hh*(.14+r*.21); x=W*.1
        while x<W*.88:
            w=W*rnd.uniform(.03,.06); h=Hh*rnd.uniform(.11,.17)
            c=rnd.choice([pal[2],pal[3],pal[4],BONE*.8])
            l.shape(lambda d,S,x=x,y=y,w=w,h=h:d.rectangle([x*S,(y+Hh*.18-h)*S,(x+w)*S,(y+Hh*.18)*S],fill=255),c,pal[1],alpha=235,ang=90); x+=w+W*.006
        l.shape(lambda d,S,y=y:d.rectangle([W*.08*S,(y+Hh*.18)*S,W*.92*S,(y+Hh*.19)*S],fill=255),BONE,BONE,alpha=120)
    finish(a,l,name)
def scene_poster(W,Hh,pal,name): scene_arches(W,Hh,pal,name)

P_IND=[INK,INK2,IRIS,CORAL,GOLD]
P_TEAL=[INK,H('#0B2430'),MINT,SKY,GOLD]
P_ROSE=[INK,H('#1B1030'),IRIS,ROSE,GOLD]
P_SUN=[INK,H('#220F1F'),CORAL,ROSE,GOLD]
P_SKY=[INK,H('#0C1A33'),SKY,IRIS,MINT]
if __name__=='__main__':
    # hero posters 1000x1250
    scene_rays(1000,1250,P_IND,'hero-1'); scene_steps(1000,1250,P_TEAL,'hero-2'); scene_arches(1000,1250,P_ROSE,'hero-3')
    # campuses 1200x900
    scene_arches(1200,900,P_IND,'campus-jamkhandi'); scene_hills(1200,900,P_SUN,'campus-hulyal')
    scene_ridges(1200,900,P_TEAL,'campus-bagalkot'); scene_dome(1200,900,P_ROSE,'campus-vijayapura')
    # programmes 800x800
    scene_blocks(800,800,P_SUN,'prog-montessori'); scene_book(800,800,P_SKY,'prog-school')
    scene_atom(800,800,P_IND,'prog-pu'); scene_target(800,800,P_ROSE,'prog-competitive'); scene_layers(800,800,P_TEAL,'prog-ug')
    # life 900x1100
    scene_book(900,1100,P_IND,'life-classroom'); scene_flask(900,1100,P_TEAL,'life-science'); scene_lanes(900,1100,P_SUN,'life-sports')
    scene_waves(900,1100,P_ROSE,'life-culture'); scene_shelves(900,1100,P_SKY,'life-library'); scene_arches(900,1100,P_TEAL,'life-campus')
    # social/OG
    scene_rays(1200,630,P_IND,'og')
    print(len(os.listdir(OUT)),'images')
