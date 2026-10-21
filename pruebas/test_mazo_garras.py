from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
import os
JSON=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','mazos','garras_de_alquiler.json')
res=[]
def check(n,c,i=''):
    res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; DL=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d:(DL.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(1200)
    pg.set_input_files('#importBackupFile', JSON); pg.wait_for_timeout(1200)
    check('Se importa con el botón del juego', any('importada correctamente' in d for d in DL), DL)
    ev=pg.evaluate
    check('Mazo válido (40 + Extra 5, máx. 3 copias)', ev("validateDeck(decks.find(d=>d.id==='ga_deck_garras')).valid"))
    dc=ev("calculateDeckCost(decks.find(d=>d.id==='ga_deck_garras'))")
    per=ev("Object.fromEntries(collection.filter(c=>c.id.startsWith('ga_')).map(c=>[c.name.split(',')[0], cardDC(c)]))")
    print('DC total', dc['total'], 'main', dc['main'], 'extra', dc['extra']); print(per)
    pg.click('button[data-tab="tabDuelo"]')
    def setup(hand=[], pM=[], aM=[], aST=[], deck=None, gy=[], field=None):
        ev("""(a)=>{ cleanupAllTokens(); sbAutoPick=false; sbPick=null; document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); });
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck = a.deck.slice(); ai.deck = Array(20).fill('ga_vigia'); player.hand=a.hand.slice(); player.gy=a.gy.slice();
          a.pM.forEach((x,i)=>{ if(x){ player.monsterZones[i]=emptyMonsterState(x,'attack',true); player.monsterZones[i].summonedThisTurn=false; } });
          a.aM.forEach((x,i)=>{ if(x){ ai.monsterZones[i]=emptyMonsterState(x,'attack',true); ai.monsterZones[i].summonedThisTurn=false; } });
          a.aST.forEach((x,i)=>ai.stZones[i]={cardId:x, faceup:false, setThisTurn:false});
          if(a.field) player.fieldZone={cardId:a.field};
          player.extra=['ga_capitan','ga_capitan','ga_lobo','ga_desatada','ga_manada'];
          duel = { player, ai, turn:3, activePlayer:'player', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:9, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""",
          dict(hand=hand,pM=pM,aM=aM,aST=aST,deck=deck or ['ga_cazador','ga_medico','ga_vendaval'],gy=gy,field=field))
        pg.wait_for_timeout(150)
    def click(t): pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(700)
    def names(side): return ev(f"duel.{side}.monsterZones.filter(Boolean).map(z=>findCardDef(z.cardId).name.split(',')[0])")
    ev("Math.random=()=>0.99")
    # COMBO 1: Rastreadora sola desde la mano → busca Cazador → Cazador saca a Zarpazo → Capitán
    setup(hand=['ga_rastreadora','ga_zarpazo'], aM=['ga_intendente','ga_cazador'], deck=['ga_cazador','ga_medico','ga_recluta'])
    ev("trySpecialSummonIgnoreLevel(0)"); pg.wait_for_timeout(600); click('Cazador Errante')
    check('C1) Rastreadora se Invoca sola y busca a Cazador', ev("duel.player.hand.includes('ga_cazador')"), ev("duel.log.slice(0,4)"))
    ev("tryNormalSummon(duel.player.hand.indexOf('ga_cazador'),'attack',true)"); pg.wait_for_timeout(600); click('Zarpazo'); pg.wait_for_timeout(500)
    click('Intendente'); pg.wait_for_timeout(500)
    check('C1) Cazador saca a Zarpazo y Zarpazo destruye un monstruo', names('player')==['Rastreadora','Cazador Errante','Zarpazo'] and names('ai')==['Cazador Errante'], [names('player'), names('ai'), ev("duel.log.slice(0,5)")])
    ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click('Capitán Colmillo'); pg.wait_for_timeout(200)
    pg.locator('#matGrid .choice-btn', has_text='Rastreadora').click(); pg.locator('#matGrid .choice-btn', has_text='Cazador').click(); pg.locator('#matConfirm').click(); pg.wait_for_timeout(900)
    click('Cazador Errante'); pg.wait_for_timeout(500)
    check('C1) Capitán Colmillo entra y destruye el último monstruo rival', 'Capitán Colmillo' in ' '.join(names('player')) and names('ai')==[], [names('player'), names('ai'), ev("duel.log.slice(0,4)")])
    pg.screenshot(path='/tmp/combo_garras.png')
    # COMBO 2: Reparto del Botín descartando a Recluta → saca Rastreadora del Deck → busca
    setup(hand=['ga_botin','ga_recluta'], deck=['ga_olla','ga_waboku','ga_olla','ga_rastreadora','ga_olla','ga_waboku','ga_olla','ga_cazador','ga_zarpazo'])
    ev("sbAutoPick=true; sbPick=/Recluta|Activar/"); ev("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(3500); ev("sbAutoPick=false")
    check('C2) Descartas a Recluta y saca a un compañero del Deck que vuelve a buscar', ev("duel.player.gy.includes('ga_recluta')") and len(names('player'))==1, [names('player'), ev("duel.log.slice(0,8)")])
    # COMBO 3: Campamento + Intendente Nv6 sin Tributos
    setup(hand=['ga_intendente'], field='ga_campamento', deck=['ga_olla','ga_olla'])
    ev("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(600)
    check('C3) Intendente (Nv 6) entra sin Tributos con el Campamento y roba', names('player')==['Intendente'] and ev("duel.player.hand.length")==1 and ev("atkVal(duel.player.monsterZones.find(Boolean))")==2600, [names('player'), ev("duel.log.slice(0,4)")])
    # COMBO 4: Contrato de Rescate revive a Zarpazo y vuelve a destruir
    setup(hand=['ga_rescate'], gy=['ga_zarpazo'], aM=['ga_intendente'])
    ev("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(1500); click('Zarpazo'); pg.wait_for_timeout(1500)
    if pg.locator('.choice-btn', has_text='Intendente').count(): click('Intendente')
    pg.wait_for_timeout(500)
    check('C4) Contrato de Rescate revive a Zarpazo y su efecto se activa otra vez', names('player')==['Zarpazo'] and names('ai')==[] and ev("duel.player.lp")==7200, [names('player'), names('ai'), ev("duel.log.slice(0,6)")])
    # COMBO 5: Médico revive y el revivido dispara su efecto (Cazador → saca otro de la mano)
    setup(hand=['ga_medico','ga_vendaval'], gy=['ga_cazador'], aST=['ga_waboku'])
    ev("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(600); click('Cazador'); pg.wait_for_timeout(800); click('Vendaval'); pg.wait_for_timeout(800)
    if pg.locator('.choice-btn').count(): pg.locator('.choice-btn').first.click(); pg.wait_for_timeout(600)
    check('C5) Médico → Cazador del Cementerio → Vendaval de la mano → destruye la trampa', len(names('player'))==3 and ev("!duel.ai.stZones.some(Boolean)"), [names('player'), ev("duel.log.slice(0,8)")])
    print('errores:', errs); check('Sin errores', not errs, errs)
    print(f'{sum(res)}/{len(res)}'); b.close()
