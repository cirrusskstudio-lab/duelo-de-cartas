from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
CARDS = r"""
(function(){
 const M=(id,name,atk,lvl,extra)=>Object.assign({id, kind:'monster', name, image:null, finish:'normal',
   monster:Object.assign({attribute:'LUZ',race:'Guerrero',category:'Efecto',isExtra:false,pendulum:false,level:lvl,atk,def:1000,materials:'',effectText:'',trigger:'none'}, extra||{})});
 const S=(id,name,spell)=>({id, kind:'spell', name, image:null, finish:'normal', spell:Object.assign({subtype:'Normal',effectText:'',func:'none',value:0},spell)});
 window.__C = [
  M('u_sol','Soldado',1000,4), M('u_cab','Caballero',1500,4), M('u_gig','Gigante',2000,8), M('u_dra','Dragoncito',1200,3,{race:'Dragón',attribute:'FUEGO'}),
  M('u_fus','Dragón Fusión',3000,7,{category:'Fusión',isExtra:true,materials:'Soldado + 1 monstruo Guerrero'}),
  M('u_rit','Dragón Ritual',2800,8,{category:'Ritual'}),
  S('u_poly','Polimerización',{func:'polymerization'}),
  S('u_rs','Ritual del Dragón',{subtype:'Ritual',ritual:{targetCardId:'u_rit',requirementMode:'level',levelRequired:8,specificCardIds:[]}}),
 ];
 window.__C.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); });
})();
"""
SETUP = r"""
(function(hand, field, extra){
  cleanupAllTokens();
  const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
  player.deck = Array(30).fill('u_sol'); ai.deck = Array(30).fill('u_sol');
  player.hand = hand.slice(); player.extra = extra.slice();
  field.forEach((id,i)=>{ const z=emptyMonsterState(id,'attack',true); z.summonedThisTurn=false; player.monsterZones[i]=z; });
  duel = { player, ai, turn:2, activePlayer:'player', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
  netState.active=false;
  document.getElementById('duelSetupPanel').style.display='none';
  document.getElementById('duelBoard').style.display='block';
  renderDuel();
})
"""
res=[]
def check(name, cond, info=''):
    res.append((name, bool(cond))); print(('✅' if cond else '❌'), name, info if not cond else '')
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000})
    errs=[]; dialogs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    def ondlg(d):
        dialogs.append(d.message); d.accept()
    pg.on('dialog', ondlg)
    pg.goto(F); pg.wait_for_timeout(700)
    pg.evaluate(CARDS)
    pg.click('button[data-tab="tabDuelo"]')
    def setup(hand, field, extra):
        pg.evaluate(SETUP+"(%s,%s,%s)"%(hand, field, extra)); pg.wait_for_timeout(150)
    def click_hand(cardid):
        idx = pg.evaluate("(id)=>duel.player.hand.indexOf(id)", cardid)
        pg.locator('#handArea .card').nth(idx).click(); pg.wait_for_timeout(150)
    def choice(text):
        pg.locator('.choice-btn', has_text=text).first.click(); pg.wait_for_timeout(250)
    def names():
        return pg.evaluate("duel.player.monsterZones.map(z=>z?(findCardDef(z.cardId).name+':'+z.position):null).filter(Boolean)")

    # 1. Fusión mano + campo con el selector manual
    setup(['u_poly','u_sol'], ['u_cab'], ['u_fus'])
    click_hand('u_poly'); choice('Activar ahora')
    pg.wait_for_selector('.material-picker', timeout=4000)
    check('Aparece el selector de materiales de Fusión', pg.locator('.material-picker').count()==1)
    ok_disabled = pg.locator('.material-picker .mat-ok').first.is_disabled()
    pg.locator('.material-picker .choice-btn', has_text='Mano: Soldado').click()
    check('Con 1 material el botón sigue bloqueado', pg.locator('.material-picker .mat-ok').first.is_disabled() and ok_disabled)
    pg.locator('.material-picker .choice-btn', has_text='Campo: Caballero').click()
    st = pg.inner_text('.material-picker .mat-status')
    check('Mano + campo = combinación válida', 'válida' in st, st)
    pg.locator('.material-picker .mat-ok', has_text='Defensa').click(); pg.wait_for_timeout(300)
    check('Fusión invocada en Defensa', names()==['Dragón Fusión:defense'], names())
    check('Materiales y Polimerización al Cementerio', sorted(pg.evaluate("duel.player.gy"))==sorted(['u_sol','u_cab','u_poly']), pg.evaluate("duel.player.gy"))
    check('Extra Deck vacío tras la Fusión', pg.evaluate("duel.player.extra.length")==0)

    # 2. Selección inválida (2 Caballeros no tienen "Soldado")
    setup(['u_poly','u_cab'], ['u_cab','u_sol'], ['u_fus'])
    click_hand('u_poly'); choice('Activar ahora'); pg.wait_for_selector('.material-picker')
    pg.locator('.material-picker .choice-btn', has_text='Mano: Caballero').click()
    pg.locator('.material-picker .choice-btn', has_text='Campo: Caballero').click()
    check('Caballero + Caballero no es válido (falta «Soldado»)', pg.locator('.material-picker .mat-ok').first.is_disabled())
    pg.locator('.material-picker .mat-auto').click()
    st = pg.inner_text('.material-picker .mat-status')
    check('Botón «Elegir automáticamente» encuentra una combinación', 'válida' in st, st)
    pg.locator('.material-picker .mat-ok', has_text='Ataque').click(); pg.wait_for_timeout(300)
    check('Fusión en Ataque tras autoelegir', 'Dragón Fusión:attack' in names(), names())

    # 3. Sin Polimerización: el Extra Deck lo impide
    dialogs.clear()
    setup([], ['u_cab','u_sol'], ['u_fus'])
    pg.click('#extraDeckBtn'); pg.wait_for_timeout(150); choice('Dragón Fusión'); pg.wait_for_timeout(200)
    check('Sin Polimerización aparece el aviso', any('Polimerización' in d for d in dialogs), dialogs)
    check('…y no se invoca nada', names()==['Caballero:attack','Soldado:attack'], names())

    # 4. Sin materiales no deja activar
    dialogs.clear()
    setup(['u_poly','u_dra'], [], ['u_fus'])
    click_hand('u_poly'); choice('Activar ahora'); pg.wait_for_timeout(200)
    check('Polimerización sin materiales válidos: aviso y no se gasta', any('No puedes activar' in d for d in dialogs) and 'u_poly' in pg.evaluate('duel.player.hand'), dialogs)

    # 5. Ritual desde la mano + campo, con regla de no sobrar tributos
    setup(['u_rit','u_rs','u_sol','u_gig'], ['u_cab'], [])
    click_hand('u_rit')
    choice('Activar "Ritual del Dragón"')
    pg.wait_for_selector('.material-picker', timeout=4000)
    pg.locator('.material-picker .choice-btn', has_text='Mano: Soldado').click()
    pg.locator('.material-picker .choice-btn', has_text='Campo: Caballero').click()
    pg.locator('.material-picker .choice-btn', has_text='Mano: Gigante').click()
    st = pg.inner_text('.material-picker .mat-status')
    check('Tributos de sobra bloqueados (4+4+8)', pg.locator('.material-picker .mat-ok').first.is_disabled() and 'sobra' in st, st)
    pg.locator('.material-picker .choice-btn', has_text='Mano: Gigante').click()
    st = pg.inner_text('.material-picker .mat-status')
    check('Mano (4) + campo (4) = 8 válido', not pg.locator('.material-picker .mat-ok').first.is_disabled(), st)
    pg.locator('.material-picker .mat-ok', has_text='Ataque').click(); pg.wait_for_timeout(300)
    check('Monstruo Ritual invocado', names()==['Dragón Ritual:attack'], names())
    check('Gigante sigue en la mano', 'u_gig' in pg.evaluate('duel.player.hand'))

    # 6. Monstruo Ritual no se puede invocar normal
    setup(['u_rit'], [], [])
    click_hand('u_rit')
    btns = pg.locator('.choice-btn').all_inner_texts()
    check('Monstruo Ritual: no ofrece Invocación Normal', not any('Invocar en Ataque' in t for t in btns), btns)
    pg.locator('.close-x').last.click()

    # 7. Hint del Creador
    pg.click('button[data-tab="tabColeccion"]'); pg.wait_for_timeout(200)
    pg.select_option('#c_kind', 'monster') if pg.locator('#c_kind').count() else None
    pg.select_option('#m_category', 'Fusión'); pg.fill('#m_materials', 'Soldado + 2 monstruos LUZ + Pepito Inexistente')
    txt = pg.inner_text('#m_materials_parsed')
    check('Creador: reconoce los materiales', '1× «Soldado»' in txt and '2 monstruos LUZ' in txt and 'Pepito Inexistente' in txt.split('⚠️')[-1], txt)
    pg.select_option('#m_category', 'Ritual')
    check('Creador: explica el Ritual', 'Mágica de Ritual' in pg.inner_text('#m_materials_parsed'))
    print('page errors:', errs)
    print(f"{sum(1 for r in res if r[1])}/{len(res)} OK")
    b.close()
