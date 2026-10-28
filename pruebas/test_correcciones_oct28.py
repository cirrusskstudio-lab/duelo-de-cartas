# Correcciones del 28-oct: Xyz por Nivel, Extra Deck con 5 monstruos, Golem de Lava, Polimerización,
# Espadas Reveladoras, continuas 1 vez por turno, Jabalina Encantada y Cambio de Objetivo.
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
def M(i,n,atk=1500,d=1000,lvl=4,cat='Efecto',race='Guerrero',**kw):
    m={"attribute":"LUZ","race":race,"category":cat,"isExtra":cat in('Fusión','Sincronía','Xyz','Link'),"level":lvl,"atk":atk,"def":d,"materials":"","effectText":"x","trigger":"none"}; m.update(kw)
    return {"id":i,"kind":"monster","name":n,"image":None,"finish":"normal","monster":m}
def S(i,n,func,sub='Normal',val=0,**kw):
    sp={"subtype":sub,"effectText":"x","func":func,"value":val}; sp.update(kw)
    return {"id":i,"kind":"spell","name":n,"image":None,"finish":"normal","spell":sp}
def T(i,n,func,cond='Cuando tu oponente declara un ataque',sub='Normal',val=0):
    return {"id":i,"kind":"trap","name":n,"image":None,"finish":"normal","trap":{"subtype":sub,"cond":cond,"effectText":"x","func":func,"value":val}}
cards=[M('w4','Soldado Nv4',1500),M('w4b','Caballero Nv4',1600),M('w3','Escudero Nv3',1000,lvl=3),M('big','Gigante',2600,1000,lvl=7),M('wall','Muralla',0,2500,lvl=4),
  M('lava','Golem de Lava',3000,2500,lvl=8,handEffect='lavaGolem',handValue=1000),
  M('inbd','Indestructible Batalla',1000,1000,noBattleDestroy=True),M('ined','Inmune Efectos',1000,1000,noEffectDestroy=True),
  M('dbw','Dragón Blanco de Ojos Azules',3000,2500,lvl=8,race='Dragón'),
  M('xyz4','Xyz Rango 4',2500,2000,lvl=4,cat='Xyz',materials='2 monstruos de Nivel 4'),
  M('syn','Sincro',2500,2000,lvl=7,cat='Sincronía',materials='2 monstruos'),
  M('fusW','Fusión de Guerreros',2800,2000,lvl=6,cat='Fusión',materials='2 Guerreros'),
  M('fusD','Dragón Supremo',4500,3800,lvl=12,cat='Fusión',materials='Dragón Blanco + 1 monstruo Guerrero'),
  S('poly','Polimerización','polymerization'),S('harp','Plumero','destroyAllOppST'),
  S('swords','Espadas de Luz','none','Continua',swords={"enabled":True,"turns":3}),
  S('cdest','Destructora Continua','destroyTarget','Continua'),
  T('jav','Jabalina Encantada','enchantedJavelin'),T('shift','Cambio de Objetivo','shiftTarget')]
res=[]
def check(n,c,i=''):
    res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; DL=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d:(DL.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(500)
    pg.evaluate("(c)=>localStorage.setItem('yugioh_collection_v1', JSON.stringify(c))", cards); pg.reload(); pg.wait_for_timeout(900)
    pg.click('button[data-tab="tabDuelo"]')
    ev=pg.evaluate
    def setup(hand=[], pM=[], aM=[], pST=[], aST=[], extra=[], active='player', phase='Main1', deck=None, gy=[]):
        ev("duel && (duel.over=true)"); pg.wait_for_timeout(200)
        ev("""(a)=>{ cleanupAllTokens(); sbAutoPick=false; sbPick=null; document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); });
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck=(a.deck||Array(10).fill('w3')).slice(); ai.deck=Array(10).fill('w3'); player.hand=a.hand.slice(); player.extra=a.extra.slice(); player.gy=a.gy.slice();
          a.pM.forEach((x,i)=>{ if(x){ player.monsterZones[i]=emptyMonsterState(x[0],x[1]||'attack',x[2]!==false); player.monsterZones[i].summonedThisTurn=false; } });
          a.aM.forEach((x,i)=>{ if(x){ ai.monsterZones[i]=emptyMonsterState(x[0],x[1]||'attack',x[2]!==false); ai.monsterZones[i].summonedThisTurn=false; } });
          a.pST.forEach((x,i)=>{ if(x) player.stZones[i]={cardId:x[0], faceup:!!x[1], setThisTurn:!!x[2]}; });
          a.aST.forEach((x,i)=>{ if(x) ai.stZones[i]={cardId:x[0], faceup:!!x[1], setThisTurn:false}; });
          duel = { player, ai, turn:3, activePlayer:a.active, phase:a.phase, over:false, firstTurn:false, log:[], chainLinks:[], handLimit:9, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""",
          dict(hand=hand,pM=pM,aM=aM,pST=pST,aST=aST,extra=extra,active=active,phase=phase,deck=deck,gy=gy))
        pg.wait_for_timeout(150)
    def click(t):
        pg.locator('.choice-btn', has_text=t).first.click(); pg.wait_for_timeout(700)
    def names(side): return ev(f"duel.{side}.monsterZones.filter(Boolean).map(z=>findCardDef(z.cardId).name)")
    def extraSummon(name, mats):
        ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click(name)
        for m in mats: pg.locator('#matGrid .choice-btn').nth(m).click()
        if pg.locator('#matConfirm').count(): pg.locator('#matConfirm').click()
        pg.wait_for_timeout(600)
    ev("Math.random=()=>0.99")
    # ---- Xyz por Nivel ----
    setup(pM=[['w4'],['w3']], extra=['xyz4'])
    ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click('Xyz Rango 4'); pg.wait_for_timeout(300)
    check('XYZ) Con un Nivel 4 y un Nivel 3 NO deja hacer el Xyz de Rango 4', any('Rango 4' in d and 'Nivel 4' in d for d in DL[-1:]) and names('player')==['Soldado Nv4','Escudero Nv3'], DL[-1:])
    setup(pM=[['w4'],['w4b'],['w3'],['big'],['wall']], extra=['xyz4','syn'])
    extraSummon('Xyz Rango 4', [0,1])
    check('XYZ) Con 2 Nivel 4 sí sale, aunque tengas las 5 zonas llenas', 'Xyz Rango 4' in names('player') and len(names('player'))==4, names('player'))
    ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click('Xyz Rango 4' if False else 'Sincro')
    opts=pg.locator('#matGrid .choice-btn').all_inner_texts()
    pg.locator('#matGrid .choice-btn').nth(0).click(); pg.locator('#matGrid .choice-btn').nth(1).click(); pg.locator('#matConfirm').click(); pg.wait_for_timeout(600)
    check('SINCRO) También sale con el campo lleno', 'Sincro' in names('player'), names('player'))
    setup(pM=[['w4','defense',False],['w4b']], extra=['xyz4'])
    ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click('Xyz Rango 4'); pg.wait_for_timeout(300)
    check('XYZ) Los monstruos boca abajo no cuentan como material Xyz', names('player')==['Caballero Nv4'] or len(ev("duel.player.monsterZones.filter(Boolean)"))==2, DL[-1:])
    # ---- Golem de Lava con indestructibles ----
    setup(hand=['lava'], aM=[['inbd'],['ined']])
    ev("tryLavaGolem(duel.player, 0, findCardDef('lava'))"); pg.wait_for_timeout(300)
    click('Indestructible'); click('Inmune')
    check('LAVA) Tributa monstruos que no se destruyen en batalla ni por efectos (tributar no es destruir)', names('ai')==['Golem de Lava'] and ev("duel.ai.gy.length")==2, [names('ai'), ev("duel.log.slice(0,3)")])
    # ---- Polimerización ----
    setup(hand=['poly','w4'], pM=[['w4b']], extra=['fusW'])
    ev("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(1500)
    if pg.locator('.material-picker .mat-auto').count(): pg.locator('.material-picker .mat-auto').click(); pg.wait_for_timeout(200); pg.locator('.material-picker .mat-ok').first.click(); pg.wait_for_timeout(800)
    check('POLI) Materiales «2 Guerreros» (en plural) desde mano y campo', names('player')==['Fusión de Guerreros'], [names('player'), ev("duel.log.slice(0,4)")])
    setup(pST=[['poly',False,True]], hand=['dbw','w4'], extra=['fusD'])
    ev("tryActivateSetST(duel.player,0)"); pg.wait_for_timeout(1500)
    if pg.locator('.material-picker .mat-auto').count(): pg.locator('.material-picker .mat-auto').click(); pg.wait_for_timeout(200); pg.locator('.material-picker .mat-ok').first.click(); pg.wait_for_timeout(800)
    check('POLI) Polimerización colocada este turno se puede activar (como en el juego real)', names('player')==['Dragón Supremo'], [names('player'), DL[-2:], ev("duel.log.slice(0,4)")])
    check('POLI) Material por nombre parcial: «Dragón Blanco» = «Dragón Blanco de Ojos Azules»', 'dbw' in ev("duel.player.gy"))
    setup(pST=[['poly',False]], pM=[['w4'],['w4b']], extra=['fusW'])
    DL.clear(); ev("openExtraDeckModal()"); pg.wait_for_timeout(300); click('Fusión de Guerreros'); pg.wait_for_timeout(1500)
    if pg.locator('.material-picker .mat-auto').count(): pg.locator('.material-picker .mat-auto').click(); pg.wait_for_timeout(200); pg.locator('.material-picker .mat-ok').first.click(); pg.wait_for_timeout(800)
    check('POLI) Desde el Extra Deck usa la Polimerización colocada en el campo', names('player')==['Fusión de Guerreros'], [names('player'), DL[-2:]])
    # ---- Espadas Reveladoras ----
    setup(hand=['swords'], aM=[['big','defense',False]])
    ev("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(1500)
    check('ESPADAS) Voltea al rival y lo bloquea 3 turnos', ev("duel.ai.monsterZones[0].faceup") and ev("swordsLockOn(duel.ai)")==3)
    check('ESPADAS) Se ve el contador en la carta', pg.locator('#p_st_row .zone-badge').count()==1)
    ev("duel.ai.stZones=[null,null,null,null,null]; duel.ai.hand=['harp']"); ev("duel.activePlayer='ai'; startChain(duel.ai, findCardDef('harp'), 'harp', 'spell', ()=>{ duel.ai.hand.splice(0,1); }, null)"); pg.wait_for_timeout(2500)
    if pg.locator('.choice-btn', has_text='No').count(): pg.locator('.choice-btn', has_text='No').first.click(); pg.wait_for_timeout(1500)
    check('ESPADAS) Si destruyen las Espadas, el rival vuelve a poder atacar', ev("swordsLockOn(duel.ai)")==0 and ev("duel.player.gy.includes('swords')"), [ev("swordsLockOn(duel.ai)"), ev("duel.log.slice(0,4)")])
    # ---- Continua: activarla cuenta como su uso del turno ----
    setup(hand=['cdest'], aM=[['w4'],['w4b']])
    ev("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(1200); click('Soldado'); pg.wait_for_timeout(800)
    ev("onFieldSTClick(duel.player, duel.player.stZones.findIndex(Boolean))"); pg.wait_for_timeout(300)
    o=pg.locator('.choice-btn').all_inner_texts()
    check('CONTINUA) Recién activada no se puede volver a usar el mismo turno', not any('otra vez' in x for x in o), o)
    ev("document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); }); duel.turn++; renderDuel()")
    ev("onFieldSTClick(duel.player, duel.player.stZones.findIndex(Boolean))"); pg.wait_for_timeout(300)
    check('CONTINUA) Al turno siguiente sí', any('otra vez' in x for x in pg.locator('.choice-btn').all_inner_texts()))
    # ---- Jabalina Encantada ----
    setup(pM=[['wall','defense']], aM=[['big']], pST=[['jav',False]], active='ai', phase='Battle')
    ev("performAttack(duel.ai,0,0,()=>{})"); pg.wait_for_timeout(800); click('Jabalina'); pg.wait_for_timeout(2500)
    check('JABALINA) Ganas LP igual al ATK del atacante (2600) y el ataque sigue', ev("duel.player.lp")==10600 and ev("duel.ai.gy.length")==0, [ev("duel.player.lp"), ev("duel.log.slice(0,5)")])
    # ---- Cambio de Objetivo ----
    setup(pM=[['w3'],['inbd']], aM=[['big']], pST=[['shift',False]], active='ai', phase='Battle')
    ev("performAttack(duel.ai,0,0,()=>{})"); pg.wait_for_timeout(800); click('Cambio'); pg.wait_for_timeout(700); click('Indestructible'); pg.wait_for_timeout(2500)
    check('CAMBIO) El ataque se desvía a tu otro monstruo: el débil sobrevive', 'Escudero Nv3' in names('player') and 'Indestructible Batalla' in names('player'), [names('player'), ev("duel.log.slice(0,6)")])
    check('CAMBIO) El daño se calcula contra el nuevo objetivo (2600-1000)', ev("duel.player.lp")==6400, ev("duel.player.lp"))
    setup(pM=[['big']], aM=[['w4'],['wall']], aST=[['shift',False]], active='player', phase='Battle')
    ev("sbAutoPick=false; Math.random=()=>0.1"); ev("tryAttack(duel.player,0)"); pg.wait_for_timeout(300); click('Soldado'); pg.wait_for_timeout(3000)
    check('CAMBIO IA) La IA desvía tu ataque a su monstruo más resistente', 'Soldado Nv4' in names('ai'), [names('ai'), ev("duel.log.slice(0,6)")])
    ev("Math.random=()=>0.99")
    # ---- creador ----
    check('CREADOR) Las trampas nuevas aparecen en el creador', ev("['enchantedJavelin','shiftTarget'].every(v=>!!document.querySelector('#t_func option[value=\"'+v+'\"]'))"))
    print('errores:', errs); check('Sin errores', not errs, errs)
    print(f'{sum(res)}/{len(res)}'); b.close()
