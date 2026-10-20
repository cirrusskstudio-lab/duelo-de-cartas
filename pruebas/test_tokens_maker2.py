from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: (dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(600)
    pg.click('button[data-tab="tabColeccion"]')
    pg.select_option('#c_kind','spell'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name','Mágica sin efecto elegido')
    pg.check('#tok_enabled'); pg.fill('#tok_name','Soldadito'); pg.fill('#tok_atk','500'); pg.fill('#tok_def','500'); pg.fill('#tok_quantity','2')
    pg.click('#saveCardBtn'); pg.wait_for_timeout(300)
    c=pg.evaluate("collection.find(c=>c.name==='Mágica sin efecto elegido')")
    check('Se guarda con efecto Generar Token(s)', c and c['spell']['func']=='generateToken', c and c['spell'])
    check('Avisa del ajuste', any('Generar Token' in m for m in dl), dl)
    # monstruo Normal con token -> aviso y no guarda
    dl.clear()
    pg.select_option('#c_kind','monster'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name','Normal con token')
    pg.select_option('#m_category','Normal'); pg.dispatch_event('#m_category','change')
    if not pg.is_checked('#tok_enabled'): pg.check('#tok_enabled')
    pg.fill('#tok_name','X')
    pg.click('#saveCardBtn'); pg.wait_for_timeout(300)
    check('Normal + Token avisa y no guarda', pg.evaluate("!collection.find(c=>c.name==='Normal con token')") and any('Normal' in m for m in dl), dl)
    # duelo: activar la mágica
    sid=c['id']
    pg.click('button[data-tab="tabDuelo"]')
    pg.evaluate("""(sid)=>{ cleanupAllTokens(); const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
      player.deck = Array(30).fill(sid); ai.deck = Array(30).fill(sid); player.hand=[sid];
      duel = { player, ai, turn:2, activePlayer:'player', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
      document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""", sid)
    pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(150)
    pg.locator('.choice-btn', has_text='Activar ahora').first.click(); pg.wait_for_timeout(1500)
    n=pg.evaluate("duel.player.monsterZones.filter(z=>z&&isTokenId(z.cardId)).length")
    check('Al activarla pone 2 Tokens en el campo', n==2, pg.evaluate("duel.log.slice(0,6)"))
    print('errs', errs); print(f"{sum(res)}/{len(res)}")
