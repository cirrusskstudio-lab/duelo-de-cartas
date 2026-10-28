# Revivir en multijugador: con y sin respuesta del rival (antes fallaba dentro de la Cadena).
from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const cs=[
  {id:'r_reb', kind:'spell', name:'Renacido Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'reviveAny',value:0}},
  {id:'r_pre', kind:'spell', name:'Entierro Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'prematureBurial',value:0}},
  {id:'r_cgy', kind:'spell', name:'Llamado Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'specialFromGY',value:0}},
  {id:'r_jar', kind:'trap', name:'Jarra Red', image:null, finish:'normal', trap:{subtype:'Normal',cond:'En cualquier momento (libre)',effectText:'',func:'draw',value:1}},
  {id:'r_mon', kind:'monster', name:'Caído Red', image:null, finish:'normal', monster:{attribute:'LUZ',race:'Guerrero',category:'Normal',isExtra:false,level:4,atk:1700,def:1000,materials:'',effectText:'',trigger:'none'}}];
  cs.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def passAll(*pgs):
    for _ in range(3):
        for pg in pgs:
            for t in ('Pasar','No responder','No activar'):
                if pg.locator('.choice-btn', has_text=t).count(): pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(400)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    for card,label in (('r_reb','Renacido'),('r_pre','Entierro'),('r_cgy','Llamado')):
        for respond in (False, True):
            A.evaluate(f"(()=>{{ duel.player.hand=['{card}']; duel.player.gy=['r_mon']; duel.player.monsterZones=[null,null,null,null,null]; duel.player.stZones=[null,null,null,null,null]; duel.player.lp=8000; renderDuel(); }})()")
            B.evaluate(f"(()=>{{ duel.player.stZones=[{'{'}cardId:'r_jar',faceup:false,setThisTurn:false{'}'},null,null,null,null]; renderDuel(); }})()" if respond else "(()=>{ duel.player.stZones=[null,null,null,null,null]; renderDuel(); })()")
            A.wait_for_timeout(1200)
            A.evaluate("tryActivateFromHandSpell(0)"); A.wait_for_timeout(1500)
            if respond and B.locator('.choice-btn', has_text='Jarra Red').count(): B.locator('.choice-btn', has_text='Jarra Red').first.click(); B.wait_for_timeout(1200)
            passAll(A,B); A.wait_for_timeout(1500)
            for _ in range(2):
                if A.locator('.choice-btn', has_text='Caído Red').count(): A.locator('.choice-btn', has_text='Caído Red').first.click(); A.wait_for_timeout(1500)
                passAll(A,B)
            A.wait_for_timeout(2500)
            okA = A.evaluate("duel.player.monsterZones.some(z=>z&&z.cardId==='r_mon')")
            okB = B.evaluate("duel.ai.monsterZones.some(z=>z&&z.faceup&&findCardDef(z.cardId)&&findCardDef(z.cardId).name==='Caído Red')")
            check(f"{label} {'con' if respond else 'sin'} respuesta del rival: revive (y el rival lo ve)", okA and okB, [okA, okB, A.evaluate("duel.log.slice(0,5)"), A.dialogs[-2:]])
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
