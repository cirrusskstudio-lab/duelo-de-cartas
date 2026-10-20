from playwright.sync_api import sync_playwright
from net_helpers import F
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def M(i,n): return {"id":i,"kind":"monster","name":n,"image":None,"finish":"normal","monster":{"attribute":"LUZ","race":"Guerrero","category":"Normal","level":4,"atk":1000,"def":1000,"materials":"","effectText":"","trigger":"none"}}
with sync_playwright() as p:
    b=p.chromium.launch(); pages=[]
    for role,cards in (('host',[M('h1','Carta Host 1'),M('h2','Carta Host 2'),M('h3','Carta Host 3')]),('guest',[M('g1','Carta Guest 1'),M('g2','Carta Guest 2')])):
        ctx=b.new_context(viewport={'width':1200,'height':900}); pg=ctx.new_page(); pg.errs=[]; pg.dl=[]
        pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e))); pg.on('dialog', lambda d, pg=pg: (pg.dl.append(d.message), d.accept()))
        pg.goto(F); pg.wait_for_timeout(500)
        pg.evaluate("(c)=>{ localStorage.setItem('yugioh_collection_v1', JSON.stringify(c)); localStorage.setItem('yugioh_decks_v1', JSON.stringify([{id:'d1',name:'Mazo',main:c.map(x=>x.id),extra:[]}])); }", cards)
        pg.reload(); pg.wait_for_timeout(600); pg.click('button[data-tab="tabMultijugador"]'); pages.append(pg)
    h,g=pages
    h.click('#mpCreateBtn'); h.wait_for_function("document.getElementById('mpOfferOut').value.length>20", timeout=30000)
    g.click('#mpJoinBtn'); g.fill('#mpOfferIn', h.input_value('#mpOfferOut')); g.click('#mpGenAnswerBtn')
    g.wait_for_function("document.getElementById('mpAnswerOut').value.length>20", timeout=30000)
    h.fill('#mpAnswerIn', g.input_value('#mpAnswerOut')); h.click('#mpHostConnectBtn')
    for pg in (h,g): pg.wait_for_selector('#mpReadyPanel', state='visible', timeout=30000)
    h.click('#mpTradeBtn'); h.wait_for_timeout(600)
    check('El rival ve abrirse la ventana de intercambio', g.locator('#tradeOverlay').count()==1)
    # host ofrece h2, guest ofrece g1
    h.locator('#trPick .card').nth(1).click(); h.wait_for_timeout(500)
    g.locator('#trPick .card').nth(0).click(); g.wait_for_timeout(500)
    check('El guest ve la oferta del host en vivo', g.locator('#trTheirs .card').count()==1 and 'Carta Host 2' in g.locator('#trTheirs').inner_text())
    check('El host ve la oferta del guest en vivo', 'Carta Guest 1' in h.locator('#trTheirs').inner_text())
    h.click('#trAcceptBtn'); h.wait_for_timeout(400)
    check('Con una sola aceptación no se cambia nada', h.evaluate("collection.length")==3 and g.evaluate("collection.length")==2)
    # guest cambia su oferta -> la aceptación del host se cae
    g.locator('#trPick .card').nth(1).click(); g.wait_for_timeout(500)
    check('Cambiar la oferta quita la aceptación', h.locator('#trAcceptBtn').is_enabled())
    h.click('#trAcceptBtn'); h.wait_for_timeout(300); g.click('#trAcceptBtn'); g.wait_for_timeout(1200)
    hn=h.evaluate("collection.map(c=>c.name).sort()"); gn=g.evaluate("collection.map(c=>c.name).sort()")
    print(hn, gn)
    check('Host: dio Host 2 y recibió Guest 1 y Guest 2', hn==['Carta Guest 1','Carta Guest 2','Carta Host 1','Carta Host 3'], hn)
    check('Guest: recibió Host 2 y dio sus dos cartas', gn==['Carta Host 2'], gn)
    check('Se guarda en el navegador (sobrevive a recargar)', h.evaluate("JSON.parse(lsGet('yugioh_collection_v1')).length")==4)
    check('El mazo del host ya no usa la carta dada', h.evaluate("JSON.parse(lsGet('yugioh_decks_v1'))[0].main.includes('h2')")==False)
    check('Ambos ven la pantalla de intercambio completado', h.locator('#tradeResultOverlay').count()==1 and g.locator('#tradeResultOverlay').count()==1)
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
