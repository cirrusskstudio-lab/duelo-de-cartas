from playwright.sync_api import sync_playwright
exec(open('test_bugs_oct6.py').read().split('res=[]')[0])
import json
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch()
    for speed in ['normal','off','fast']:
        pg=b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(F); pg.wait_for_timeout(400); pg.evaluate(CARDS); pg.evaluate(f"setAnimSpeed('{speed}')"); pg.click('button[data-tab="tabDuelo"]')
        pg.evaluate(SETUP+"(%s)"%json.dumps(dict(field=['u_big','u_cab'], aiField=['u_sol'], phase='Battle')))
        pg.evaluate("performAttack(duel.player,0,0)"); pg.wait_for_timeout(300)
        pg.evaluate("performAttack(duel.player,1,null)")
        pg.wait_for_timeout(1600)
        check(f'[{speed}] LP en pantalla terminan en el valor real', pg.inner_text('#opp_lp')==f"Rival: {pg.evaluate('duel.ai.lp')} LP" and pg.evaluate('duel.ai.lp')==5000, pg.inner_text('#opp_lp'))
        check(f'[{speed}] No quedan restos de animación', pg.evaluate("document.querySelectorAll('.fx-ghost,.fx-shard,.fx-hold,.fx-showcase,.fx-spark,.fx-big-number').length")==0)
        check(f'[{speed}] Las cartas reales vuelven a verse', pg.evaluate("[...document.querySelectorAll('[data-zonekey] > .card')].every(c=>getComputedStyle(c).visibility==='visible')"))
        check(f'[{speed}] Sin errores', not errs, errs)
        pg.close()
    b.close()
print(f"{sum(res)}/{len(res)}")
