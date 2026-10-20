from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const cs=[{id:'u_mon', kind:'monster', name:'Atacante Red', image:null, finish:'normal', monster:{attribute:'LUZ',race:'Guerrero',category:'Efecto',isExtra:false,level:4,atk:1600,def:1000,materials:'',effectText:'',trigger:'none'}},
   {id:'u_hole', kind:'trap', name:'Hoyo Red', image:null, finish:'normal', trap:{subtype:'Normal',cond:'Cuando tu oponente invoca un monstruo',effectText:'',func:'destroySummoned',value:0}}];
  cs.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    B.evaluate("(()=>{ duel.player.stZones=[{cardId:'u_hole',faceup:false,setThisTurn:false},null,null,null,null]; renderDuel(); })()"); B.wait_for_timeout(300)
    A.evaluate("(()=>{ duel.player.hand=['u_mon']; duel.player.monsterZones=[null,null,null,null,null]; renderDuel(); })()"); A.wait_for_timeout(800)
    A.evaluate("tryNormalSummon(0,'attack',true)"); A.wait_for_timeout(1500)
    opts=B.locator('.choice-btn').all_inner_texts()
    check('El rival recibe la opción de activar su Trampa', any('Hoyo Red' in o for o in opts), (opts, B.evaluate("duel.log.slice(0,5)")))
    if any('Hoyo Red' in o for o in opts): B.locator('.choice-btn', has_text='Hoyo Red').first.click()
    A.wait_for_timeout(2500)
    check('Tu monstruo se destruye en tu dispositivo', A.evaluate("duel.player.monsterZones.filter(Boolean).length")==0, A.evaluate("duel.log.slice(0,5)"))
    check('El rival lo ve destruido también', B.evaluate("duel.ai.monsterZones.filter(Boolean).length")==0)
    check('La Trampa del rival va a su Cementerio', B.evaluate("duel.player.gy.includes('u_hole')"))
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
