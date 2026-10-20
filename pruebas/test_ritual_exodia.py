import json, re
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
def M(i,n,atk=1500,d=1000,lvl=4,cat='Efecto',**kw):
    m={"attribute":"LUZ","race":"Guerrero","category":cat,"isExtra":False,"level":lvl,"atk":atk,"def":d,"materials":"","effectText":"x","trigger":"none"}; m.update(kw)
    return {"id":i,"kind":"monster","name":n,"image":None,"finish":"normal","monster":m}
def S(i,n,func,sub='Normal',val=0,**kw):
    sp={"subtype":sub,"effectText":"x","func":func,"value":val}; sp.update(kw)
    return {"id":i,"kind":"spell","name":n,"image":None,"finish":"normal","spell":sp}
def T(i,n,func,cond='En cualquier momento (libre)',sub='Normal',val=0):
    return {"id":i,"kind":"trap","name":n,"image":None,"finish":"normal","trap":{"subtype":sub,"cond":cond,"effectText":"x","func":func,"value":val}}
def piece(i,n,k):
    c=M(i,n,1000,1000,lvl=3,cat='Normal'); c['victoryPiece']={"setId":"vsEx","pieceIndex":k}; return c
cards=[M('m1','Soldado',1500),M('big','Atacante',3000),M('weak','Débil',800),
  M('rit','Caballero Ritual',2800,2500,lvl=8,cat='Ritual'),
  S('ritS','Ritual del Caballero','none','Ritual',ritual={"targetCardId":"rit","requirementMode":"level","levelRequired":8,"specificCardIds":[]}),
  M('rit7','Bestia Ritual',2400,2000,lvl=7,cat='Ritual'),
  S('ritS7','Ritual de la Bestia','none','Ritual',ritual={"targetCardId":"rit7","requirementMode":"level","levelRequired":7,"specificCardIds":[]}),
  M('manju','Manju',1400,1000,trigger='searchRitualOnSummon'),M('sonic','Pájaro Sónico',1400,1000,trigger='searchRitualSpellOnSummon'),
  M('raven','Cuervo Ritual',300,300,lvl=1,ritualFull=True),M('gyt','Alma Ritual',1000,1000,lvl=4,ritualGY=True),
  M('n4','Normal Nv4',1200,1000,lvl=4,cat='Normal'),
  S('ara','Arte Ritual Avanzado','advancedRitualArt','Ritual'),S('ppr','Pre-Preparación','prePreparationOfRites'),S('pr','Preparación de Ritos','preparationOfRites'),
  piece('p1','Pieza 1',1),piece('p2','Pieza 2',2),piece('p3','Pieza 3',3),piece('p4','Pieza 4',4),piece('p5','Pieza 5',5),
  M('necro','Exodia Necross',1800,0,lvl=7,necross=True),S('contract','Contrato con Exodia','contractWithExodia'),
  S('srchp','Llamado de la Pieza','searchVictoryPiece'),M('srchm','Guardián de Piezas',1000,1000,trigger='searchVictoryPieceOnSummon'),
  M('lib','Biblioteca Mágica',0,2000,lvl=4,spellCounter=True),S('pot','Olla','draw',val=1),
  T('wab','Waboku','waboku'),T('roar','Rugido','threateningRoar'),T('backup','Soldado de Refuerzo','backupSoldier'),S('sanct','Santidad','cardOfSanctity'),
  M('tom','Tomate',1400,1100,gy=1),S('raig','Raigeki','destroyAllOppMonsters')]
for c in cards:
    if c['id']=='tom': del c['monster']['gy']; c['gyEffect']={"trigger":"onSend","effect":"summonAtkLowFromDeck","value":1500,"cost":"none","restriction":"none"}
vsets=[{"id":"vsEx","name":"Los Cinco Sellos","desc":"","pieceIds":["p1","p2","p3","p4","p5"]}]
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); DL=[]; pg.on('dialog', lambda d: (DL.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(500)
    pg.evaluate("(a)=>{ localStorage.setItem('yugioh_collection_v1', JSON.stringify(a[0])); localStorage.setItem('yugioh_victorysets_v1', JSON.stringify(a[1])); }", [cards, vsets]); pg.reload(); pg.wait_for_timeout(900)
    pg.click('button[data-tab="tabDuelo"]')
    def setup(hand=[], pM=[], aM=[], pST=[], aST=[], aiHand=[], active='player', phase='Main1', deck=None, aiDeck=None, gy=[], aiGy=[]):
        pg.evaluate("""(a)=>{ cleanupAllTokens(); sbAutoPick=false; document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); });
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck = (a.deck||Array(20).fill('m1')).slice(); ai.deck = (a.aiDeck||Array(20).fill('m1')).slice(); player.hand=a.hand.slice(); ai.hand=a.aiHand.slice();
          player.gy=a.gy.slice(); ai.gy=a.aiGy.slice();
          a.pM.forEach((x,i)=>{ if(x) player.monsterZones[i]=emptyMonsterState(x[0], x[1]||'attack', true); });
          a.aM.forEach((x,i)=>{ if(x) ai.monsterZones[i]=emptyMonsterState(x[0], x[1]||'attack', true); });
          a.pST.forEach((x,i)=>player.stZones[i]={cardId:x[0], faceup:x[1], setThisTurn:false});
          a.aST.forEach((x,i)=>ai.stZones[i]={cardId:x[0], faceup:x[1], setThisTurn:false});
          player.monsterZones.forEach(z=>{ if(z) z.summonedThisTurn=false; }); ai.monsterZones.forEach(z=>{ if(z) z.summonedThisTurn=false; });
          duel = { player, ai, turn:3, activePlayer:a.active, phase:a.phase, over:false, firstTurn:false, log:[], chainLinks:[], handLimit:9, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""",
          dict(hand=hand,pM=pM,aM=aM,pST=pST,aST=aST,aiHand=aiHand,active=active,phase=phase,deck=deck,aiDeck=aiDeck,gy=gy,aiGy=aiGy))
        pg.wait_for_timeout(150)
    def log(n=8): return pg.evaluate(f"duel.log.slice(0,{n})")
    def opts(): return pg.locator('.choice-btn').all_inner_texts()
    def click(txt): pg.locator('.choice-btn', has_text=txt).first.click(); pg.wait_for_timeout(600)
    def ev(x): return pg.evaluate(x)
    def cast(cid, who='player'):
        pg.evaluate(f"(()=>{{ const P=duel.{who}; const k=P.hand.indexOf('{cid}'); startChain(P, findCardDef('{cid}'), '{cid}', 'spell', ()=>{{ if(k>-1) P.hand.splice(k,1); }}, null); }})()"); pg.wait_for_timeout(1300)
    def resolve(cid, who='player'):
        pg.evaluate(f"resolveSpellTrapEffect(duel.{who}, findCardDef('{cid}'), ()=>{{ window._done=true; }})"); pg.wait_for_timeout(500)
    pg.evaluate("Math.random=()=>0.99")

    # ---- RITUAL ----
    setup(hand=['manju'], deck=['m1','ritS','rit','m1'])
    pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(500)
    o=opts(); check('MANJU) Ofrece Monstruo Ritual o Mágica de Ritual del Deck', any('Caballero Ritual' in x for x in o) and any('Ritual del Caballero' in x for x in o) and not any('Soldado' in x for x in o), o)
    click('Caballero Ritual'); check('MANJU) Lo añade a la mano', ev("duel.player.hand.includes('rit') && !duel.player.deck.includes('rit')"), log())
    setup(hand=['sonic'], deck=['m1','ritS','rit'])
    pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(500)
    o=opts(); check('SÓNICO) Solo ofrece Mágicas de Ritual', o and all('Ritual del Caballero' in x for x in o if 'Cancel' not in x and '✕' not in x), o)
    click('Ritual del Caballero')
    setup(hand=['rit','ritS','raven'])
    check('CUERVO) El Ritual (Nivel 8) se puede activar solo con el Cuervo', ev("spellActivationBlockReason(duel.player, findCardDef('ritS'))")==None)
    cast('ritS'); pg.wait_for_timeout(300)
    pg.locator('.material-picker .choice-btn', has_text='Cuervo').click(); pg.wait_for_timeout(200)
    st=pg.locator('.material-picker .mat-status').inner_text()
    check('CUERVO) El selector acepta al Cuervo como Tributo completo', 'cubre' in st, st)
    pg.locator('.material-picker .mat-ok').first.click(); pg.wait_for_timeout(900)
    check('CUERVO) Invoca por Ritual y el Cuervo va al Cementerio', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='rit') && duel.player.gy.includes('raven')"), log())
    setup(hand=['rit','ritS'], pM=[['m1']], gy=['gyt'])
    cast('ritS'); pg.wait_for_timeout(300)
    o=pg.locator('.material-picker .choice-btn').all_inner_texts()
    check('GY) El monstruo del Cementerio aparece como Tributo', any('Cementerio' in x and 'Alma Ritual' in x for x in o), o)
    pg.locator('.material-picker .choice-btn', has_text='Alma Ritual').click(); pg.locator('.material-picker .choice-btn', has_text='Soldado').click(); pg.wait_for_timeout(200)
    pg.locator('.material-picker .mat-ok').first.click(); pg.wait_for_timeout(900)
    check('GY) Ritual con Tributo desde el Cementerio: queda desterrado', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='rit') && duel.player.banish.includes('gyt') && !duel.player.gy.includes('gyt')"), log())
    setup(hand=['rit','ara'], deck=['n4','m1','n4','n4'])
    check('ARA) Se puede activar con Normales en el Deck', ev("spellActivationBlockReason(duel.player, findCardDef('ara'))")==None, ev("spellActivationBlockReason(duel.player, findCardDef('ara'))"))
    pg.evaluate("sbAutoPick=true"); cast('ara'); pg.evaluate("sbAutoPick=false")
    check('ARA) Invoca al Ritual mandando 2 Normales del Deck al Cementerio', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='rit') && duel.player.gy.filter(x=>x==='n4').length===2 && duel.player.deck.length===2"), [log(), ev("duel.player.deck")])
    setup(hand=['rit','ara'], deck=['m1','m1'])
    check('ARA) Bloqueada si no hay Normales suficientes', ev("!!spellActivationBlockReason(duel.player, findCardDef('ara'))"))
    setup(hand=['ppr'], deck=['m1','ritS','rit','m1'])
    pg.evaluate("sbAutoPick=true"); cast('ppr'); pg.evaluate("sbAutoPick=false")
    check('PRE-PREP) Añade la Mágica de Ritual y su monstruo', ev("duel.player.hand.includes('ritS') && duel.player.hand.includes('rit')"), log())
    setup(hand=['pr'], deck=['m1','rit7','rit'], gy=['ritS7'])
    pg.evaluate("sbAutoPick=true"); cast('pr'); pg.evaluate("sbAutoPick=false")
    check('PREP) Añade Ritual Nv≤7 del Deck + su Mágica del Cementerio', ev("duel.player.hand.includes('rit7') && !duel.player.hand.includes('rit') && duel.player.hand.includes('ritS7')"), log())

    # ---- EXODIA ----
    setup(hand=['necro','contract'])
    check('NECROSS) Contrato bloqueado sin las 5 piezas en el Cementerio', 'Cementerio' in (ev("spellActivationBlockReason(duel.player, findCardDef('contract'))") or ''))
    pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(200)
    check('NECROSS) No se puede Invocar de Modo Normal', ev("!duel.player.monsterZones.some(Boolean)") and any('Contrato' in d for d in DL), DL[-1:])
    setup(hand=['necro','contract'], gy=['p1','p2','p3','p4','p5'])
    check('NECROSS) Con las 5 piezas el Contrato se puede activar', ev("spellActivationBlockReason(duel.player, findCardDef('contract'))")==None)
    cast('contract'); pg.wait_for_timeout(1500)
    check('NECROSS) El Contrato Invoca a Exodia Necross', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='necro')"), log())
    check('NECROSS) Aura visual en su zona', pg.locator('#p_mon_row .zone.necross-aura').count()==1)
    pg.evaluate("duel.activePlayer='ai'"); resolve('raig','ai')
    check('NECROSS) No se destruye por efectos (Raigeki)', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='necro')"), log())
    pg.evaluate("duel.ai.monsterZones[0]=emptyMonsterState('big','attack',true); duel.ai.monsterZones[0].summonedThisTurn=false; duel.phase='Battle'")
    lp=ev("duel.player.lp"); pg.evaluate("performAttack(duel.ai, 0, duel.player.monsterZones.findIndex(z=>z&&z.cardId==='necro'), ()=>{window._bt=1})"); pg.wait_for_timeout(2500)
    check('NECROSS) No se destruye en batalla (pero recibes el daño)', ev("duel.player.monsterZones.some(z=>z&&z.cardId==='necro')") and ev("duel.player.lp")==lp-1200, [log(), ev("duel.player.lp")])
    pg.evaluate("duel.activePlayer='player'; duel.phase='Main1'")
    a0=ev("atkVal(duel.player.monsterZones.find(z=>z&&z.cardId==='necro'))"); pg.evaluate("processFieldDrawbacks(duel.player)")
    check('NECROSS) Gana 500 ATK en tu Standby', ev("atkVal(duel.player.monsterZones.find(z=>z&&z.cardId==='necro'))")==a0+500)
    pg.evaluate("duel.player.gy.splice(duel.player.gy.indexOf('p3'),1); duel.player.banish.push('p3'); renderDuel();"); pg.wait_for_timeout(400)
    check('NECROSS) Se destruye si falta una pieza en el Cementerio', ev("!duel.player.monsterZones.some(z=>z&&z.cardId==='necro') && duel.player.gy.includes('necro')"), log())
    setup(hand=['srchp'], deck=['m1','p4','m1'])
    pg.evaluate("sbAutoPick=true"); cast('srchp'); pg.evaluate("sbAutoPick=false")
    check('PIEZA) La Mágica busca una Pieza de Victoria', ev("duel.player.hand.includes('p4')"), log())
    setup(hand=['srchm'], deck=['m1','p2'])
    pg.evaluate("sbAutoPick=true; tryNormalSummon(0,'attack',true); sbAutoPick=false"); pg.wait_for_timeout(500)
    check('PIEZA) El monstruo busca una Pieza al ser invocado', ev("duel.player.hand.includes('p2')"), log())
    setup(aiHand=['necro','contract'], aiGy=['p1','p2','p3','p4','p5'], active='ai')
    pg.evaluate("aiMainPhaseActions(()=>{ window._aiDone=1; })"); pg.wait_for_timeout(4000)
    check('IA) La IA usa el Contrato con Exodia', ev("duel.ai.monsterZones.some(z=>z&&z.cardId==='necro')"), log())

    # ---- BIBLIOTECA / CLÁSICOS ----
    setup(hand=['pot','pot','pot'], pM=[['lib','defense']], deck=['m1']*10)
    for _ in range(3): cast('pot')
    check('BIBLIOTECA) Gana 1 Contador por cada Mágica (3/3)', ev("duel.player.monsterZones[0].spellCounters")==3, log())
    check('BIBLIOTECA) Se ve el contador en la zona', '3/3' in pg.locator('#p_mon_row .zone-badge').first.inner_text())
    h=ev("duel.player.hand.length"); pg.evaluate("onFieldMonsterClick(duel.player,0)"); pg.wait_for_timeout(200); click('Contadores de Magia')
    check('BIBLIOTECA) Quita 3 y roba 1', ev("duel.player.monsterZones[0].spellCounters")==0 and ev("duel.player.hand.length")==h+1, log())
    check('BIBLIOTECA) Los contadores se sincronizan por red', ev("sanitizeZone(Object.assign({}, duel.player.monsterZones[0], {spellCounters:2})).spellCounters")==2)
    setup(pM=[['m1']], aM=[['big']], active='ai', phase='Battle')
    resolve('wab'); lp=ev("duel.player.lp")
    pg.evaluate("performAttack(duel.ai, 0, 0, ()=>{})"); pg.wait_for_timeout(2500)
    check('WABOKU) Tu monstruo no se destruye y no recibes daño', ev("!!duel.player.monsterZones[0]") and ev("duel.player.lp")==lp, [log(), ev("duel.player.lp")])
    pg.evaluate("finishTurn()"); pg.wait_for_timeout(300)
    check('WABOKU) Se acaba al final del turno', ev("!duel.player._waboku"))
    setup(aM=[['big'],['m1']], active='ai', phase='Battle')
    resolve('roar'); lp=ev("duel.player.lp")
    pg.evaluate("aiBattlePhase(()=>{ window._bp=1; })"); pg.wait_for_timeout(1500)
    check('RUGIDO) La IA no puede atacar ese turno', ev("duel.player.lp")==lp and ev("window._bp===1"), log())
    setup(pM=[['big']], active='player', phase='Battle'); pg.evaluate("duel.player._roarLock=true")
    pg.evaluate("tryAttack(duel.player,0)"); pg.wait_for_timeout(200)
    check('RUGIDO) Tú tampoco puedes atacar si te lo aplican', any('Rugido' in d for d in DL[-2:]), DL[-2:])
    setup(gy=['weak','m1','weak','big','weak','m1'])
    pg.evaluate("sbAutoPick=true"); resolve('backup'); pg.wait_for_timeout(500); pg.evaluate("sbAutoPick=false")
    check('REFUERZO) Recupera 3 monstruos con 1500 ATK o menos', len(ev("duel.player.hand"))==3 and 'big' not in ev("duel.player.hand"), [ev("duel.player.hand"), log()])
    setup(gy=['weak','m1'])
    resolve('backup')
    check('REFUERZO) Sin 5 monstruos en el Cementerio no hace nada', len(ev("duel.player.hand"))==0)
    setup(hand=['sanct','m1'], aiHand=['m1'], deck=['m1']*10)
    cast('sanct')
    check('SANTIDAD) Ambos roban hasta tener 6', ev("duel.player.hand.length")==6 and ev("duel.ai.hand.length")==6, [ev("duel.player.hand.length"), ev("duel.ai.hand.length")])
    setup(deck=['big','weak','m1'])
    pg.evaluate("sbAutoPick=true; applyGYEffect(duel.player, 'tom', findCardDef('tom'), findCardDef('tom').gyEffect)"); pg.wait_for_timeout(800); pg.evaluate("sbAutoPick=false")
    check('TOMATE) Invoca del Deck un monstruo con ATK ≤1500', ev("duel.player.monsterZones.some(z=>z&&(z.cardId==='m1'||z.cardId==='weak'))") and ev("duel.player.deck.includes('big')"), log())

    # ---- DC y creador ----
    dcN=ev("autoDeckCost(findCardDef('necro')).total"); dcM=ev("autoDeckCost(findCardDef('manju')).total"); dcL=ev("autoDeckCost(findCardDef('lib')).total")
    check('DC) Los efectos nuevos suman DC', dcM>ev("autoDeckCost(findCardDef('m1')).total") and dcL>8 and dcN>20, [dcN,dcM,dcL])
    print('DC necross/manju/biblioteca:', dcN, dcM, dcL)
    pg.click('button[data-tab="tabCrear"]') if pg.locator('button[data-tab="tabCrear"]').count() else None
    has=ev("['m_kw_ritualFull','m_kw_ritualGY','m_kw_spellCounter','m_kw_necross'].every(id=>!!document.getElementById(id)) && ['prePreparationOfRites','advancedRitualArt','contractWithExodia','cardOfSanctity'].every(v=>!!document.querySelector('#s_func option[value=\"'+v+'\"]')) && ['waboku','threateningRoar','backupSoldier'].every(v=>!!document.querySelector('#t_func option[value=\"'+v+'\"]')) && !!document.querySelector('#m_trigger option[value=\"searchRitualOnSummon\"]') && !!document.querySelector('#gy_effect option[value=\"summonAtkLowFromDeck\"]')")
    check('CREADOR) Todas las opciones nuevas están en el creador', has)
    print('page errors:', errs)
    check('Sin errores de página', not errs, errs)
    print(f'{sum(res)}/{len(res)}')
    b.close()
