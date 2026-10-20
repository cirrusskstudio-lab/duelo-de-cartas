from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
CARDS = open('test_fusion_ui.py').read().split('CARDS = r"""')[1].split('"""')[0]
CARDS = CARDS.replace("window.__C.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); });",
  "for(let i=0;i<14;i++) window.__C.push(M('u_f'+i,'Relleno '+i,500,3)); window.__C.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection();")
DECK = """(function(){ const main=[]; for(let i=0;i<14;i++) for(let k=0;k<3;k++) main.push('u_f'+i);
 decks = decks.filter(d=>d.id!=='dtest'); decks.push({id:'dtest', name:'Prueba Fusión', main:main.slice(0,40), extra:['u_fus']}); saveDecks(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def pass_chain(pg, timeout=8000):
    pg.wait_for_timeout(1200)
    loc = pg.locator('.critical-decision .choice-btn', has_text='Pasar')
    if loc.count(): loc.first.click()
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS, DECK)
    actor = h if h.evaluate("duel.activePlayer")=='player' else g
    other = g if actor is h else h
    print('actor:', 'host' if actor is h else 'guest')
    actor.evaluate("""(()=>{ duel.phase='Main1'; duel.player.hand=['u_poly','u_sol','u_rit','u_rs','u_gig'];
       const z=emptyMonsterState('u_cab','attack',true); z.summonedThisTurn=false; duel.player.monsterZones=[z,null,null,null,null]; renderDuel(); })()""")
    actor.wait_for_timeout(800)
    # FUSIÓN
    actor.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('u_poly'))")
    pass_chain(other)
    actor.wait_for_selector('.material-picker', timeout=8000)
    actor.locator('.material-picker .choice-btn', has_text='Mano: Soldado').click()
    actor.locator('.material-picker .choice-btn', has_text='Campo: Caballero').click()
    actor.locator('.material-picker .mat-ok', has_text='Ataque').click()
    actor.wait_for_timeout(1500)
    mine = actor.evaluate("duel.player.monsterZones.map(z=>z&&findCardDef(z.cardId).name)")
    theirs = other.evaluate("duel.ai.monsterZones.map(z=>z&&findCardDef(z.cardId)&&findCardDef(z.cardId).name)")
    check('Fusión en red: aparece en mi campo', 'Dragón Fusión' in mine, mine)
    check('Fusión en red: el rival la ve', 'Dragón Fusión' in theirs, theirs)
    check('Rival ve materiales en mi Cementerio', sorted(other.evaluate("duel.ai.gy"))==sorted(['u_sol','u_cab','u_poly']), other.evaluate("duel.ai.gy"))
    check('Rival ve mi Extra Deck sin la Fusión', other.evaluate("duel.ai.extra.length")==0, other.evaluate("duel.ai.extra"))
    # RITUAL (Gigante Nivel 8 de la mano)
    actor.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('u_rs'))")
    pass_chain(other)
    actor.wait_for_selector('.material-picker', timeout=8000)
    actor.locator('.material-picker .mat-auto').click()
    actor.locator('.material-picker .mat-ok', has_text='Defensa').click()
    actor.wait_for_timeout(1500)
    theirs = other.evaluate("duel.ai.monsterZones.map(z=>z&&(findCardDef(z.cardId).name+':'+z.position))")
    check('Ritual en red: el rival ve al Monstruo Ritual en Defensa', 'Dragón Ritual:defense' in theirs, theirs)
    check('Ritual en red: Gigante tributado desde la mano', 'u_gig' in other.evaluate("duel.ai.gy"), other.evaluate("duel.ai.gy"))
    # sigue funcionando el duelo: pasar de fase
    check('Sin cadenas colgadas', actor.evaluate("duel.chainLinks.length")==0 and other.evaluate("duel.chainLinks.length")==0)
    for pg,nm in ((h,'host'),(g,'guest')):
        check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK")
    b.close()
