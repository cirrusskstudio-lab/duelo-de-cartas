from playwright.sync_api import sync_playwright
import sys
F='file://'+(sys.argv[1] if len(sys.argv)>1 else '/home/claude/duelo-de-cartas/docs/index.html')
def S(i,n,func,sub='Normal',val=0): return {"id":i,"kind":"spell","name":n,"image":None,"finish":"normal","spell":{"subtype":sub,"effectText":"","func":func,"value":val}}
def T(i,n,func,sub='Normal'): return {"id":i,"kind":"trap","name":n,"image":None,"finish":"normal","trap":{"subtype":sub,"cond":"En cualquier momento (libre)","effectText":"","func":func,"value":1}}
def M(i,n): return {"id":i,"kind":"monster","name":n,"image":None,"finish":"normal","monster":{"attribute":"LUZ","race":"Guerrero","category":"Normal","level":4,"atk":1500,"def":1000,"materials":"","effectText":"","trigger":"none"}}
cards=[S('harpie','Plumero de Harpía','destroyAllOppST'),T('ctrap','Trampa Continua Destructora','destroyTarget','Continua'),T('ntrap','Trampa Normal Robo','draw'),M('m1','Mon')]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(F); pg.wait_for_timeout(500)
    pg.evaluate("(c)=>localStorage.setItem('yugioh_collection_v1', JSON.stringify(c))", cards); pg.reload(); pg.wait_for_timeout(800)
    pg.click('button[data-tab="tabDuelo"]')
    pg.evaluate("""()=>{ const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
      player.deck=Array(30).fill('m1'); ai.deck=Array(30).fill('m1'); ai.hand=['harpie'];
      player.stZones[0]={cardId:'ctrap',faceup:false,setThisTurn:false}; player.stZones[1]={cardId:'ntrap',faceup:false,setThisTurn:false};
      ai.monsterZones[0]=emptyMonsterState('m1','attack',true);
      duel = { player, ai, turn:2, activePlayer:'ai', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
      document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""")
    # la IA activa el Plumero
    pg.evaluate("startChain(duel.ai, findCardDef('harpie'), 'harpie', 'spell', ()=>{ duel.ai.hand.splice(0,1); }, null)")
    pg.wait_for_timeout(500)
    print('opciones:', pg.locator('.choice-btn').all_inner_texts())
    pg.locator('.choice-btn', has_text='Trampa Continua Destructora').first.click(); pg.wait_for_timeout(500)
    print('opciones 2:', pg.locator('.choice-btn').all_inner_texts())
    if pg.locator('.choice-btn', has_text='Pasar').count(): pg.locator('.choice-btn', has_text='Pasar').first.click(); pg.wait_for_timeout(500)
    print('opciones 3 (elegir objetivo):', pg.locator('.choice-btn').all_inner_texts())
    print('campo en este momento:', pg.evaluate("duel.player.stZones.map(z=>z&&z.cardId)"), 'log:', pg.evaluate("duel.log.slice(0,6)"))
    if pg.locator('.choice-btn').count(): pg.locator('.choice-btn').first.click(); pg.wait_for_timeout(600)
    print('FINAL campo jugador:', pg.evaluate("duel.player.stZones.map(z=>z&&(z.cardId+(z.faceup?'(arriba)':'')))"), 'GY:', pg.evaluate("duel.player.gy"))
    print('log:', pg.evaluate("duel.log.slice(0,8)"))
    print(errs)
