from playwright.sync_api import sync_playwright
from net_helpers import F
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def M(i,dc): return {"id":i,"kind":"monster","name":"Carta "+i,"image":None,"finish":"normal","deckCost":dc,"dcManual":True,"monster":{"attribute":"LUZ","race":"Guerrero","category":"Normal","level":4,"atk":1000,"def":1000,"materials":"","effectText":"","trigger":"none"}}
with sync_playwright() as p:
    b=p.chromium.launch(); pages=[]
    for role,dc in (('host',5),('guest',10)):
        ctx=b.new_context(viewport={'width':1200,'height':900}); pg=ctx.new_page(); pg.errs=[]; pg.dl=[]
        pg.on('pageerror', lambda e, pg=pg: pg.errs.append(str(e))); pg.on('dialog', lambda d, pg=pg: (pg.dl.append(d.message), d.accept()))
        pg.goto(F); pg.wait_for_timeout(500)
        cards=[M(f'{role}{i}',dc) for i in range(14)]+[M(f'{role}cheap{i}',1) for i in range(14)]
        decks=[{'id':'heavy','name':'Pesado','main':[c['id'] for c in cards[:14]]*3,'extra':[]}, {'id':'light','name':'Ligero','main':[c['id'] for c in cards[14:]]*3,'extra':[]}]
        for d in decks: d['main']=d['main'][:40]
        pg.evaluate("([c,d])=>{ localStorage.setItem('yugioh_collection_v1', JSON.stringify(c)); localStorage.setItem('yugioh_decks_v1', JSON.stringify(d)); }", [cards,decks])
        pg.reload(); pg.wait_for_timeout(700); pg.click('button[data-tab="tabMultijugador"]'); pages.append(pg)
    h,g=pages
    h.click('#mpCreateBtn'); h.wait_for_function("document.getElementById('mpOfferOut').value.length>20", timeout=30000)
    g.click('#mpJoinBtn'); g.fill('#mpOfferIn', h.input_value('#mpOfferOut')); g.click('#mpGenAnswerBtn')
    g.wait_for_function("document.getElementById('mpAnswerOut').value.length>20", timeout=30000)
    h.fill('#mpAnswerIn', g.input_value('#mpAnswerOut')); h.click('#mpHostConnectBtn')
    for pg in (h,g): pg.wait_for_selector('#mpReadyPanel', state='visible', timeout=30000)
    # --- Modo emparejamiento ±150
    h.select_option('#mp_dcMode','match'); h.fill('#mp_dcTol','150'); h.dispatch_event('#mp_dcTol','change'); h.wait_for_timeout(600)
    check('El invitado recibe el Emparejamiento DC (±150)', g.evaluate("netState.dcMode.mode==='match' && netState.dcMode.tol===150"), g.evaluate("netState.dcMode"))
    check('El invitado no puede cambiar el modo', g.evaluate("document.getElementById('mp_dcMode').disabled"))
    # host 'heavy' = 40x5 = 200 ; guest 'heavy' = 40x5... guest cartas valen 5 tambien -> usar mazos distintos
    g.evaluate("populateMpDeckSelect()"); h.evaluate("populateMpDeckSelect()")
    h.select_option('#mp_myDeck','light'); h.click('#mpReadyBtn'); h.wait_for_timeout(300)   # host ligero: 40 DC... (min 5) => 200
    g.select_option('#mp_myDeck','heavy'); g.click('#mpReadyBtn'); g.wait_for_timeout(1500)  # guest pesado: 40x10 = 400
    hd=h.evaluate("netState.myDC"); gd=g.evaluate("netState.myDC"); print('   DC host', hd, 'guest', gd)
    check('Mazos con diferencia > 150 no empiezan el duelo', h.evaluate("!(typeof duel!=='undefined' && duel && duel.player && duel.player.hand.length>0)") and any('Emparejamiento DC' in m for m in g.dl) and any('Emparejamiento DC' in m for m in h.dl), (h.dl[-1:], g.dl[-1:]))
    check('Ambos pueden volver a tocar "Estoy listo"', not h.evaluate("document.getElementById('mpReadyBtn').disabled") and not g.evaluate("document.getElementById('mpReadyBtn').disabled"))
    g.select_option('#mp_myDeck','light'); g.click('#mpReadyBtn'); g.wait_for_timeout(300)
    h.click('#mpReadyBtn')
    check('Mazos de peso parecido: el duelo empieza', h.wait_for_function("typeof duel!=='undefined' && duel && duel.player && duel.player.hand.length>0", timeout=20000) is not None)
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
