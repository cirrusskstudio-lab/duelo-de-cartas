from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const P=(i,k)=>({id:i, kind:'monster', name:'Sello '+k, image:null, finish:'normal', victoryPiece:{setId:'vsN',pieceIndex:k}, monster:{attribute:'OSCURIDAD',race:'Lanzador de Conjuros',category:'Normal',isExtra:false,level:3,atk:1000,def:1000,materials:'',effectText:'',trigger:'none'}});
  const cs=[P('x1',1),P('x2',2),P('x3',3),P('x4',4),P('x5',5),
  {id:'x_nec', kind:'monster', name:'Necross Red', image:null, finish:'normal', monster:{attribute:'OSCURIDAD',race:'Demonio',category:'Efecto',isExtra:false,level:7,atk:1800,def:0,materials:'',effectText:'',trigger:'none',necross:true}},
  {id:'x_con', kind:'spell', name:'Contrato Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'contractWithExodia',value:0}},
  {id:'x_lib', kind:'monster', name:'Biblioteca Red', image:null, finish:'normal', monster:{attribute:'LUZ',race:'Lanzador de Conjuros',category:'Efecto',isExtra:false,level:4,atk:0,def:2000,materials:'',effectText:'',trigger:'none',spellCounter:true}},
  {id:'x_pot', kind:'spell', name:'Olla Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'draw',value:1}},
  {id:'x_rai', kind:'spell', name:'Raigeki Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'destroyAllOppMonsters',value:0}},
  {id:'x_roar', kind:'trap', name:'Rugido Red', image:null, finish:'normal', trap:{subtype:'Normal',cond:'En cualquier momento (libre)',effectText:'',func:'threateningRoar',value:0}},
  {id:'x_san', kind:'spell', name:'Santidad Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'cardOfSanctity',value:0}}];
  cs.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def passAll(*pgs):
    for pg in pgs:
        for t in ('Pasar','No responder','No activar'):
            if pg.locator('.choice-btn', has_text=t).count(): pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(300)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    # Biblioteca de B gana contador cuando A activa una Mágica
    B.evaluate("(()=>{ duel.player.monsterZones=[{cardId:'x_lib',position:'defense',faceup:true,atkMod:0,defMod:0},null,null,null,null]; duel.player.stZones=[null,null,null,null,null]; renderDuel(); })()"); B.wait_for_timeout(1200)
    A.evaluate("(()=>{ duel.player.hand=['x_pot','x_con','x_nec','x_rai','x_san']; duel.player.gy=['x1','x2','x3','x4','x5']; duel.player.stZones=[null,null,null,null,null]; duel.player.monsterZones=[null,null,null,null,null]; renderDuel(); })()"); A.wait_for_timeout(1200)
    A.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('x_pot'))"); A.wait_for_timeout(1500); passAll(B,A); A.wait_for_timeout(2500)
    check('La Biblioteca de B gana un Contador cuando A activa una Mágica', B.evaluate("duel.player.monsterZones[0].spellCounters")==1, B.evaluate("duel.log.slice(0,5)"))
    check('A ve el contador de la Biblioteca de B', A.evaluate("(duel.ai.monsterZones[0]||{}).spellCounters")==1, A.evaluate("duel.ai.monsterZones[0]"))
    # Contrato con Exodia por red
    A.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('x_con'))"); A.wait_for_timeout(1500); passAll(B,A); A.wait_for_timeout(3000)
    check('A Invoca a Necross con el Contrato', A.evaluate("duel.player.monsterZones.some(z=>z&&z.cardId==='x_nec')"), A.evaluate("duel.log.slice(0,6)"))
    check('B ve a Necross (con su aura)', B.evaluate("duel.ai.monsterZones.some(z=>z&&z.faceup&&findCardDef(z.cardId)&&findCardDef(z.cardId).name==='Necross Red')") and B.locator('#opp_mon_row .zone.necross-aura').count()==1)
    check('La Biblioteca de B ya tiene 2 contadores', B.evaluate("duel.player.monsterZones[0].spellCounters")==2)
    # Santidad por red
    A.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('x_san'))"); A.wait_for_timeout(1500); passAll(B,A); A.wait_for_timeout(3000)
    check('Tarjeta de Santidad: ambos tienen 6 cartas', A.evaluate("duel.player.hand.length")==6 and B.evaluate("duel.player.hand.length")==6, [A.evaluate("duel.player.hand.length"), B.evaluate("duel.player.hand.length")])
    # Rugido: A bloquea a B
    A.evaluate("ritualExodiaFuncs(duel.player, duel.ai, findCardDef('x_roar'), findCardDef('x_roar').trap, 'threateningRoar', ()=>{})"); B.wait_for_timeout(1500)
    check('Rugido Amenazante llega a B (no puede atacar)', B.evaluate("duel.player._roarLock===true"))
    A.evaluate("duel.player.hand=duel.player.hand.slice(0,3); renderDuel(); jumpToEndPhase(); advancePhase()"); A.wait_for_timeout(3000); print("   turno B:", B.evaluate("duel.activePlayer"), A.evaluate("[duel.activePlayer,duel.phase,duel.chainLinks.length,netState.awaitingAttack,!!netState.awaitingSpecialSummonResponse, document.querySelectorAll('.overlay').length]"), A.evaluate("[...document.querySelectorAll('.overlay')].map(o=>o.id+'|'+o.style.display+'|'+o.textContent.slice(0,120))"))
    check('Al cambiar de turno se levanta el bloqueo en B', B.evaluate("!duel.player._roarLock"))
    # Raigeki de B contra Necross de A
    B.evaluate("(()=>{ duel.player.hand.push('x_rai'); duel.phase='Main1'; renderDuel(); })()"); B.wait_for_timeout(800)
    B.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('x_rai'))"); B.wait_for_timeout(1500); passAll(A,B); B.wait_for_timeout(3000)
    check('Necross de A no se destruye con el Raigeki de B', A.evaluate("duel.player.monsterZones.some(z=>z&&z.cardId==='x_nec')") and B.evaluate("duel.ai.monsterZones.some(Boolean)"), [A.evaluate("duel.log.slice(0,5)"), B.evaluate("duel.log.slice(0,5)")])
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
