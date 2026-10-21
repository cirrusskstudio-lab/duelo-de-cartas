import os
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
JSON=os.environ.get('JSON') or os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','mazos','ejercito_rebelde.json')
res=[]
def check(n,c,i=''):
    res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; DL=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d:(DL.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(1200)
    pg.set_input_files('#importBackupFile', JSON); pg.wait_for_timeout(1200)
    ev=pg.evaluate
    check('Se importa con el botón del juego', any('importada correctamente' in d for d in DL), DL)
    check('Mazo válido (40 + Extra 4)', ev("validateDeck(decks.find(d=>d.id==='rb_deck_rebeldes')).valid"))
    dc=ev("calculateDeckCost(decks.find(d=>d.id==='rb_deck_rebeldes'))"); print('DC', dc['main'], dc['extra'])
    print(ev("Object.fromEntries(collection.filter(c=>c.id.startsWith('rb_')).map(c=>[c.name, cardDC(c)]))"))
    pg.click('button[data-tab="tabDuelo"]')
    def setup0(hand=[], pM=[], aM=[], pST=[], deck=None, gy=[], active='player', phase='Main1', field=None, aiHand=[]):
        ev("""(a)=>{ cleanupAllTokens(); sbAutoPick=false; sbPick=null; document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); });
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck = a.deck.slice(); ai.deck = Array(20).fill('rb_fusilero'); player.hand=a.hand.slice(); player.gy=a.gy.slice(); ai.hand=a.aiHand.slice();
          a.pM.forEach((x,i)=>{ if(x){ player.monsterZones[i]=emptyMonsterState(x[0],x[1]||'attack',x[2]!==false); player.monsterZones[i].summonedThisTurn=false; } });
          a.aM.forEach((x,i)=>{ if(x){ ai.monsterZones[i]=emptyMonsterState(x,'attack',true); ai.monsterZones[i].summonedThisTurn=false; } });
          a.pST.forEach((x,i)=>player.stZones[i]={cardId:x[0], faceup:!!x[1], setThisTurn:false});
          if(a.field) player.fieldZone={cardId:a.field};
          player.extra=['rb_acorazado','rb_acorazado','rb_bombardero','rb_helicoptero'];
          duel = { player, ai, turn:3, activePlayer:a.active, phase:a.phase, over:false, firstTurn:false, log:[], chainLinks:[], handLimit:9, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""",
          dict(hand=hand,pM=pM,aM=aM,pST=pST,deck=deck or ['rb_suministros']*8,gy=gy,active=active,phase=phase,field=field,aiHand=aiHand))
        pg.wait_for_timeout(150)
    def setup(*a, **k):
        ev("duel && (duel.over=true)"); pg.wait_for_timeout(1300); setup0(*a, **k)
    def click(t): pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(700)
    def cast(cid): ev(f"tryActivateFromHandSpell(duel.player.hand.indexOf('{cid}'))"); pg.wait_for_timeout(1400)
    def names(side): return ev(f"duel.{side}.monsterZones.filter(Boolean).map(z=>findCardDef(z.cardId).name)")
    ev("Math.random=()=>0.99")
    # 1 Golpe de Estado
    setup(hand=['rb_general','rb_golpe'], deck=['rb_fusilero','rb_suministros','rb_granadero','rb_escudero'])
    ev("sbAutoPick=true"); cast('rb_golpe'); ev("sbAutoPick=false")
    gen=ev("(()=>{ const z=duel.player.monsterZones.find(z=>z&&z.cardId==='rb_general'); return z?atkVal(z):null; })()")
    check('Golpe de Estado: el General llega mandando 2 soldados Normales del Deck', gen is not None and ev("duel.player.gy.filter(x=>['rb_fusilero','rb_granadero','rb_escudero'].includes(x)).length")==2, [gen, ev("duel.log.slice(0,4)")])
    check('El General gana +100 ATK por cada monstruo en tu Cementerio', gen==3000, gen)
    # 2 Paracaidista + tokens tributables
    setup(hand=['rb_paracaidista','rb_girida'])
    ev("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(700)
    check('Paracaidista aterriza con 2 Reclutas', len(names('player'))==3, names('player'))
    check('Los Reclutas sí se pueden Sacrificar', ev("duel.player.monsterZones.filter(z=>z&&isTokenId(z.cardId)).every(z=>canUseAsMaterial(z.cardId,'tribute'))"))
    # 3 Mina boca abajo destruye al atacante
    setup(pM=[['rb_mina','defense',False]], aM=['rb_motorizado'], active='ai', phase='Battle')
    ev("performAttack(duel.ai,0,0,()=>{})"); pg.wait_for_timeout(800)
    if pg.locator('.choice-btn', has_text='Motorizado').count(): click('Motorizado')
    pg.wait_for_timeout(1500)
    check('Mina Antitanque: al ser atacada boca abajo destruye al atacante', names('ai')==[], [names('ai'), ev("duel.log.slice(0,5)")])
    # 4 Hozumi
    setup(hand=['rb_hozumi'], aM=['rb_granadero'])
    ev("trySpecialSummonIgnoreLevel(0)"); pg.wait_for_timeout(700)
    if pg.locator('.choice-btn', has_text='Granadero').count(): click('Granadero')
    check('Hozumi emerge sin Tributos y pone boca abajo al monstruo rival', 'Submarino Rebelde Hozumi' in names('player') and ev("duel.ai.monsterZones[0] && !duel.ai.monsterZones[0].faceup"), [names('player'), ev("duel.log.slice(0,4)")])
    ev("duel.phase='Battle'; tryAttack(duel.player, duel.player.monsterZones.findIndex(z=>z&&z.cardId==='rb_hozumi'))"); pg.wait_for_timeout(300)
    check('Hozumi no puede atacar cuando emerge así', any('no puede declarar ataques' in d for d in DL[-2:]), DL[-2:])
    ev("document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); }); duel.phase='End'; finishTurn()"); pg.wait_for_timeout(500)
    check('Hozumi se sumerge: regresa a la mano en la End Phase', ev("duel.player.hand.includes('rb_hozumi')") and 'Submarino Rebelde Hozumi' not in names('player'), [names('player'), ev("duel.player.hand")])
    # 5 Desertor
    setup(hand=['rb_desertor'], deck=['rb_suministros','rb_suministros'])
    ev("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(500)
    h=ev("duel.player.hand.length"); ev("duel.phase='End'; finishTurn()"); pg.wait_for_timeout(500)
    check('Desertor roba 1 y huye a la mano al final del turno', h==1 and ev("duel.player.hand.includes('rb_desertor')"), [h, ev("duel.player.hand")])
    # 6 Torpedo
    setup(hand=['rb_torpedo'], aM=['rb_dicoka'])
    cast('rb_torpedo'); pg.wait_for_timeout(300)
    if pg.locator('.choice-btn', has_text='Di-Coka').count(): click('Di-Coka')
    check('¡Torpedo! regresa a la mano el monstruo rival', names('ai')==[] and ev("duel.ai.hand.includes('rb_dicoka')"), [names('ai'), ev("duel.log.slice(0,4)")])
    # 7 Fusión Acorazado con 2 vanilla
    setup(hand=['rb_ensamble'], pM=[['rb_fusilero'],['rb_escudero']])
    ev("sbAutoPick=true"); cast('rb_ensamble'); ev("sbAutoPick=false")
    check('Ensamble de Guerra: 2 Normales forman al Gran Acorazado', 'El Gran Acorazado Rebelde' in names('player'), [names('player'), ev("duel.log.slice(0,4)")])
    # 8 Sargento Metralla al Cementerio
    setup(pM=[['rb_metralla']])
    ev("fxDestroyMonster(duel.player,0)"); pg.wait_for_timeout(700)
    if pg.locator('.choice-btn', has_text='Activar').count(): click('Activar')
    check('Sargento Metralla: al caer, el rival pierde 1000 LP', ev("duel.ai.lp")==7000, ev("duel.log.slice(0,4)"))
    # 9 Campo Minado continuo
    setup(pST=[['rb_campominado',True]], aiHand=['rb_motorizado'], active='ai')
    ev("aiMainPhaseActionsCore(()=>{window._ok=1})"); pg.wait_for_timeout(2500)
    check('Campo Minado destruye lo que Invoca el rival', names('ai')==[] and ev("duel.ai.gy.includes('rb_motorizado')"), [names('ai'), ev("duel.log.slice(0,5)")])
    # 10 Cuartel General
    setup(hand=['rb_metralla'], field='rb_cuartel', pM=[['rb_fusilero']])
    ev("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(500)
    check('Cuartel: Nivel 5 sin Sacrificio y +300 a los Guerreros', 'Sargento Metralla Rebelde' in names('player') and ev("atkVal(duel.player.monsterZones[0])")==1800, [names('player'), ev("atkVal(duel.player.monsterZones[0])")])
    # 11 Bombardero (Sincronía)
    setup(pM=[['rb_dicoka'],['rb_fusilero']])
    ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click('Bombardero')
    pg.locator('#matGrid .choice-btn').nth(0).click(); pg.locator('#matGrid .choice-btn').nth(1).click(); pg.locator('#matConfirm').click(); pg.wait_for_timeout(700)
    check('Bombardero Rebelde sale del Extra Deck', names('player')==['Bombardero Rebelde'], names('player'))
    print('errores:', errs); check('Sin errores', not errs, errs)
    print(f'{sum(res)}/{len(res)}'); b.close()
