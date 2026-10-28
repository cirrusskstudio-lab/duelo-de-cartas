# Espadas Reveladoras, Jabalina Encantada y Cambio de Objetivo entre dos dispositivos.
from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const M=(id,n,atk,df)=>({id, kind:'monster', name:n, image:null, finish:'normal', monster:{attribute:'LUZ',race:'Guerrero',category:'Normal',isExtra:false,level:4,atk,def:df,materials:'',effectText:'',trigger:'none'}});
  const cs=[M('e_big','Gigante Red',2600,1000), M('e_low','Bajito Red',800,800), M('e_wall','Muro Red',0,2600),
  {id:'e_sw', kind:'spell', name:'Espadas Red', image:null, finish:'normal', spell:{subtype:'Continua',effectText:'',func:'none',value:0,swords:{enabled:true,turns:3}}},
  {id:'e_harp', kind:'spell', name:'Plumero Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'destroyAllOppST',value:0}},
  {id:'e_jav', kind:'trap', name:'Jabalina Red', image:null, finish:'normal', trap:{subtype:'Normal',cond:'Cuando tu oponente declara un ataque',effectText:'',func:'enchantedJavelin',value:0}},
  {id:'e_shift', kind:'trap', name:'Cambio Red', image:null, finish:'normal', trap:{subtype:'Normal',cond:'Cuando tu oponente declara un ataque',effectText:'',func:'shiftTarget',value:0}}];
  cs.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def passAll(*pgs):
    for _ in range(3):
        for pg in pgs:
            for t in ('Pasar','No responder','No activar'):
                if pg.locator('.choice-btn', has_text=t).count(): pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(400)
Z="{cardId:'%s',position:'%s',faceup:%s,atkMod:0,defMod:0,summonedThisTurn:false,attackedThisTurn:false}"
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    B.evaluate("(()=>{ duel.player.monsterZones=["+(Z%('e_big','defense','false'))+",null,null,null,null]; duel.player.stZones=[null,null,null,null,null]; renderDuel(); })()"); B.wait_for_timeout(1200)
    A.evaluate("(()=>{ duel.player.hand=['e_sw']; duel.player.stZones=[null,null,null,null,null]; duel.player.monsterZones=[null,null,null,null,null]; renderDuel(); })()"); A.wait_for_timeout(1000)
    A.evaluate("tryActivateFromHandSpell(0)"); A.wait_for_timeout(1500); passAll(B,A); A.wait_for_timeout(3000)
    check('Espadas: el monstruo boca abajo de B queda boca arriba en el celular de B', B.evaluate("duel.player.monsterZones[0].faceup"))
    check('Espadas: B está bloqueado 3 turnos (lo ve en su celular)', B.evaluate("swordsLockOn(duel.player)")==3, B.evaluate("swordsLockOn(duel.player)"))
    # turno de B
    A.evaluate("duel.player.hand=[]; renderDuel(); jumpToEndPhase(); advancePhase()"); A.wait_for_timeout(3000)
    B.evaluate("duel.phase='Battle'; renderDuel()"); B.evaluate("duel.player.monsterZones[0].position='attack'; tryAttack(duel.player,0)"); B.wait_for_timeout(500)
    check('Espadas: B no puede atacar en su turno', any('Espadas' in d for d in B.dialogs[-2:]), B.dialogs[-2:])
    B.evaluate("document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); }); duel.player.hand=[]; renderDuel(); jumpToEndPhase(); advancePhase()"); B.wait_for_timeout(3500)
    check('Espadas: al terminar el turno de B quedan 2 (en ambos celulares)', A.evaluate("duel.player.stZones.find(z=>z&&z.cardId==='e_sw').swordsTurns")==2 and B.evaluate("swordsLockOn(duel.player)")==2,
          [A.evaluate("JSON.stringify(duel.player.stZones)"), B.evaluate("swordsLockOn(duel.player)")])
    # turno de A otra vez -> pasa a B; B destruye las Espadas con el Plumero
    A.evaluate("duel.player.hand=[]; renderDuel(); jumpToEndPhase(); advancePhase()"); A.wait_for_timeout(3000)
    B.evaluate("(()=>{ duel.player.hand=['e_harp']; duel.phase='Main1'; renderDuel(); })()"); B.wait_for_timeout(800)
    B.evaluate("tryActivateFromHandSpell(0)"); B.wait_for_timeout(1500); passAll(A,B); B.wait_for_timeout(3000)
    check('Espadas: si B las destruye, ya puede atacar', B.evaluate("swordsLockOn(duel.player)")==0 and A.evaluate("duel.player.gy.includes('e_sw')"), [B.evaluate("swordsLockOn(duel.player)"), A.evaluate("duel.log.slice(0,4)")])
    # Jabalina: B ataca a A; A responde con la Jabalina
    A.evaluate("(()=>{ duel.player.monsterZones=["+(Z%('e_wall','defense','true'))+",null,null,null,null]; duel.player.stZones=[{cardId:'e_jav',faceup:false,setThisTurn:false},null,null,null,null]; renderDuel(); })()"); A.wait_for_timeout(1200)
    lpA=A.evaluate("duel.player.lp")
    B.evaluate("duel.phase='Battle'; duel.player.monsterZones[0].position='attack'; duel.player.monsterZones[0].attackedThisTurn=false; duel.player.monsterZones[0].attackCount=0; renderDuel()"); B.wait_for_timeout(800)
    B.evaluate("tryAttack(duel.player,0)"); B.wait_for_timeout(500)
    if B.locator('.choice-btn', has_text='Muro').count(): B.locator('.choice-btn', has_text='Muro').first.click()
    A.wait_for_timeout(1500)
    if A.locator('.choice-btn', has_text='Jabalina').count(): A.locator('.choice-btn', has_text='Jabalina').first.click()
    A.wait_for_timeout(1500); passAll(B,A); A.wait_for_timeout(3500)
    check('Jabalina en red: A gana 2600 LP y B lo ve', A.evaluate("duel.player.lp")==lpA+2600 and B.evaluate("duel.ai.lp")==lpA+2600, [A.evaluate("duel.player.lp"), B.evaluate("duel.ai.lp"), A.evaluate("duel.log.slice(0,5)")])
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
