from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('dialog', lambda d: (dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(700)
    def make(kind, name, setup_fn):
        pg.click('button[data-tab="tabColeccion"]'); pg.wait_for_timeout(100)
        pg.evaluate("resetForm && resetForm()") if pg.evaluate("typeof resetForm==='function'") else None
        pg.select_option('#c_kind', kind); pg.dispatch_event('#c_kind','change')
        pg.fill('#c_name', name)
        setup_fn()
        if not pg.is_checked('#tok_enabled'):
            pg.check('#tok_enabled'); pg.wait_for_timeout(50)
        pg.fill('#tok_name', name+' Token'); pg.fill('#tok_atk','800'); pg.fill('#tok_def','600'); pg.fill('#tok_quantity','2')
        pg.click('#saveCardBtn'); pg.wait_for_timeout(200)
        return pg.evaluate("(n)=>{ const c=collection.find(c=>c.name===n); return c ? c.id : null }", name)
    def mon():
        pg.select_option('#m_category','Efecto'); pg.select_option('#m_trigger','generateTokenOnSummon'); pg.select_option('#m_level','4') if False else pg.fill('#m_level','4')
    mid = make('monster','Invocador Maker', mon)
    sid = make('spell','Mágica Tokens Maker', lambda: pg.select_option('#s_func','generateToken'))
    tid = make('trap','Trampa Tokens Maker', lambda: pg.select_option('#t_func','generateToken'))
    print('ids', mid, sid, tid, 'dialogs', dl)
    info = pg.evaluate("(ids)=>ids.map(id=>{ const c=findCardDef(id); return c && [c.kind, !!c.tokenDef, c.tokenDef&&c.tokenDef.quantity, c.monster&&c.monster.trigger, c.spell&&c.spell.func, c.trap&&c.trap.func]; })", [mid,sid,tid])
    print(info)
    check('Las 3 cartas guardan su Token', all(i and i[1] for i in info), info)
    pg.click('button[data-tab="tabDuelo"]')
    pg.evaluate("""(ids)=>{ cleanupAllTokens();
      const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
      player.deck = Array(30).fill(ids[0]); ai.deck = Array(30).fill(ids[0]);
      player.hand = [ids[0], ids[1], ids[2]];
      duel = { player, ai, turn:2, activePlayer:'player', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
      document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""", [mid,sid,tid])
    def toks(): return pg.evaluate("duel.player.monsterZones.filter(z=>z&&isTokenId(z.cardId)).length")
    def visible_tokens(): return pg.locator('#p_monsters .card, #playerMonsters .card').count()
    pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(150)
    pg.locator('.choice-btn', has_text='Invocar en Ataque').first.click(); pg.wait_for_timeout(500)
    check('Monstruo del Creador genera 2 Tokens', toks()==2, pg.evaluate("duel.log.slice(0,6)"))
    # mágica
    pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(150)
    pg.locator('.choice-btn', has_text='Activar ahora').first.click(); pg.wait_for_timeout(800)
    check('Mágica del Creador genera Tokens (quedan 2 zonas)', toks()==4, pg.evaluate("duel.log.slice(0,6)"))
    # trampa: colocar, luego activar
    pg.evaluate("(()=>{ duel.player.monsterZones=[duel.player.monsterZones[0],null,null,null,null]; renderDuel(); })()")
    pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(300)
    pg.evaluate("duel.player.stZones.forEach(z=>{ if(z) z.setThisTurn=false; }); renderDuel();")
    idx = pg.evaluate("duel.player.stZones.findIndex(z=>z)")
    pg.evaluate("(i)=>onFieldSTClick(duel.player, i)", idx); pg.wait_for_timeout(200)
    btns = pg.locator('.choice-btn').all_inner_texts(); print('ST options', btns)
    if btns: pg.locator('.choice-btn').first.click()
    pg.wait_for_timeout(800)
    check('Trampa del Creador genera Tokens', toks()==2, pg.evaluate("duel.log.slice(0,8)"))
    html_tokens = pg.evaluate("document.querySelectorAll('.card.token, .card.is-token, [data-token]').length")
    print('token DOM:', html_tokens, pg.evaluate("document.getElementById('playerMonsterRow') ? 1 : 0"))
    pg.screenshot(path='/tmp/claude-0/-home-claude/a6468e31-b5a9-51af-b43c-d4587a0deb49/scratchpad/tokens.png')
    print('errs', errs, 'dialogs', dl)
    print(f"{sum(res)}/{len(res)}")
