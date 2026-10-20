from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS, DECK)
    for X,Y in ((h,g),(g,h)):
        n = X.evaluate("duel.player.hand.length")
        Y.wait_for_timeout(300)
        check('Red: el rival ve cuántas cartas tengo', Y.inner_text('#oppHandCount')==str(n), [n, Y.inner_text('#oppHandCount')])
    A = h if h.evaluate("duel.activePlayer")=='player' else g; B = g if A is h else h
    A.evaluate("drawCard(duel.player); drawCard(duel.player); renderDuel();"); A.wait_for_timeout(1200)
    n = A.evaluate("duel.player.hand.length")
    check('Red: al robar se actualiza en el otro dispositivo', B.inner_text('#oppHandCount')==str(n), [n, B.inner_text('#oppHandCount')])
    check('Red: no se filtra ninguna carta', 'HIDDEN' not in B.inner_html('#oppHandRow') and 'u_' not in B.inner_html('#oppHandRow'))
    for pg in (h,g): check('Sin errores JS', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)}"); b.close()
