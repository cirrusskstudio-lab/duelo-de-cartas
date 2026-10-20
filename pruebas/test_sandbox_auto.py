import sys, asyncio
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page()
    errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(800)
    pg.evaluate("runSandboxAutoTests()")
    pg.wait_for_function("!document.getElementById('sb_runTestsBtn').disabled && /pruebas correctas/.test(document.getElementById('sb_testSummary').textContent)", timeout=180000)
    print(pg.inner_text('#sb_testSummary'))
    fails=pg.evaluate("""[...document.querySelectorAll('#sb_testResults details')].map(d=>[...d.querySelectorAll('div > div')].filter(x=>x.textContent.trim().startsWith('❌')).map(x=>d.querySelector('summary').textContent+' :: '+x.textContent)).flat()""")
    for f in fails: print(f)
    cats=pg.evaluate("[...document.querySelectorAll('#sb_testResults summary')].map(s=>s.textContent)")
    print(cats)
    print('page errors:', errs)
    b.close()
