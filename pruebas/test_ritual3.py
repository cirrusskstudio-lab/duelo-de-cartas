from playwright.sync_api import sync_playwright
exec(open('test_ritual2.py').read().split('with sync_playwright')[0])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':900}); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d:(dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(400)
    res=[]
    def check(n,c,i=''): res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
    def mk_monster(name, lvl, cat='Efecto'):
        pg.select_option('#c_kind','monster'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name',name)
        pg.select_option('#m_category',cat); pg.fill('#m_level',str(lvl)); pg.click('#saveCardBtn'); pg.wait_for_timeout(150)
        return pg.evaluate("(n)=>collection.find(c=>c.name===n).id", name)
    R=mk_monster('Rey Ritual',8,'Ritual'); A=mk_monster('Sacerdote A',4); B=mk_monster('Soldado B',4); C=mk_monster('Gigante C',8)
    def mk_ritual(name, mode, s1, s2, lvl=None):
        pg.select_option('#c_kind','spell'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name',name)
        pg.select_option('#s_subtype','Ritual'); pg.dispatch_event('#s_subtype','change'); pg.wait_for_timeout(80)
        pg.select_option('#s_ritual_target', R); pg.select_option('#s_ritual_mode',mode); pg.dispatch_event('#s_ritual_mode','change')
        if lvl: pg.fill('#s_ritual_level', str(lvl))
        if s1: pg.select_option('#s_ritual_specific1', s1)
        pg.select_option('#s_ritual_specific2', s2)
        txt = pg.inner_text('#s_ritual_autotext')
        pg.click('#saveCardBtn'); pg.wait_for_timeout(150)
        return pg.evaluate("(n)=>collection.find(c=>c.name===n).id", name), txt
    S1, t1 = mk_ritual('Ritual A + otro', 'specific', A, '__any__')
    check('Creador: opción «cualquier otro monstruo» y texto', 'otro monstruo cualquiera' in t1 and '2 tributos' in t1, t1)
    check('Se guarda como [A, __any__]', pg.evaluate("(id)=>findCardDef(id).spell.ritual.specificCardIds", S1)==[A,'__any__'])
    S2, t2 = mk_ritual('Ritual A + Nivel', 'specificLevel', A, '', 8)
    check('Creador: modo «obligatoria + Nivel» muestra ambos campos', 'DEBEN incluir' in t2 and pg.evaluate("1"), t2)
    # editar la carta 1 recarga opciones
    pg.evaluate("(id)=>{ const el=[...document.querySelectorAll('#collectionGrid .card')]; }", S1)
    pg.click('button[data-tab="tabDuelo"]')
    def duel(hand, field):
        pg.evaluate("""(o)=>{ const player=makeEmptyPlayer('Tú',8000,false), ai=makeEmptyPlayer('IA',8000,true);
          player.deck=Array(20).fill(o.A); ai.deck=Array(20).fill(o.A); player.hand=o.hand.slice();
          o.field.forEach((id,i)=>{ player.monsterZones[i]=Object.assign(emptyMonsterState(id,'attack',true),{summonedThisTurn:false}); });
          duel={player,ai,turn:2,activePlayer:'player',phase:'Main1',over:false,firstTurn:false,log:[],chainLinks:[],handLimit:9,difficulty:'normal'};
          document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""", dict(A=A, hand=hand, field=field))
        pg.evaluate("Math.random=()=>0.99")
    dl.clear(); duel([S1,R,A],[]); pg.evaluate("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(300)
    check('Solo con «Sacerdote A»: el Ritual NO se puede activar', any('No puedes activar' in d for d in dl) and pg.locator('.material-picker').count()==0, dl)
    duel([S1,R,A],[B]); pg.evaluate("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(300)
    pg.locator('.material-picker .choice-btn', has_text='Sacerdote A').click()
    check('Con 1 de 2 tributos el botón sigue bloqueado', pg.locator('.material-picker .mat-ok').first.is_disabled(), pg.inner_text('.material-picker .mat-status'))
    pg.locator('.material-picker .choice-btn', has_text='Soldado B').click()
    check('Con A + otro monstruo: válido', not pg.locator('.material-picker .mat-ok').first.is_disabled())
    pg.locator('.material-picker .mat-ok').first.click(); pg.wait_for_timeout(300)
    check('Ritual completado con 2 tributos', pg.evaluate("duel.player.monsterZones.filter(Boolean).map(z=>findCardDef(z.cardId).name)")==['Rey Ritual'] and len(pg.evaluate("duel.player.gy"))==3)
    duel([S2,R,C,B],[]); pg.evaluate("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(300)
    check('Modo obligatoria+Nivel sin la obligatoria: no se activa', pg.locator('.material-picker').count()==0)
    duel([S2,R,A,C],[B]); pg.evaluate("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(300)
    pg.locator('.material-picker .choice-btn', has_text='Gigante C').click()
    check('Gigante (Nivel 8) sin la obligatoria: no vale', pg.locator('.material-picker .mat-ok').first.is_disabled() and 'Falta incluir' in pg.inner_text('.material-picker .mat-status'), pg.inner_text('.material-picker .mat-status'))
    pg.locator('.material-picker .choice-btn', has_text='Gigante C').click()
    pg.locator('.material-picker .choice-btn', has_text='Sacerdote A').click(); pg.locator('.material-picker .choice-btn', has_text='Soldado B').click()
    check('A (4) + B (4) = 8 incluyendo la obligatoria: válido', not pg.locator('.material-picker .mat-ok').first.is_disabled())
    print('errs', errs); print(f"{sum(res)}/{len(res)}"); b.close()
