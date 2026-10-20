import json
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
d=json.load(open('/home/claude/intro/backup.json'))
col=d if isinstance(d,list) else [v for v in d.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'kind' in v[0]][0]
names=['ハリケーンを呼び寄せる！','Cody Preñado','Brock Lesnar']
cards=[c for c in col if c['name'] in names]
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda dd: (dl.append(dd.message), dd.accept()))
    pg.goto(F); pg.wait_for_timeout(500)
    pg.evaluate("(c)=>{ localStorage.setItem('yugioh_collection_v1', JSON.stringify(c)); }", cards)
    pg.reload(); pg.wait_for_timeout(700)
    info=pg.evaluate("collection.map(c=>[c.name, c.kind, c.spell&&c.spell.func, c.trap&&c.trap.func, c.monster&&c.monster.trigger])")
    print(info)
    hur=[c for c in cards if c['kind']=='trap'][0]['id']; cody=[c for c in cards if c['name']=='Cody Preñado'][0]['id']; brock=[c for c in cards if c['name']=='Brock Lesnar'][0]['id']
    check('Trampa normalizada a generateToken', pg.evaluate("(id)=>findCardDef(id).trap.func", hur)=='generateToken')
    check('Cody normalizado a generateTokenOnSummon', pg.evaluate("(id)=>findCardDef(id).monster.trigger", cody)=='generateTokenOnSummon')
    pg.click('button[data-tab="tabDuelo"]')
    pg.evaluate("""(ids)=>{ cleanupAllTokens();
      const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
      player.deck = Array(30).fill(ids[2]); ai.deck = Array(30).fill(ids[2]);
      player.hand = [ids[0], ids[1]];
      duel = { player, ai, turn:2, activePlayer:'player', phase:'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
      document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block'; renderDuel(); }""", [hur,cody,brock])
    def toks(): return pg.evaluate("duel.player.monsterZones.filter(z=>z&&isTokenId(z.cardId)).length")
    # trampa: colocar desde la mano y activarla
    pg.locator('#handArea .card').nth(0).click(); pg.wait_for_timeout(200)
    opts=pg.locator('.choice-btn').all_inner_texts(); print('hand opts', opts)
    set_btn=[o for o in opts if 'Colocar' in o]
    if set_btn: pg.locator('.choice-btn', has_text=set_btn[0]).first.click(); pg.wait_for_timeout(300)
    pg.evaluate("duel.player.stZones.forEach(z=>{ if(z) z.setThisTurn=false; }); renderDuel();")
    idx = pg.evaluate("duel.player.stZones.findIndex(z=>z)")
    pg.evaluate("(i)=>onFieldSTClick(duel.player, i)", idx); pg.wait_for_timeout(200)
    btns = pg.locator('.choice-btn').all_inner_texts(); print('ST options', btns)
    act=[x for x in btns if 'Activar' in x]
    if act: pg.locator('.choice-btn', has_text=act[0]).first.click(); pg.wait_for_timeout(1500)
    else:
        pg.evaluate("(id)=>new Promise(r=>resolveSpellTrapEffect(duel.player, findCardDef(id), r))", hur); pg.wait_for_timeout(500)
    check('Trampa "Hurricane" pone 3 Tokens en el campo', toks()==3, pg.evaluate("duel.log.slice(0,8)"))
    vis = pg.evaluate("[...document.querySelectorAll('.zone .card')].filter(e=>e.querySelector('.token-badge')).length")
    check('Los 3 Tokens se ven en el tablero', vis>=3, vis)
    # Cody: colocar boca abajo y voltear
    pg.evaluate("(()=>{ duel.player.monsterZones=[null,null,null,null,null]; cleanupAllTokens(); renderDuel(); })()")
    pg.evaluate("(id)=>{ duel.player.monsterZones[0]=emptyMonsterState(id,'defense',false); duel.player.monsterZones[0].faceDown=true; renderDuel(); }", cody)
    pg.evaluate("(id)=>{ const z=duel.player.monsterZones[0]; z.faceDown=false; z.position='attack'; applyFlipTrigger(duel.player, z, findCardDef(id)); renderDuel(); }", cody)
    pg.wait_for_timeout(800)
    check('Cody al voltearse genera Mini Orton', toks()==1, pg.evaluate("duel.log.slice(0,6)"))
    pg.screenshot(path='/tmp/claude-0/-home-claude/a6468e31-b5a9-51af-b43c-d4587a0deb49/scratchpad/tokens_user.png')
    print('errs', errs); print('dialogs', dl)
    print(f"{sum(res)}/{len(res)}")
