from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
CARDS = """(()=>{ const M=(id,name,lvl,extra)=>({id, kind:'monster', name, image:null, finish:'normal', monster:Object.assign({attribute:'LUZ',race:'Guerrero',category:'Efecto',isExtra:false,pendulum:false,level:lvl,atk:2500,def:1000,materials:'',effectText:'',trigger:'none'}, extra)});
 [M('e1','Errata 1 turno',8,{ignoreLevelSpecial:true, drawback:'selfDestructTurns', drawbackTurns:1}),
  M('e2','Errata 2 turnos',8,{ignoreLevelSpecial:true, drawback:'selfDestructTurns', drawbackTurns:2}),
  M('e4','Errata nivel 4',4,{ignoreLevelSpecial:true, drawback:'selfDestructTurns', drawbackTurns:1}),
  M('es','Errata siempre',4,{ignoreLevelSpecial:false, drawback:'selfDestructTurns', drawbackTurns:1}),
  M('ec','No ataca por errata',4,{ignoreLevelSpecial:true, drawback:'cannotAttack'}),
  M('sol','Soldado',4,{atk:1000})].forEach(c=>collection.push(c)); })()"""
SETUP = """(hand)=>{ cleanupAllTokens(); const player=makeEmptyPlayer('Tú',8000,false), ai=makeEmptyPlayer('IA',8000,true);
 player.deck=Array(30).fill('sol'); ai.deck=Array(30).fill('sol'); player.hand=hand.slice();
 duel={player, ai, turn:2, activePlayer:'player', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:99, difficulty:'normal', sandbox:true, sandboxAIPaused:true};
 netState.active=false; document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }"""
def names(pg): return pg.evaluate("duel.player.monsterZones.filter(Boolean).map(z=>findCardDef(z.cardId).name)")
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(F); pg.wait_for_timeout(400); pg.evaluate(CARDS); pg.click('button[data-tab="tabDuelo"]')
    def end_round(): pg.evaluate("finishTurn()"); pg.evaluate("finishTurn()"); pg.wait_for_timeout(50)
    def attack_ok(): 
        pg.evaluate("duel.phase='Battle'"); pg.evaluate("tryAttack(duel.player,0)"); pg.wait_for_timeout(250)
        r = pg.evaluate("duel.ai.lp"); pg.evaluate("duel.phase='Main1'; duel.ai.lp=8000; renderDuel()"); return r<8000
    # N=1
    pg.evaluate(SETUP, ['e1']); pg.evaluate("trySpecialSummonIgnoreLevel(0)"); pg.wait_for_timeout(200)
    check('N=1: se invoca de modo especial con errata', names(pg)==['Errata 1 turno'] and pg.evaluate("duel.player.monsterZones[0].errata===true"))
    check('N=1: puede atacar el turno en que se invoca', attack_ok())
    end_round()
    check('N=1: sigue en el campo al empezar tu siguiente turno', names(pg)==['Errata 1 turno'])
    check('N=1: puede atacar en tu siguiente turno (ya no se destruye al atacar)', attack_ok() and names(pg)==['Errata 1 turno'])
    pg.evaluate("finishTurn()"); pg.wait_for_timeout(600)
    check('N=1: se autodestruye al FINAL de ese turno', names(pg)==[] and 'e1' in pg.evaluate("duel.player.gy"), pg.evaluate("duel.log.slice(0,4)"))
    # N=2
    pg.evaluate(SETUP, ['e2']); pg.evaluate("trySpecialSummonIgnoreLevel(0)"); pg.wait_for_timeout(100)
    end_round(); check('N=2: sobrevive 1er turno', names(pg)==['Errata 2 turnos'])
    end_round(); check('N=2: sobrevive al inicio del 2º turno', names(pg)==['Errata 2 turnos'])
    pg.evaluate("finishTurn()"); pg.wait_for_timeout(100)
    check('N=2: se destruye al final del 2º turno', names(pg)==[])
    # Invocación Normal de una carta con errata solo para su Invocación Especial
    pg.evaluate(SETUP, ['e4']); pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(100)
    end_round(); end_round(); end_round()
    check('Invocada de forma Normal: la errata NO aplica', names(pg)==['Errata nivel 4'])
    # errata sin opción de Invocación Especial: aplica siempre
    pg.evaluate(SETUP, ['es']); pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(100)
    end_round(); check('Errata "siempre": sobrevive su siguiente turno', names(pg)==['Errata siempre'])
    pg.evaluate("finishTurn()"); check('Errata "siempre": se destruye al final', names(pg)==[])
    # cannotAttack solo si salió con la Invocación Especial
    pg.evaluate(SETUP, ['ec']); pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(100)
    check('"No puede atacar": invocada Normal sí ataca', attack_ok())
    pg.evaluate(SETUP, ['ec']); pg.evaluate("trySpecialSummonIgnoreLevel(0)"); pg.wait_for_timeout(100)
    check('"No puede atacar": con Invocación Especial no ataca', not attack_ok())
    print('errs', errs); print(f"{sum(res)}/{len(res)}"); b.close()
