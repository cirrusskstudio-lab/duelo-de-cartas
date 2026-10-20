from playwright.sync_api import sync_playwright
exec(open('test_fusion_net.py').read().split('res=[]')[0].replace('from net_helpers import setup_pair',''))
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':900}); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(F); pg.wait_for_timeout(600); pg.evaluate(CARDS); pg.evaluate(DECK)
    pg.click('button[data-tab="tabDuelo"]'); pg.wait_for_timeout(200)
    pg.evaluate("(()=>{ const sel=document.getElementById('duel_playerDeck'); if(![...sel.options].some(o=>o.value==='dtest')) sel.innerHTML += '<option value=\"dtest\">t</option>'; sel.value='dtest'; })()")
    pg.click('#startDuelBtn'); pg.wait_for_timeout(400)
    pg.evaluate("Math.random=()=>0.99")  # la IA no encadena trampas al azar
    info = pg.evaluate("""(()=>{ const pool=window._demoPool; const poly=pool.find(c=>c.spell&&c.spell.func==='polymerization');
      const mons=pool.filter(c=>c.kind==='monster'&&!c.monster.isExtra&&c.monster.level<=4).slice(0,2);
      duel.ai.hand=[poly.id, mons[0].id, mons[1].id]; duel.ai.deck = duel.ai.deck.filter(id=>{ const d=findCardDef(id); return d.kind==='monster'; });
      duel.player.monsterZones=[null,null,null,null,null]; return [poly.name, mons.map(m=>m.name), duel.ai.extra.map(id=>findCardDef(id).name)]; })()""")
    print('IA:', info)
    pg.click('#endTurnBtn')
    pg.wait_for_timeout(6000)
    print(pg.evaluate("[duel.activePlayer, duel.phase, duel.turn, duel.chainLinks.length, document.querySelectorAll('.overlay').length, [...document.querySelectorAll('.overlay')].map(o=>o.className+':'+o.textContent.slice(0,80))]"))
    print(pg.evaluate("duel.log.slice(0,12)"))
    pg.wait_for_function("duel.activePlayer==='player' && duel.turn>=2", timeout=30000)
    pg.wait_for_timeout(500)
    ai_field = pg.evaluate("duel.ai.monsterZones.map(z=>z&&findCardDef(z.cardId).name).filter(Boolean)")
    check('La IA hizo una Invocación por Fusión', 'Dragón Guerrero Supremo' in ai_field, ai_field)
    check('La IA no se quedó trabada (te devolvió el turno)', pg.evaluate("duel.activePlayer")=='player')
    check('Polimerización de la IA en su Cementerio', any('Polimeriz' in n for n in pg.evaluate("duel.ai.gy.map(id=>findCardDef(id).name)")))
    log = pg.evaluate("duel.log.slice(0,25)")
    print('\n'.join(l for l in log if 'Fusi' in l or 'Polimer' in l))
    check('Sin errores JS', not errs, errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
