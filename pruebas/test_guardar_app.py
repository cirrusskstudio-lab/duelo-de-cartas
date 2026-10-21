# Guardar copia de seguridad: descarga normal en navegador y Filesystem+Share en la app Android (simulada).
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
res=[]
def check(n,c,i=''):
    res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(accept_downloads=True); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(900)
    with pg.expect_download() as dl: pg.click('#exportBackupBtn')
    check('Navegador: descarga la copia .json', dl.value.suggested_filename.endswith('.json'))
    # App Android simulada
    pg2=ctx.new_page(); DL=[]; pg2.on('dialog', lambda d:(DL.append(d.message), d.accept())); pg2.on('pageerror',lambda e:errs.append(str(e)))
    pg2.add_init_script("""window._calls=[]; window.Capacitor={ isNativePlatform:()=>true, getPlatform:()=>'android',
      registerPlugin:(n)=>({ writeFile:async(o)=>{ window._calls.push([n,'write',o.directory,o.path,o.data.length]); return {uri:'file:///cache/'+o.path}; },
                             share:async(o)=>{ window._calls.push([n,'share',o.files[0]]); return {}; },
                             addListener:()=>({}) }) };""")
    pg2.goto(F); pg2.wait_for_timeout(900)
    pg2.click('#exportBackupBtn'); pg2.wait_for_timeout(600)
    calls=pg2.evaluate("window._calls")
    check('App: guarda en Documentos y en caché', any(c[1]=='write' and c[2]=='DOCUMENTS' for c in calls) and any(c[1]=='write' and c[2]=='CACHE' for c in calls), calls)
    check('App: abre el menú Compartir con el archivo', any(c[1]=='share' and c[2].endswith('.json') for c in calls), calls)
    check('App: avisa dónde quedó la copia', any('Documentos' in d for d in DL), DL)
    check('Sin errores', not errs, errs)
    print(f'{sum(res)}/{len(res)}'); b.close()
