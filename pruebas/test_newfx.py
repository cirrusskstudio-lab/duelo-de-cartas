import json
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
def M(i,n,atk=1500,d=1000,lvl=4,cat='Efecto',**kw):
    m={"attribute":"LUZ","race":"Guerrero","category":cat,"isExtra":False,"level":lvl,"atk":atk,"def":d,"materials":"","effectText":"x","trigger":"none"}; m.update(kw)
    return {"id":i,"kind":"monster","name":n,"image":None,"finish":"normal","monster":m}
def S(i,n,func,sub='Normal',val=0,**kw):
    sp={"subtype":sub,"effectText":"x","func":func,"value":val}; sp.update(kw)
    return {"id":i,"kind":"spell","name":n,"image":None,"finish":"normal","spell":sp}
def T(i,n,func,cond='En cualquier momento (libre)',sub='Normal',val=0):
    return {"id":i,"kind":"trap","name":n,"image":None,"finish":"normal","trap":{"subtype":sub,"cond":cond,"effectText":"x","func":func,"value":val}}
cards=[M('m1','Soldado',1500),M('m2','Guardia',1800),M('lv5','Grande Nv5',2400,lvl=5),M('lv6','Grande Nv6',2500,lvl=6),M('weak','Débil',800),
  M('lava','Golem de Lava',3000,2500,lvl=8,handEffect='lavaGolem',handValue=1000),M('cyber','Dragón Ciber',2100,1600,lvl=5,handEffect='cyberDragon'),
  M('kuri','Kuribo',300,200,lvl=1,handEffect='kuriboh'),M('hon','Honesto',1100,1900,lvl=4,handEffect='honest'),M('ash','Ceniza',0,1800,lvl=3,handEffect='handNegate'),
  M('ddraw','Descarta-roba',100,100,lvl=1,handEffect='discardDraw',handValue=2),
  M('srch','Buscador',1000,1000,trigger='searchMonsterOnSummon'),M('burn','Quemador',2000,1000,trigger='battleBurn'),M('bdraw','Ladrón',2000,1000,trigger='battleDraw'),M('gyp','Necro',1000,1000,trigger='atkPerGY'),
  S('trun','Trunade','giantTrunade'),S('vort','Vórtice','lightningVortex'),S('reinf','Refuerzo','reinforcement'),S('shrink','Encoger','shrinkTarget','Rápida'),S('dbl','Doble Inv','doubleSummon'),S('draw2','Olla','draw',val=2),
  S('fmax','Campo Nv4','none','De Campo',fieldBoost={"race":None,"attribute":None,"atk":0,"def":0,"summonRule":{"mode":"maxLevel","level":4,"who":"both"}}),
  S('fnot','Campo SinTrib','none','De Campo',fieldBoost={"race":None,"attribute":None,"atk":0,"def":0,"summonRule":{"mode":"noTributeUpTo","level":6,"who":"self"}}),
  T('torr','Torrencial','torrentialTribute'),T('bott','Sin Fondo','bottomlessHole',val=1500),T('solemn','Juicio','solemnJudgment'),T('prison','Prisión','dimensionalPrison'),
  T('decree','Decreto','royalDecree',sub='Continua'),T('neg','Muro','negateAttack'),
  T('ctr','Destructora Continua','destroyTarget',sub='Continua'),S('harp','Plumero','destroyAllOppST')]
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); DL=[]; pg.on('dialog', lambda d: (DL.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(500)
    pg.evaluate("(c)=>localStorage.setItem('yugioh_collection_v1', JSON.stringify(c))", cards); pg.reload(); pg.wait_for_timeout(800)
    pg.click('button[data-tab="tabDuelo"]')
    def setup(hand=[], pM=[], aM=[], pST=[], aST=[], aiHand=[], active='player', phase='Main1', deck=None, field=None, aField=None):
        pg.evaluate("""(a)=>{ cleanupAllTokens(); document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); });
          const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
          player.deck = (a.deck||Array(20).fill('m1')).slice(); ai.deck = Array(20).fill('m1'); player.hand=a.hand.slice(); ai.hand=a.aiHand.slice();
          a.pM.forEach((x,i)=>{ if(x) player.monsterZones[i]=emptyMonsterState(x[0], x[1]||'attack', true); });
          a.aM.forEach((x,i)=>{ if(x) ai.monsterZones[i]=emptyMonsterState(x[0], x[1]||'attack', true); });
          a.pST.forEach((x,i)=>player.stZones[i]={cardId:x[0], faceup:x[1], setThisTurn:false});
          a.aST.forEach((x,i)=>ai.stZones[i]={cardId:x[0], faceup:x[1], setThisTurn:false});
          if(a.field) player.fieldZone={cardId:a.field}; if(a.aField) ai.fieldZone={cardId:a.aField};
          player.monsterZones.forEach(z=>{ if(z) z.summonedThisTurn=false; }); ai.monsterZones.forEach(z=>{ if(z) z.summonedThisTurn=false; });
          duel = { player, ai, turn:3, activePlayer:a.active, phase:a.phase, over:false, firstTurn:false, log:[], chainLinks:[], handLimit:9, difficulty:'normal' };
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""",
          dict(hand=hand,pM=pM,aM=aM,pST=pST,aST=aST,aiHand=aiHand,active=active,phase=phase,deck=deck,field=field,aField=aField))
    def log(n=8): return pg.evaluate(f"duel.log.slice(0,{n})")
    def opts(): return pg.locator('.choice-btn').all_inner_texts()
    def click(txt): pg.locator('.choice-btn', has_text=txt).first.click(); pg.wait_for_timeout(700)
    def handclick(i): pg.locator('#handArea .card').nth(i).click(); pg.wait_for_timeout(250)
    pg.evaluate("Math.random=()=>0.1")
    # 1) Continuas reutilizables
    setup(pST=[['ctr',True]], aM=[['m1'],['m2']])
    pg.evaluate("onFieldSTClick(duel.player,0)"); pg.wait_for_timeout(200)
    check('CONT) La continua boca arriba ofrece "usar su efecto otra vez"', any('otra vez' in o for o in opts()), opts())
    click('otra vez'); pg.wait_for_timeout(600); click('Monstruo rival'); pg.wait_for_timeout(800)
    check('CONT) Se usa y destruye 1 monstruo, y sigue en el campo', pg.evaluate("duel.ai.monsterZones.filter(Boolean).length")==1 and pg.evaluate("!!duel.player.stZones[0] && duel.player.stZones[0].faceup"), log())
    pg.evaluate("onFieldSTClick(duel.player,0)"); pg.wait_for_timeout(200)
    check('CONT) Solo 1 vez por turno', not any('otra vez' in o for o in opts()), opts())
    pg.evaluate("document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); }); duel.turn++; renderDuel();")
    pg.evaluate("onFieldSTClick(duel.player,0)"); pg.wait_for_timeout(200)
    check('CONT) Al turno siguiente se puede volver a usar', any('otra vez' in o for o in opts()), opts())
    # 2) Continua en Cadena + Plumero (orden correcto)
    setup(pST=[['ctr',False]], aM=[['m1']], aiHand=['harp'], active='ai')
    pg.evaluate("startChain(duel.ai, findCardDef('harp'), 'harp', 'spell', ()=>{ duel.ai.hand.splice(0,1); }, null)"); pg.wait_for_timeout(500)
    check('CHAIN) Pila de la Cadena visible', pg.locator('#chainStack .cs-link').count()==1)
    click('Destructora Continua'); pg.wait_for_timeout(400)
    still=pg.evaluate("duel.log.some(m=>/Plumero de Harp|Plumero: se destruyen/.test(m) && /destruyen/.test(m))")
    check('CHAIN) El Plumero espera a que elijas el objetivo de tu trampa', not still, log())
    click('Monstruo rival'); pg.wait_for_timeout(1500)
    check('CHAIN) Tu trampa continua resuelve y DESPUÉS el Plumero la destruye', pg.evaluate("duel.player.gy.includes('ctr') && !duel.player.stZones.some(Boolean)") and pg.evaluate("duel.ai.monsterZones.filter(Boolean).length")==0, log())
    check('CHAIN) La pila desaparece al terminar', pg.locator('#chainStack').count()==0)
    # 3) Golem de Lava
    setup(hand=['lava'], aM=[['m1'],['m2'],['weak']])
    handclick(0); click('campo del RIVAL'); pg.wait_for_timeout(300)
    click('zona'); pg.wait_for_timeout(300); click('zona'); pg.wait_for_timeout(500)
    st=pg.evaluate("duel.ai.monsterZones.map(z=>z&&[z.cardId, !!z.lavaGolem])")
    check('LAVA) Tributa 2 monstruos del rival y queda en SU campo', sum(1 for z in st if z)==2 and any(z and z[0]=='lava' and z[1] for z in st), st)
    lp=pg.evaluate("duel.ai.lp"); pg.evaluate("processFieldDrawbacks(duel.ai)")
    check('LAVA) Quema 1000 LP al rival en su turno', pg.evaluate("duel.ai.lp")==lp-1000, log())
    # 4) Reglas de campo
    setup(hand=['lv5','m1'], field='fmax')
    handclick(0); click('Invocar en Ataque')
    check('CAMPO) Prohíbe invocar Nivel 5 con "máximo Nivel 4"', pg.evaluate("duel.player.monsterZones.filter(Boolean).length")==0)
    pg.evaluate("document.querySelectorAll('.overlay').forEach(o=>{ if(o.id!=='mpQrScanOverlay') o.remove(); })")
    handclick(1); click('Invocar en Ataque')
    check('CAMPO) Nivel 4 sí se puede', pg.evaluate("duel.player.monsterZones.filter(Boolean).length")==1)
    check('CAMPO) Afecta también a la IA (no invoca Nivel 5)', pg.evaluate("summonBlockReason(duel.ai, findCardDef('lv5'))") is not None)
    setup(hand=['lv6'], field='fnot')
    handclick(0); click('Invocar en Ataque')
    check('CAMPO) "Sin Tributos hasta Nivel 6": Nivel 6 sale sin Tributos', pg.evaluate("duel.player.monsterZones.filter(Boolean).length")==1, log())
    # 5) Kuriboh
    setup(hand=['kuri'], aM=[['m2']], active='ai', phase='Battle')
    pg.evaluate("performAttack(duel.ai, 0, null)"); pg.wait_for_timeout(500)
    check('MANO) Kuriboh se ofrece al recibir un ataque directo', any('Kuribo' in o for o in opts()), opts())
    click('Kuribo'); pg.wait_for_timeout(900)
    check('MANO) Con Kuriboh no recibes daño', pg.evaluate("duel.player.lp")==8000 and pg.evaluate("duel.player.gy.includes('kuri')"), log())
    # 6) Honesto
    setup(hand=['hon'], pM=[['m1']], aM=[['m2']], active='ai', phase='Battle')
    pg.evaluate("performAttack(duel.ai, 0, 0)"); pg.wait_for_timeout(500)
    click('Honesto'); pg.wait_for_timeout(900)
    check('MANO) Honesto: tu monstruo gana el ATK del atacante y gana la batalla', pg.evaluate("!!duel.player.monsterZones[0]") and pg.evaluate("duel.ai.monsterZones.filter(Boolean).length")==0, log())
    pg.evaluate("finishTurn()"); pg.wait_for_timeout(300)
    check('MANO) El ATK extra dura solo ese turno', pg.evaluate("duel.player.monsterZones[0] ? atkVal(duel.player.monsterZones[0]) : -1")==1500)
    pg.evaluate("duel.over=true"); pg.wait_for_timeout(2500)
    # 7) Anular desde la mano en Cadena
    setup(hand=['ash'], aiHand=['draw2'], active='ai')
    h0=pg.evaluate("duel.ai.hand.length")
    pg.evaluate("startChain(duel.ai, findCardDef('draw2'), 'draw2', 'spell', ()=>{ duel.ai.hand.splice(0,1); }, null)"); pg.wait_for_timeout(400)
    check('MANO) El efecto de mano aparece como respuesta en la Cadena', any('efecto de mano' in o for o in opts()), opts())
    click('efecto de mano'); pg.wait_for_timeout(1500)
    check('MANO) Anula la Mágica del rival (no roba 2)', pg.evaluate("duel.ai.hand.length")==h0-1 and pg.evaluate("duel.player.gy.includes('ash')"), log())
    # 8) Dragón Cibernético
    setup(hand=['cyber'], aM=[['m1']])
    handclick(0); click('Invocar Especial desde la mano'); pg.wait_for_timeout(500)
    check('MANO) Dragón Cibernético se invoca de modo especial', pg.evaluate("duel.player.monsterZones.some(z=>z&&z.cardId==='cyber')") and not pg.evaluate("duel.player.normalSummonUsed"))
    # 9) Descartar para robar
    setup(hand=['ddraw'])
    handclick(0); click('Descartar esta carta'); pg.wait_for_timeout(400)
    check('MANO) Descartar: roba 2', pg.evaluate("duel.player.hand.length")==2 and pg.evaluate("duel.player.gy.includes('ddraw')"))
    # 10) Mágicas nuevas
    setup(hand=['trun'], pST=[['ctr',True]], aST=[['neg',False],['ctr',True]])
    handclick(0); click('Activar ahora'); pg.wait_for_timeout(900)
    if any('Pasar' in o for o in opts()): click('Pasar')
    pg.wait_for_timeout(1500)
    check('MAG) Trunade Gigante devuelve todas las M/T a la mano', pg.evaluate("!duel.player.stZones.some(Boolean) && !duel.ai.stZones.some(Boolean)") and pg.evaluate("duel.player.hand.includes('ctr') && duel.ai.hand.includes('ctr')"), log())
    setup(hand=['vort','m1'], aM=[['m1'],['m2','defense']])
    pg.evaluate("duel.ai.monsterZones[1].faceup=false; renderDuel();")
    handclick(0); click('Activar ahora'); pg.wait_for_timeout(600); click('Soldado'); pg.wait_for_timeout(1200)
    check('MAG) Vórtice: descarta 1 y destruye solo los boca arriba', pg.evaluate("duel.ai.monsterZones.filter(Boolean).length")==1 and pg.evaluate("duel.player.gy.includes('m1')"), log())
    setup(hand=['reinf'], deck=['m1','lv5','srch','m1'])
    handclick(0); click('Activar ahora'); pg.wait_for_timeout(800)
    if opts(): click(opts()[0])
    check('MAG) Refuerzo añade un monstruo de Nivel ≤4', pg.evaluate("duel.player.hand.some(id=>['m1','srch'].includes(id))") and pg.evaluate("duel.player.deck.length")==3, log())
    setup(hand=['shrink'], aM=[['m2']])
    handclick(0); click('Activar ahora'); pg.wait_for_timeout(600); click('Guardia'); pg.wait_for_timeout(900)
    check('MAG) Encoger: ATK a la mitad', pg.evaluate("atkVal(duel.ai.monsterZones[0])")==900, log())
    pg.evaluate("finishTurn()"); pg.wait_for_timeout(200)
    check('MAG) ...solo hasta el final del turno', pg.evaluate("atkVal(duel.ai.monsterZones[0])")==1800)
    pg.evaluate("duel.over=true"); pg.wait_for_timeout(2500)
    setup(hand=['dbl','m1','m2'])
    handclick(0); click('Activar ahora'); pg.wait_for_timeout(1000)
    print('   dbl log', log(4), opts())
    handclick(0); print('   opts1', opts()); click('Invocar en Ataque'); print('   DL', DL[-2:]); pg.wait_for_timeout(800); print('   hand', pg.evaluate("[duel.player.hand, duel.player.normalSummonUsed, duel.player.extraNormalSummons, document.querySelectorAll('#handArea .card').length, [...document.querySelectorAll('.overlay')].filter(o=>o.offsetParent).map(o=>o.className)]")); handclick(0); print('   opts2', opts()); click('Invocar en Ataque')
    check('MAG) Doble Invocación permite 2 Invocaciones Normales', pg.evaluate("duel.player.monsterZones.filter(Boolean).length")==2, log())
    # 11) Trampas nuevas (respuesta a invocación)
    for tid, name, expect in (('torr','Torrencial', "duel.ai.monsterZones.filter(Boolean).length===0 && duel.player.monsterZones.filter(Boolean).length===0"),
                              ('bott','Sin Fondo', "duel.ai.monsterZones.filter(Boolean).length===0 && duel.ai.banish.includes('m2')"),
                              ('solemn','Juicio', "duel.ai.monsterZones.filter(Boolean).length===0 && duel.player.lp===4000")):
        setup(pM=[['weak']], pST=[[tid,False]], aiHand=['m2'], active='ai')
        pg.evaluate("aiMainPhaseActions(()=>{})"); pg.wait_for_timeout(700)
        if any(name in o for o in opts()): click(name); pg.wait_for_timeout(900)
        check(f'TRAMPA) {name} responde a la invocación de la IA', pg.evaluate(expect), log())
    setup(pM=[['m1']], pST=[['prison',False]], aM=[['m2']], active='ai', phase='Battle')
    pg.evaluate("performAttack(duel.ai, 0, 0)"); pg.wait_for_timeout(500); click('Prisión'); pg.wait_for_timeout(500)
    if any('Pasar' in o for o in opts()): click('Pasar')
    pg.wait_for_timeout(1200)
    check('TRAMPA) Prisión Dimensional destierra al atacante', pg.evaluate("duel.ai.banish.includes('m2')") and pg.evaluate("!!duel.player.monsterZones[0]"), log())
    setup(pST=[['decree',True],['neg',False]])
    check('TRAMPA) Decreto Real bloquea las demás Trampas', pg.evaluate("trapsLocked()"))
    # 12) Monstruos nuevos
    setup(hand=['srch'], deck=['lv5','m2','m1'])
    handclick(0); click('Invocar en Ataque'); pg.wait_for_timeout(600)
    if opts(): click(opts()[0])
    check('MON) Al invocarse busca un monstruo Nv≤4', pg.evaluate("duel.player.hand.some(id=>['m2','m1'].includes(id))"), log())
    setup(pM=[['burn']], aM=[['m1']], phase='Battle')
    pg.evaluate("performAttack(duel.player, 0, 0)"); pg.wait_for_timeout(900)
    check('MON) Quemador: el rival pierde el ATK del destruido (500 batalla + 1500)', pg.evaluate("duel.ai.lp")==8000-500-1500, (pg.evaluate("duel.ai.lp"), log()))
    setup(pM=[['bdraw']], aM=[['m1']], phase='Battle')
    h=pg.evaluate("duel.player.hand.length"); pg.evaluate("performAttack(duel.player, 0, 0)"); pg.wait_for_timeout(900)
    check('MON) Ladrón: roba al destruir en batalla', pg.evaluate("duel.player.hand.length")==h+1)
    setup(pM=[['gyp']]); pg.evaluate("duel.player.gy=['m1','m2','harp']; renderDuel();")
    check('MON) +100 ATK por monstruo en el Cementerio', pg.evaluate("atkVal(duel.player.monsterZones[0])")==1200)
    # 13) DC de los efectos nuevos
    dc=lambda i: pg.evaluate("(i)=>cardDC(findCardDef(i))", i)
    print('   DC:', {k:dc(k) for k in ['lava','cyber','kuri','hon','ash','torr','bott','solemn','prison','decree','neg','vort','trun','fmax','fnot']})
    check('DC) Tributo Torrencial pesa mucho más que anular un ataque', dc('torr')>=dc('neg')+20)
    check('DC) Los efectos de mano suben el DC (Honesto > monstruo igual sin efecto)', dc('hon')>pg.evaluate("autoDeckCost(Object.assign({}, findCardDef('hon'), {monster:Object.assign({}, findCardDef('hon').monster, {handEffect:'none'})})).total")+10)
    check('DC) Campo con regla de nivel pesa más que un campo vacío', dc('fmax')>=12 and dc('fnot')>=10)
    print('errs', errs); print(f"{sum(res)}/{len(res)}")
