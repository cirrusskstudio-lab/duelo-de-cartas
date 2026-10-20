import json
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
def M(i,n,dc=None,extra=False,atk=1000,df=900,lvl=4,cat=None,**kw):
    m={"attribute":"LUZ","race":"Guerrero","category":cat or ("Fusión" if extra else "Efecto"),"isExtra":extra,"level":lvl,"atk":atk,"def":df,"materials":"","effectText":"","trigger":"none"}
    m.update(kw)
    c={"id":i,"kind":"monster","name":n,"image":None,"finish":"normal","monster":m}
    if dc is not None: c['deckCost']=dc; c['dcManual']=True
    return c
def S(i,n,func='draw',val=1,dc=None,sub='Normal'):
    c={"id":i,"kind":"spell","name":n,"image":None,"finish":"normal","spell":{"subtype":sub,"effectText":"","func":func,"value":val}}
    if dc is not None: c['deckCost']=dc; c['dcManual']=True
    return c
def T(i,n,func,cond='Cuando tu oponente declara un ataque',sub='Normal'):
    return {"id":i,"kind":"trap","name":n,"image":None,"finish":"normal","trap":{"subtype":sub,"cond":cond,"effectText":"","func":func,"value":0}}
cards=[M('A','Carta A',10),M('B','Carta B',20),S('C','Carta C',dc=5),M('D','Carta D (auto)',atk=1800,df=1000,cat='Normal'),M('X','Fusión X',30,True)]
filler=[M(f'f{i}',f'Relleno {i}',5) for i in range(20)]
auto=[T('mf','Fuerza Espejo','mirrorForce'),T('na','Solo anula ataque','negateAttack'),
      M('van','Vanilla 1800',atk=1800,df=1000,cat='Normal'),
      M('brk','Rota 3 efectos',atk=2400,df=2000,trigger='destroyOppMonsterOnSummon',noBattleDestroy=True,directAttack=True),
      M('ind','Indestructible',atk=2000,df=1500,noBattleDestroy=True,noEffectDestroy=True),
      M('b300','Sube 300',atk=2000,df=1500,trigger='boost300'),
      S('d4','Roba 4','draw',4),S('d2','Roba 2','draw',2),
      M('zero','Cero',atk=0,df=0,cat='Normal'),
      M('god','Dios roto',atk=5000,df=5000,lvl=4,trigger='destroyOppMonsterOnSummon',noBattleDestroy=True,noEffectDestroy=True,trapLock=True,doubleAttack=True,directAttack=True,ignoreLevelSpecial=True)]
old_deck={"id":"dold","name":"Mazo viejo","main":['A','A','A','B','B','C']+[f'f{i%20}' for i in range(34)],"extra":['X'],"freeMode":False}
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':1300,'height':1000}); pg=ctx.new_page(); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: (dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(600)
    legacy=[dict(c) for c in cards+filler+auto]
    pg.evaluate("([c,d])=>{ localStorage.setItem('yugioh_collection_v1', JSON.stringify(c)); localStorage.setItem('yugioh_decks_v1', JSON.stringify(d)); }", [legacy,[old_deck]])
    pg.reload(); pg.wait_for_timeout(900)
    dc=lambda i: pg.evaluate("(i)=>cardDC(cardById(i))", i)
    # --- DC automático
    print('   auto:', {k:dc(k) for k in ['mf','na','van','brk','ind','b300','d4','d2','zero','god','D']})
    check('AUTO) Fuerza Espejo pesa mucho más que una trampa que solo anula el ataque', dc('mf') >= dc('na')+20)
    check('AUTO) Monstruo roto con 3 efectos pesa mucho más que un vanilla de 1800', dc('brk') >= dc('van')+25)
    check('AUTO) Indestructible (batalla + efectos) pesa mucho más que uno que sube 300', dc('ind') >= dc('b300')+20)
    check('AUTO) Robar 4 pesa más que robar 2', dc('d4') > dc('d2'))
    check('AUTO) Mínimo 5 (0/0 sin efecto)', dc('zero')==5)
    check('AUTO) Máximo 80 (carta absurda)', dc('god')==80)
    check('AUTO) Todas las cartas quedan entre 5 y 80', all(5<=dc(c['id'])<=80 for c in auto))
    check('AUTO) Desglose explica de dónde sale el número', len(pg.evaluate("autoDeckCost(cardById('brk')).parts"))>=4)
    # --- migración / manual
    check('5) Carta vieja sin DC recibe DC automático', pg.evaluate("cardById('D').dcManual")==False and pg.evaluate("cardById('D').deckCost")==dc('D'))
    check('5) DC manual se respeta (A=10)', dc('A')==10)
    check('5) El mazo viejo sigue intacto (40 + 1 Extra)', pg.evaluate("decks[0].main.length")==40 and pg.evaluate("decks[0].extra.length")==1)
    check('2) Suma de copias: 3×10 + 2×20 + 1×5 = 75', pg.evaluate("calculateDeckCost({main:['A','A','A','B','B','C'],extra:[]}).total")==75)
    tot0=pg.evaluate("calculateDeckCost(decks[0]).total")
    check('2) Mazo viejo: 75 + 34×5 = 245 (el Extra no cuenta por defecto)', tot0==245, tot0)
    # --- constructor
    pg.click('button[data-tab="tabMazos"]'); pg.evaluate("openDeckEditor('dold')"); pg.wait_for_timeout(300)
    lbl=lambda: pg.inner_text('#dcTotalLabel')
    check('4) Constructor muestra DC total', '245' in lbl(), lbl())
    pg.locator('#deckSourceGrid .card').nth(1).click(); pg.wait_for_timeout(200)
    check('3) Al añadir una carta (B) el DC se actualiza en vivo (265)', '265' in lbl(), lbl())
    pg.locator('#deckMainCol .card').last.click(); pg.wait_for_timeout(200)
    check('3) Al quitarla vuelve a 245', '245' in lbl(), lbl())
    check('4) Etiqueta de DC en cada carta', pg.locator('#deckSourceGrid .dc-badge').count()==len(cards+filler+auto))
    bd=pg.inner_text('#dcBreakdown')
    check('4) DC por grupo', 'Monstruos' in bd and 'Mágicas' in bd and 'Extra: 30' in bd, bd)
    pg.evaluate("cardById('A').deckCost=15; saveCollection(); dcRefreshAll();"); pg.wait_for_timeout(200)
    check('6) Cambiar el DC de una carta actualiza el mazo (245 + 3×5 = 260)', '260' in lbl(), lbl())
    pg.evaluate("cardById('A').deckCost=10; saveCollection(); dcRefreshAll();")
    for n in (40,41,60):
        r=pg.evaluate("(m)=>{ const d={main:m,extra:[],freeMode:true}; return [validateDeck(d).mainOk, calculateDeckCost(d).total]; }", [f'f{i%20}' for i in range(n)])
        check(f'4) Mazo de {n} cartas válido y DC = {n*5}', r==[True,n*5], r)
    check('4) 39 cartas sigue siendo inválido', pg.evaluate("validateDeck({main:Array(39).fill('f1'),extra:[],freeMode:true}).mainOk")==False)
    # --- sin coste (con automático apagado)
    d={'main':['D','D','A'],'extra':[]}
    pg.evaluate("cardById('D').deckCost=null; cardById('D').dcManual=false;")
    check('8) Automático apagado: sin DC cuenta como 0', pg.evaluate("(d)=>calculateDeckCost(d, mergeDcConfig({auto:false})).total", d)==10)
    check('8) Automático apagado + valor por defecto 7 → 24', pg.evaluate("(d)=>calculateDeckCost(d, mergeDcConfig({auto:false, missing:'default', defaultCost:7})).total", d)==24)
    check('8) Automático apagado + "bloquear": impide el modo con límite', pg.evaluate("(d)=>dcCheckDeck(d,'force', mergeDcConfig({auto:false, missing:'block', maxDC:500})).ok", d)==False)
    pg.evaluate("migrateCardDC(cardById('D'))")
    # --- límites
    check('7) Por defecto el DC es informativo', pg.evaluate("dcCheckDeck(decks[0],'save').ok") and pg.evaluate("dcCfg.maxDC")==0)
    pg.evaluate("dcCfg.maxDC=200; dcCfg.enforce.save=true; saveDcConfig();")
    n_before=pg.evaluate("decks[0].main.length"); dl.clear()
    pg.locator('#deckSourceGrid .card').nth(1).click(); pg.wait_for_timeout(200)
    check('7) Con máximo 200 y bloqueo al guardar no deja añadir', pg.evaluate("decks[0].main.length")==n_before and any('No se puede añadir' in m for m in dl), dl)
    pg.evaluate("dcCfg.enforce.save=false; dcCfg.maxDC=0; saveDcConfig();")
    # --- listas
    txt=pg.evaluate("exportDeckList(decks[0])")
    r=pg.evaluate("(t)=>{ const r=parseDeckList(t); return [r.main.length, r.extra.length, r.unknown.length, calculateDeckCost({main:r.main,extra:r.extra}).total]; }", txt)
    check('6) Exportar e importar la lista reproduce el mazo (40 + 1, DC 245)', r==[40,1,0,245], r)
    pg.evaluate("dcCfg.enforce.import=true; dcCfg.maxDC=200; saveDcConfig();")
    rr=pg.evaluate("(t)=>importDeckListInto({id:'tmp',name:'t',main:[],extra:[],freeMode:true}, parseDeckList(t))", txt)
    check('7) Importar con límite 200 rechaza la lista de 245', rr['ok']==False, rr)
    pg.evaluate("dcCfg.enforce.import=false; dcCfg.maxDC=0; saveDcConfig();")
    # --- Emparejamiento contra la IA
    pg.click('button[data-tab="tabDuelo"]'); pg.evaluate("populateDeckSelect()"); pg.select_option('#duel_playerDeck','dold'); pg.select_option('#duel_mode','match'); dl.clear()
    pg.click('#startDuelBtn'); pg.wait_for_timeout(700)
    info=pg.evaluate("duel && duel.dcMode")
    print('   emparejamiento:', info, [m for m in pg.evaluate("duel.log") if 'Emparejamiento' in m])
    check('MATCH) La IA usa un mazo de 40 cartas de peso parecido (±250)', info and info.get('match') and abs(info['ai']-info['mine'])<=250 and pg.evaluate("duel.ai.deck.length+duel.ai.hand.length")==40, info)
    # mazo pesado: la IA también sube su peso
    pg.evaluate("(()=>{ decks.push({id:'dheavy',name:'Pesado',main:[].concat(...Array(3).fill(['god','brk','mf','ind','d4','mf','brk','god','ind','d4','b300','mf','brk','ind'])).slice(0,40),extra:[],freeMode:true}); saveDecks(); populateDeckSelect(); })()")
    pg.evaluate("document.getElementById('duelBoard').style.display='none'; document.getElementById('duelSetupPanel').style.display='block';")
    pg.select_option('#duel_playerDeck','dheavy'); pg.select_option('#duel_mode','match'); pg.click('#startDuelBtn'); pg.wait_for_timeout(700)
    info2=pg.evaluate("duel.dcMode"); print('   mazo pesado:', info2)
    check('MATCH) Con un mazo pesado la IA arma uno pesado (más cerca que el demo)', info2['ai'] > info['ai'] + 300, (info, info2))
    # --- reglas intactas
    def run_internal():
        pg.evaluate("document.getElementById('sb_testSummary').textContent=''; runSandboxAutoTests()")
        pg.wait_for_function("!document.getElementById('sb_runTestsBtn').disabled && /pruebas correctas/.test(document.getElementById('sb_testSummary').textContent)", timeout=180000)
        return pg.inner_text('#sb_testSummary')
    on=run_internal(); pg.evaluate("dcCfg.enabled=false; saveDcConfig();"); off=run_internal(); pg.evaluate("dcCfg.enabled=true; saveDcConfig();")
    check('9) Con DC activado o desactivado pasan las 103 pruebas de reglas', '119/119' in on and '119/119' in off, (on, off))
    before={c['id']:{k:v for k,v in c.items() if k not in ('deckCost','dcManual')} for c in cards+auto}
    after={c['id']:c for c in pg.evaluate("collection.map(c=>{ const x=JSON.parse(JSON.stringify(c)); delete x.deckCost; delete x.dcManual; return x; })")}
    check('10) Efectos, ATK y DEF intactos', all(json.dumps(before[k],sort_keys=True)==json.dumps(after[k],sort_keys=True) for k in before))
    # --- Creador: vista previa automática en vivo
    pg.click('button[data-tab="tabColeccion"]')
    pg.select_option('#c_kind','monster'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name','Nueva prueba DC')
    pg.select_option('#m_category','Efecto'); pg.dispatch_event('#m_category','change'); pg.fill('#m_atk','1800'); pg.fill('#m_def','1000'); pg.fill('#m_level','4'); pg.wait_for_timeout(400)
    n1=int(pg.inner_text('#c_dcAuto .dc-auto-num').split('\n')[0])
    pg.check('#m_kw_noBD'); pg.check('#m_kw_noED'); pg.wait_for_timeout(400)
    n2=int(pg.inner_text('#c_dcAuto .dc-auto-num').split('\n')[0])
    check('CREADOR) El DC se calcula en vivo y sube al marcar protecciones', n2>=n1+20, (n1,n2))
    pg.click('#saveCardBtn'); pg.wait_for_timeout(300)
    c=pg.evaluate("collection.find(c=>c.name==='Nueva prueba DC')")
    check('CREADOR) La carta se guarda con su DC automático', c and c['deckCost']==n2 and c['dcManual']==False, c and (c['deckCost'], n2))
    pg.evaluate("(()=>{ const c=collection.find(c=>c.name==='Nueva prueba DC'); loadCardIntoForm ? loadCardIntoForm(c) : null; })()") if pg.evaluate("typeof loadCardIntoForm==='function'") else None
    pg.click('#dcConfigBtnColl'); pg.wait_for_timeout(300)
    inp=pg.locator('#dcfRows input[data-id="van"]'); inp.fill('33'); pg.wait_for_timeout(500)
    check('TABLA) Poner DC a mano en la tabla', dc('van')==33 and pg.evaluate("cardById('van').dcManual")==True)
    pg.locator('[data-reset="van"]').click(); pg.wait_for_timeout(300)
    check('TABLA) ↺ lo regresa al automático', pg.evaluate("cardById('van').dcManual")==False and dc('van')==pg.evaluate("autoDeckCost(cardById('van')).total"))
    pg.click('#dcfClose')
    print('errs', errs); print(f"{sum(res)}/{len(res)}")
