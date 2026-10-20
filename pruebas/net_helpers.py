F='file:///home/claude/duelo-de-cartas/docs/index.html'
def setup_pair(browser, card_setup_js, deck_js):
    pages=[]
    for role in ('host','guest'):
        ctx=browser.new_context(viewport={'width':1200,'height':900})
        pg=ctx.new_page(); pg.errs=[]; pg.dialogs=[]
        pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e)))
        def ondlg(d, pg=pg): pg.dialogs.append(d.message); d.accept()
        pg.on('dialog', ondlg)
        pg.goto(F); pg.wait_for_timeout(600)
        pg.evaluate(card_setup_js); pg.evaluate(deck_js)
        pg.click('button[data-tab="tabMultijugador"]')
        pages.append(pg)
    h,g=pages
    h.click('#mpCreateBtn'); h.wait_for_function("document.getElementById('mpOfferOut').value.length>20", timeout=30000)
    offer=h.input_value('#mpOfferOut')
    g.click('#mpJoinBtn'); g.fill('#mpOfferIn', offer); g.click('#mpGenAnswerBtn')
    g.wait_for_function("document.getElementById('mpAnswerOut').value.length>20", timeout=30000)
    h.fill('#mpAnswerIn', g.input_value('#mpAnswerOut')); h.click('#mpHostConnectBtn')
    for pg in (h,g): pg.wait_for_selector('#mpReadyPanel', state='visible', timeout=30000)
    for pg in (h,g):
        pg.evaluate("populateMpDeckSelect()"); pg.select_option('#mp_myDeck', 'dtest'); pg.click('#mpReadyBtn')
    for pg in (h,g): pg.wait_for_function("typeof duel!=='undefined' && duel && duel.player && duel.player.hand.length>0", timeout=30000)
    for pg in (h,g): pg.wait_for_timeout(1500)
    for pg in (h,g):
        pg.evaluate("document.querySelectorAll('.overlay').forEach(o=>{ if(o.offsetParent && /DUELO DE APUESTAS|Comienza/.test(o.textContent)) o.remove(); })")
    return h,g
