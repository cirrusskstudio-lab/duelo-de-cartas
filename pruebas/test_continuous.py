import json
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
def M(i,n,atk,d=1000,lvl=4): return {"id":i,"kind":"monster","name":n,"image":None,"imageType":"image","finish":"normal","gyEffect":None,"tokenDef":None,"monster":{"attribute":"LUZ","race":"Guerrero","category":"Efecto","isExtra":False,"level":lvl,"atk":atk,"def":d,"materials":"","effectText":"x","trigger":"none"}}
def S(i,n,func,val=0,sub='Continua'): return {"id":i,"kind":"spell","name":n,"image":None,"imageType":"image","finish":"normal","gyEffect":None,"tokenDef":None,"spell":{"subtype":sub,"effectText":"x","func":func,"value":val}}
def T(i,n,func,cond,sub='Normal',val=0): return {"id":i,"kind":"trap","name":n,"image":None,"imageType":"image","finish":"normal","gyEffect":None,"tokenDef":None,"trap":{"subtype":sub,"cond":cond,"effectText":"x","func":func,"value":val}}
SUM='Cuando tu oponente invoca un monstruo'
cards=[M('m1','Guerrero A',1500),M('m2','Guerrero B',1800),S('auraA','Aura Continua','boostatk',500),S('drawC','Robo Continuo','draw',1),
       T('hole','Agujero Trampa','destroySummoned','Cuando tu oponente invoca un monstruo'),T('holeC','Agujero Continuo','destroySummoned',SUM,'Continua'),
       T('tdraw','Trampa Continua Robo','draw','En cualquier momento (libre)','Continua',1),T('tdest','Destructora','destroyTarget',SUM)]
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(F); pg.wait_for_timeout(400)
    pg.evaluate("(c)=>localStorage.setItem('yugioh_collection_v1', JSON.stringify(c))", cards); pg.reload(); pg.wait_for_timeout(600)
    pg.click('button[data-tab="tabDuelo"]')
    def setup(hand, aiST=None, plST=None, aiHand=None, active='player'):
        pg.evaluate("""([hand,aiST,plST,aiHand,active])=>{ cleanupAllTokens();
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck = Array(30).fill('m1'); ai.deck = Array(30).fill('m1'); player.hand = hand.slice(); ai.hand=(aiHand||[]).slice();
          (aiST||[]).forEach((x,i)=>ai.stZones[i]={cardId:x[0], faceup:x[1], setThisTurn:false});
          (plST||[]).forEach((x,i)=>player.stZones[i]={cardId:x[0], faceup:x[1], setThisTurn:false});
          duel = { player, ai, turn:2, activePlayer:active, phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""", [hand,aiST,plST,aiHand,active])
    def log(n=8): return pg.evaluate(f"duel.log.slice(0,{n})")
    def summon_first():
        pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(150)
        pg.locator('.choice-btn', has_text='Invocar en Ataque').first.click(); pg.wait_for_timeout(900)
    # 1) Trampa Continua: se activa y se queda boca arriba sin errores
    setup([], plST=[['tdraw',False]])
    hand0=pg.evaluate("duel.player.hand.length")
    pg.evaluate("onFieldSTClick(duel.player, 0)"); pg.wait_for_timeout(200)
    pg.locator('.choice-btn', has_text='Activar').first.click(); pg.wait_for_timeout(1500)
    check('Trampa Continua se queda boca arriba en el campo', pg.evaluate("!!(duel.player.stZones.find(z=>z&&z.cardId==='tdraw'&&z.faceup))"), log())
    check('Trampa Continua resolvió su efecto (robó 1)', pg.evaluate("duel.player.hand.length")==hand0+1, log())
    # 2) Aura continua
    setup(['m1','auraA'])
    summon_first()
    pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(150)
    pg.locator('.choice-btn', has_text='Activar ahora').first.click(); pg.wait_for_timeout(1500)
    atk=pg.evaluate("atkVal(duel.player.monsterZones.find(z=>z))")
    check('Mágica Continua de ATK da +500 mientras está en el campo', atk==2000, (atk, log()))
    pg.evaluate("(()=>{ const i=duel.player.stZones.findIndex(z=>z&&z.cardId==='auraA'); sendToGY(duel.player,'auraA'); duel.player.stZones[i]=null; })()")
    check('Al quitar la Continua se pierde el bonus', pg.evaluate("atkVal(duel.player.monsterZones.find(z=>z))")==1500)
    # 3) Continua de robo repite en Standby
    setup([], plST=[['drawC',True]])
    h=pg.evaluate("duel.player.hand.length")
    pg.evaluate("finishTurn()"); pg.wait_for_timeout(300)
    pg.evaluate("(()=>{ if(duel.activePlayer==='ai'){ finishTurn(); } })()"); pg.wait_for_timeout(1200)
    h2=pg.evaluate("duel.player.hand.length")
    check('Mágica Continua de robo se repite en tu Standby (robo normal + 1)', h2==h+2, (h,h2,log(10)))
    # 4) Tú invocas, la IA responde con Agujero Trampa
    setup(['m2'], aiST=[['hole',False]])
    pg.evaluate("Math.random=()=>0.1")
    summon_first(); pg.wait_for_timeout(800)
    check('La IA destruye tu invocación con su Trampa', pg.evaluate("duel.player.monsterZones.filter(z=>z).length")==0 and pg.evaluate("duel.ai.gy.includes('hole')"), log())
    # 5) La IA invoca y TÚ puedes activar tu Trampa (destroyTarget + condición de invocación)
    setup([], plST=[['tdest',False]], aiHand=['m2'], active='ai')
    pg.evaluate("window._aiDone=false; aiMainPhaseActions(()=>{window._aiDone=true;})"); pg.wait_for_timeout(900)
    opts=pg.locator('.choice-btn').all_inner_texts()
    check('Se te ofrece activar la Trampa cuando la IA invoca', any('Destructora' in o for o in opts), (opts, log()))
    check('La IA espera tu respuesta antes de seguir', not pg.evaluate("window._aiDone"))
    if any('Destructora' in o for o in opts): pg.locator('.choice-btn', has_text='Destructora').first.click(); pg.wait_for_timeout(1200)
    check('Tu Trampa destruye al monstruo invocado', pg.evaluate("duel.ai.monsterZones.filter(z=>z).length")==0, log())
    pg.wait_for_timeout(600)
    check('La IA continúa su turno después', pg.evaluate("window._aiDone"))
    # 6) Trampa Continua boca arriba destruye CADA invocación
    setup([], plST=[['holeC',True]], aiHand=['m1','m2'], active='ai')
    pg.evaluate("aiMainPhaseActions(()=>{})"); pg.wait_for_timeout(1200)
    pg.evaluate("duel.ai.normalSummonUsed=false; aiMainPhaseActions(()=>{})"); pg.wait_for_timeout(1200)
    check('Trampa Continua destruye cada invocación del rival', pg.evaluate("duel.ai.monsterZones.filter(z=>z).length")==0 and pg.evaluate("duel.ai.gy.filter(x=>x==='m1'||x==='m2').length")==2, log(10))
    check('La Trampa Continua sigue en el campo', pg.evaluate("!!duel.player.stZones.find(z=>z&&z.cardId==='holeC')"))
    print('errs', errs); print(f"{sum(res)}/{len(res)}")
