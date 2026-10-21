import os
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
JSON=os.environ.get('JSON') or os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','mazos','coloso_sellado.json')
res=[]
def check(n,c,i=''):
    res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; DL=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d:(DL.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(1200)
    pg.set_input_files('#importBackupFile', JSON); pg.wait_for_timeout(1200)
    ev=pg.evaluate
    check('Se importa (cartas, mazo y Conjunto de Victoria)', any('importada correctamente' in d for d in DL) and ev("victorySets.some(v=>v.id==='cs_set_coloso')"), DL)
    check('Mazo válido', ev("validateDeck(decks.find(d=>d.id==='cs_deck_coloso')).valid"))
    dc=ev("calculateDeckCost(decks.find(d=>d.id==='cs_deck_coloso'))"); print('DC total', dc['total'])
    print(ev("Object.fromEntries(collection.filter(c=>c.id.startsWith('cs_')).map(c=>[c.name, cardDC(c)]))"))
    pg.click('button[data-tab="tabDuelo"]')
    def setup(hand=[], pM=[], aM=[], pST=[], deck=None, gy=[], active='player', phase='Main1'):
        ev("""(a)=>{ cleanupAllTokens(); sbAutoPick=false; sbPick=null; document.querySelectorAll('.overlay,.fpv-overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); });
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck = a.deck.slice(); ai.deck = Array(20).fill('cs_muro'); player.hand=a.hand.slice(); player.gy=a.gy.slice();
          a.pM.forEach((x,i)=>{ if(x){ player.monsterZones[i]=emptyMonsterState(x[0],x[1]||'attack',x[2]!==false); player.monsterZones[i].summonedThisTurn=false; } });
          a.aM.forEach((x,i)=>{ if(x){ ai.monsterZones[i]=emptyMonsterState(x,'attack',true); ai.monsterZones[i].summonedThisTurn=false; } });
          a.pST.forEach((x,i)=>player.stZones[i]={cardId:x, faceup:false, setThisTurn:false});
          duel = { player, ai, turn:3, activePlayer:a.active, phase:a.phase, over:false, firstTurn:false, log:[], chainLinks:[], handLimit:9, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""",
          dict(hand=hand,pM=pM,aM=aM,pST=pST,deck=deck or ['cs_olla']*8,gy=gy,active=active,phase=phase))
        pg.wait_for_timeout(150)
    def click(t): pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(700)
    def cast(cid):
        ev(f"tryActivateFromHandSpell(duel.player.hand.indexOf('{cid}'))"); pg.wait_for_timeout(1400)
    ev("Math.random=()=>0.99")
    # C1 Guardián busca pieza
    setup(hand=['cs_guardian'], deck=['cs_olla','cs_brazod','cs_olla','cs_piernai'])
    ev("tryNormalSummon(0,'defense',true)"); pg.wait_for_timeout(500); click('Brazo Derecho')
    check('C1) Guardián del Sello busca una pieza', ev("duel.player.hand.includes('cs_brazod')"), ev("duel.log.slice(0,3)"))
    # C2 Bibliotecario: 3 Mágicas → roba
    setup(hand=['cs_llamado','cs_duende','cs_olla'], pM=[['cs_biblio','defense']], deck=['cs_olla']*6+['cs_cabeza'])
    cast('cs_llamado'); click('Coloso Sellado'); cast('cs_duende'); cast('cs_olla')
    h=ev("duel.player.hand.length"); c=ev("duel.player.monsterZones[0].spellCounters")
    ev("useSpellCounters(duel.player,0)"); pg.wait_for_timeout(300)
    check('C2) Bibliotecario junta 3 contadores con 3 Mágicas y roba 1', c==3 and ev("duel.player.hand.length")==h+1, [c, h, ev("duel.log.slice(0,5)")])
    # C3 Vigía al Cementerio → busca pieza (≤1500 ATK)
    setup(pM=[['cs_vigia','defense']], deck=['cs_olla','cs_piernad','cs_olla'])
    ev("fxDestroyMonster(duel.player,0)"); pg.wait_for_timeout(700); click('Activar'); pg.wait_for_timeout(400); click('Pierna Derecha')
    check('C3) Vigía de las Catacumbas al Cementerio busca una pieza', ev("duel.player.hand.includes('cs_piernad')"), ev("duel.log.slice(0,4)"))
    # C4 Soldado de Reserva recupera piezas descartadas
    setup(pST=['cs_reserva'], gy=['cs_brazod','cs_brazoi','cs_cabeza','cs_muro','cs_vigia','cs_necross'])
    ev("tryActivateSetST(duel.player,0)"); pg.wait_for_timeout(1500)
    for t in ('Brazo Derecho','Brazo Izquierdo','El Coloso Sellado'): click(t)
    # La IA (o la elección automática) prioriza las piezas
    setup(pST=['cs_reserva'], gy=['cs_brazod','cs_vigia','cs_cabeza','cs_muro','cs_guardian','cs_necross'])
    ev("sbAutoPick=true"); ev("tryActivateSetST(duel.player,0)"); pg.wait_for_timeout(1500); ev("sbAutoPick=false")
    check('C4) La elección automática recupera primero las piezas', all(x in ev("duel.player.hand") for x in ['cs_brazod','cs_cabeza']), ev("duel.player.hand"))
    setup(pST=['cs_reserva'], gy=['cs_brazod','cs_brazoi','cs_cabeza','cs_muro','cs_vigia','cs_necross'])
    ev("tryActivateSetST(duel.player,0)"); pg.wait_for_timeout(1500)
    for t in ('Brazo Derecho','Brazo Izquierdo','El Coloso Sellado'): click(t)
    hand=ev("duel.player.hand")
    check('C4) Soldado de Reserva regresa 3 piezas del Cementerio', len(hand)==3 and all(x in hand for x in ['cs_brazod','cs_brazoi','cs_cabeza']), [hand, ev("duel.log.slice(0,5)")])
    # C5 ¡Victoria! 4 piezas en mano + Llamado del Sello busca la quinta
    setup(hand=['cs_cabeza','cs_brazod','cs_brazoi','cs_piernad','cs_llamado'], deck=['cs_olla','cs_piernai','cs_olla'])
    cast('cs_llamado'); click('Pierna Izquierda'); pg.wait_for_timeout(1200)
    pg.screenshot(path='/tmp/coloso_victoria.png'); pg.wait_for_timeout(3500)
    check('C5) Con la quinta pieza en la mano ganas el duelo', ev("duel.over") and ev("duel.log.some(m=>/completó el conjunto/.test(m))"), ev("duel.log.slice(0,4)"))
    # C6 Espadas: la IA no puede atacar
    setup(hand=['cs_espadas'], aM=['cs_guardian'])
    cast('cs_espadas'); lp=ev("duel.player.lp")
    ev("duel.activePlayer='ai'; duel.phase='Battle'; aiBattlePhase(()=>{window._bp=1})"); pg.wait_for_timeout(1200)
    check('C6) Espadas: el rival no puede atacar por 3 turnos', ev("duel.ai.swordsLockTurns")==3 and ev("duel.player.lp")==lp, [ev("duel.ai.swordsLockTurns"), ev("duel.log.slice(0,3)")])
    # C7 Plan B: Coloso Necrótico
    setup(hand=['cs_necross','cs_contrato'], gy=['cs_cabeza','cs_brazod','cs_brazoi','cs_piernad','cs_piernai'])
    cast('cs_contrato'); pg.wait_for_timeout(1200)
    check('C7) Plan B: el Contrato Invoca al Coloso Necrótico', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='cs_necross')"), ev("duel.log.slice(0,4)"))
    # C8 Sacerdotisa de la Fe recupera el Llamado
    setup(pM=[['cs_fe','defense',False]], gy=['cs_llamado'])
    ev("tryChangePosition(duel.player,0)"); pg.wait_for_timeout(500)
    if pg.locator('.choice-btn').count(): pg.locator('.choice-btn').first.click(); pg.wait_for_timeout(600)
    if pg.locator('.choice-btn', has_text='Llamado').count(): click('Llamado')
    check('C8) Sacerdotisa de la Fe (volteo) recupera el Llamado del Sello', ev("duel.player.hand.includes('cs_llamado')"), ev("duel.log.slice(0,4)"))
    print('errores:', errs); check('Sin errores', not errs, errs)
    print(f'{sum(res)}/{len(res)}'); b.close()
