import json, os
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
big='data:image/gif;base64,'+('R0lGOD'*400000)   # ~2.4 MB por carta
def card(i): return {"id":f"g{i}","kind":"monster","name":f"Carta GIF {i}","image":big,"imageType":"gif","finish":"normal","monster":{"attribute":"LUZ","race":"Guerrero","category":"Normal","level":4,"atk":1000,"def":1000,"materials":"","effectText":"","trigger":"none"}}
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(); pg=ctx.new_page(); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: (dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(800)
    # Datos "viejos" en localStorage (como la versión anterior del juego)
    pg.evaluate("localStorage.setItem('yugioh_collection_v1', JSON.stringify([{id:'old1',kind:'spell',name:'Carta Vieja',image:null,finish:'normal',spell:{subtype:'Normal',effectText:'',func:'none',value:0}}])); localStorage.setItem('yugioh_decks_v1','[]');")
    pg.reload(); pg.wait_for_timeout(900)
    check('Usa IndexedDB', pg.evaluate("storageMode()")=='indexedDB')
    check('Migra la colección vieja de localStorage', pg.evaluate("collection.map(c=>c.name)")==['Carta Vieja'])
    check('Libera localStorage tras migrar', pg.evaluate("localStorage.getItem('yugioh_collection_v1')") is None)
    # Guardar ~12 MB de GIFs (imposible en localStorage)
    ok = pg.evaluate("(cs)=>{ cs.forEach(c=>collection.push(c)); return saveCollection(); }", [card(i) for i in range(5)])
    pg.wait_for_timeout(1500)
    check('Guarda más de 10 MB sin error', ok and not any('lleno' in m for m in dl), dl)
    mb = pg.evaluate("lsGet('yugioh_collection_v1').length")/1e6
    print('  tamaño guardado: %.1f MB' % mb)
    pg.reload(); pg.wait_for_timeout(1500)
    check('Después de recargar siguen las 6 cartas', pg.evaluate("collection.length")==6)
    check('Las imágenes GIF se conservan completas', pg.evaluate("collection.filter(c=>c.image && c.image.length>2000000).length")==5)
    pg.wait_for_timeout(800)
    info = pg.inner_text('#storageInfo')
    print('  medidor:', info.strip())
    check('Muestra el medidor de espacio', 'IndexedDB' in info)
    check('Sin errores JS', not errs, errs)
    print(f"{sum(res)}/{len(res)}")
