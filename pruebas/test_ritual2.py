from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':900}); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d:(dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(400)
    def mk_monster(name, lvl, cat='Efecto'):
        pg.select_option('#c_kind','monster'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name',name)
        pg.select_option('#m_category',cat); pg.fill('#m_level',str(lvl)); pg.click('#saveCardBtn'); pg.wait_for_timeout(150)
        return pg.evaluate("(n)=>collection.find(c=>c.name===n).id", name)
    R=mk_monster('Rey Ritual',8,'Ritual'); A=mk_monster('Sacerdote A',4); B=mk_monster('Sacerdote B',4); C=mk_monster('Gigante C',8)
    pg.select_option('#c_kind','spell'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name','Ritual Doble')
    pg.select_option('#s_subtype','Ritual'); pg.dispatch_event('#s_subtype','change'); pg.wait_for_timeout(100)
    pg.select_option('#s_ritual_target', R); pg.select_option('#s_ritual_mode','specific'); pg.dispatch_event('#s_ritual_mode','change')
    pg.select_option('#s_ritual_specific1', A); pg.select_option('#s_ritual_specific2', B)
    print('autotext:', pg.inner_text('#s_ritual_autotext'))
    pg.click('#saveCardBtn'); pg.wait_for_timeout(200)
    print(pg.evaluate("collection.find(c=>c.name==='Ritual Doble').spell.ritual"))
    S=pg.evaluate("collection.find(c=>c.name==='Ritual Doble').id")
    # level mode too
    pg.select_option('#c_kind','spell'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name','Ritual Nivel')
    pg.select_option('#s_subtype','Ritual'); pg.dispatch_event('#s_subtype','change'); pg.select_option('#s_ritual_target', R)
    pg.click('#saveCardBtn'); pg.wait_for_timeout(200)
    print(pg.evaluate("collection.find(c=>c.name==='Ritual Nivel').spell.ritual"))
    pg.click('button[data-tab="tabDuelo"]')
    pg.evaluate("""(ids)=>{ const [R,A,B,C,S]=ids; const player=makeEmptyPlayer('Tú',8000,false), ai=makeEmptyPlayer('IA',8000,true);
      player.deck=Array(20).fill(A); ai.deck=Array(20).fill(A); player.hand=[S,R,A,C]; player.monsterZones[0]=Object.assign(emptyMonsterState(B,'attack',true),{summonedThisTurn:false});
      duel={player,ai,turn:2,activePlayer:'player',phase:'Main1',over:false,firstTurn:false,log:[],chainLinks:[],handLimit:9,difficulty:'normal'};
      document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""", [R,A,B,C,S])
    pg.evaluate("Math.random=()=>0.99; tryActivateFromHandSpell(0)"); pg.wait_for_timeout(500)
    print('picker:', pg.locator('.material-picker').count(), pg.inner_text('.material-picker .hint') if pg.locator('.material-picker').count() else dl)
    pg.locator('.material-picker .choice-btn', has_text='Sacerdote A').click()
    print('only A ->', pg.inner_text('.material-picker .mat-status'), 'disabled', pg.locator('.material-picker .mat-ok').first.is_disabled())
    pg.locator('.material-picker .choice-btn', has_text='Sacerdote B').click()
    print('A+B ->', pg.inner_text('.material-picker .mat-status'), 'disabled', pg.locator('.material-picker .mat-ok').first.is_disabled())
    print(errs)
    b.close()
