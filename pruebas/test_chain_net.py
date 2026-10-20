from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const T=(id,name,func)=>({id, kind:'trap', name, image:null, finish:'normal', trap:{subtype:'Normal',cond:'',effectText:'',func,value:0}});
  const M=(id,name,atk)=>({id, kind:'monster', name, image:null, finish:'normal', monster:{attribute:'LUZ',race:'Guerrero',category:'Efecto',isExtra:false,pendulum:false,level:3,atk,def:1000,materials:'',effectText:'',trigger:'none'}});
  const sg=Object.assign(M('u_sang','Sangan',1000),{gyEffect:{trigger:'onSend', effect:'draw', value:1, targetCardId:null, restriction:'none', restrictionPhase:'Main1', condition:'', cost:'none', costLp:0}});
  [T('u_sak','Sakuretsu','destroyAttacker'), T('u_none','Trampa narrativa','none'), sg].forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def crit(pg, text, timeout=8000):
    pg.wait_for_selector(f'.critical-decision .choice-btn:has-text("{text}")', timeout=timeout)
    pg.locator('.critical-decision .choice-btn', has_text=text).first.click(); pg.wait_for_timeout(400)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    A.evaluate("""(()=>{ const z=emptyMonsterState('u_cab','attack',true); z.summonedThisTurn=false; duel.player.monsterZones=[z,null,null,null,null];
       duel.player.stZones=[{cardId:'u_none',faceup:false,setThisTurn:false},null,null,null,null]; renderDuel(); })()""")
    B.evaluate("""(()=>{ const z=emptyMonsterState('u_sol','attack',true); z.summonedThisTurn=false; duel.player.monsterZones=[z,null,null,null,null];
       duel.player.stZones=[{cardId:'u_sak',faceup:false,setThisTurn:false},null,null,null,null]; renderDuel(); })()""")
    A.wait_for_timeout(1200)
    A.evaluate("(()=>{ duel.phase='Battle'; netSend({type:'phase', phase:'Battle', turn:duel.turn}); renderDuel(); })()"); A.wait_for_timeout(500)
    A.evaluate("tryAttack(duel.player, 0)"); A.wait_for_timeout(200)
    A.locator('.choice-btn', has_text='Atacar a').first.click()
    crit(B, 'Activar Sakuretsu')
    A.wait_for_selector('.critical-decision .choice-btn:has-text("Pasar")', timeout=8000)
    s = B.evaluate("[duel.player.lp, !!duel.player.monsterZones[0], !!duel.ai.monsterZones[0]]")
    check('Red: el atacante puede responder a mi Trampa (le aparece la Cadena)', True)
    check('Red: mientras el atacante decide, ni la Trampa ni la batalla se resolvieron', s==[8000, True, True], s)
    A.wait_for_timeout(2500)
    s = B.evaluate("[duel.player.lp, !!duel.player.monsterZones[0], !!duel.ai.monsterZones[0]]")
    check('Red: sigue esperando aunque el atacante tarde', s==[8000, True, True], s)
    crit(A, 'Pasar')
    A.wait_for_timeout(2500)
    sa = A.evaluate("[duel.player.lp, !!duel.player.monsterZones[0], !!duel.ai.monsterZones[0], netState.awaitingAttack, duel.chainLinks.length]")
    sb = B.evaluate("[duel.player.lp, !!duel.player.monsterZones[0], !!duel.ai.monsterZones[0], duel.chainLinks.length]")
    check('Red: Sakuretsu destruye al atacante (en mi lado)', sb==[8000, True, False, 0], [sb, B.evaluate('duel.log.slice(0,8)')])
    check('Red: el atacante también lo ve y queda libre para seguir', sa==[8000, False, True, False, 0], [sa, A.evaluate('duel.log.slice(0,8)')])
    # Batalla normal en red sin trampas + Sangan en el Cementerio
    A.evaluate("""(()=>{ const z=emptyMonsterState('u_cab','attack',true); z.summonedThisTurn=false; duel.player.monsterZones=[z,null,null,null,null]; renderDuel(); })()""")
    B.evaluate("""(()=>{ const z=emptyMonsterState('u_sang','attack',true); z.summonedThisTurn=false; duel.player.monsterZones=[z,null,null,null,null]; duel.player.stZones=[null,null,null,null,null]; renderDuel(); })()""")
    A.wait_for_timeout(1200)
    hb = B.evaluate("duel.player.hand.length")
    A.evaluate("tryAttack(duel.player, 0)"); A.wait_for_timeout(200)
    A.locator('.choice-btn', has_text='Atacar a').first.click()
    crit(B, 'Activar el efecto')
    B.wait_for_timeout(800)
    check('Red: Sangan destruido en batalla ofrece su efecto y roba', B.evaluate("duel.player.hand.length")==hb+1, B.evaluate("duel.log.slice(0,6)"))
    check('Red: daño correcto (-500)', B.evaluate("duel.player.lp")==7500 and A.evaluate("duel.ai.lp")==7500)
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
