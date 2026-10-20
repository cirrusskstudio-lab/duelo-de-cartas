from playwright.sync_api import sync_playwright
exec(open('test_bugs_oct6.py').read().split('res=[]')[0])
SP='/tmp/claude-0/-home-claude/a6468e31-b5a9-51af-b43c-d4587a0deb49/scratchpad/'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h,tag in [(1300,900,'desk'),(390,844,'mob')]:
        pg=b.new_page(viewport={'width':w,'height':h}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(F); pg.wait_for_timeout(500); pg.evaluate(CARDS); pg.click('button[data-tab="tabDuelo"]')
        pg.evaluate(SETUP+"(%s)"%__import__('json').dumps(dict(hand=['u_sol'], aiHand=['u_big','u_sak','u_none','u_cab','u_sol'], field=['u_sol'], aiField=['u_big'])))
        check(f'[{tag}] Muestra 5 cartas del rival', pg.inner_text('#oppHandCount')=='5' and pg.locator('#oppHandCards .opp-hand-card').count()==5)
        check(f'[{tag}] No revela qué cartas son', 'Gigante' not in pg.inner_text('#oppHandRow') and 'u_big' not in pg.inner_html('#oppHandRow'))
        pg.evaluate("drawCard(duel.ai); renderDuel();")
        check(f'[{tag}] Al robar sube a 6', pg.inner_text('#oppHandCount')=='6')
        pg.evaluate("duel.ai.hand=[]; renderDuel();")
        check(f'[{tag}] Mano vacía = 0', pg.inner_text('#oppHandCount')=='0')
        pg.evaluate("duel.ai.hand=Array(15).fill('u_sol'); renderDuel();")
        check(f'[{tag}] 15 cartas: 12 reversos + «+3»', pg.locator('#oppHandCards .opp-hand-card').count()==12 and '+3' in pg.inner_text('#oppHandCards'))
        pg.evaluate("duel.ai.hand=Array(4).fill('u_sol'); renderDuel(); window.scrollTo(0, document.getElementById('turnBanner').getBoundingClientRect().top + scrollY - 10)")
        pg.wait_for_timeout(300); pg.screenshot(path=SP+f'opphand_{tag}.png')
        check(f'[{tag}] Sin errores', not errs, errs)
        pg.close()
    b.close()
print(f"{sum(res)}/{len(res)}")
