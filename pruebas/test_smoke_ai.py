from playwright.sync_api import sync_playwright
exec(open('test_fusion_net.py').read().split('res=[]')[0].replace('from net_helpers import setup_pair',''))
F='file:///home/claude/duelo-de-cartas/docs/index.html'
with sync_playwright() as p:
    b=p.chromium.launch()
    for run in range(5):
        pg=b.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
        pg.goto(F); pg.wait_for_timeout(500); pg.evaluate(CARDS); pg.evaluate(DECK)
        # el jugador usa el mazo de demostración real (con Polimerización)
        pg.evaluate("""(()=>{ const demo=buildDemoDeck(); window._demoPool=demo.pool; demo.pool.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); });
          decks.push({id:'ddemo',name:'demo',main:demo.main.slice(0,60),extra:demo.extra,freeMode:true}); })()""")
        pg.click('button[data-tab="tabDuelo"]')
        pg.evaluate("(()=>{ const sel=document.getElementById('duel_playerDeck'); sel.innerHTML += '<option value=\"ddemo\">d</option>'; sel.value='ddemo'; })()")
        pg.click('#startDuelBtn'); pg.wait_for_timeout(300)
        turns=0
        for t in range(8):
            if pg.evaluate("duel.over"): break
            # el jugador intenta: Polimerización/Ritual si puede, invocar el primer monstruo, luego atacar con todo
            pg.evaluate("""(()=>{ const p=duel.player; sbAutoPick=true;
              try{ const pi=p.hand.findIndex(id=>{const d=findCardDef(id); return d&&d.kind==='spell'&&isPolymerizationDef(d)&&!spellActivationBlockReason(p,d);}); if(pi>-1) tryActivateFromHandSpell(pi); }catch(e){console.error(e)}
              try{ const mi=p.hand.findIndex(id=>{const d=findCardDef(id); return d&&d.kind==='monster'&&!d.monster.isExtra&&d.monster.level<=4;}); if(mi>-1) tryNormalSummon(mi,'attack',true); }catch(e){console.error(e)}
              })()""")
            pg.wait_for_timeout(1500)
            pg.evaluate("sbAutoPick=false")
            pg.evaluate("document.querySelectorAll('.overlay').forEach(o=>{ if(o.offsetParent && !o.closest('#mpQrScanOverlay')) o.remove(); })")
            pg.click('#endTurnBtn'); pg.wait_for_timeout(150); pg.click('#nextPhaseBtn')
            ok=False
            for k in range(80):
                loc=pg.locator('.critical-decision .choice-btn', has_text='Pasar')
                if loc.count(): loc.first.click()
                loc=pg.locator('.critical-decision .choice-btn', has_text='No')
                if loc.count(): loc.first.click()
                if pg.evaluate("duel.over || duel.activePlayer==='player'"): ok=True; break
                pg.wait_for_timeout(250)
            if not ok:
                print('stuck', pg.evaluate("[duel.activePlayer,duel.phase,duel.log.slice(0,5),[...document.querySelectorAll('.overlay')].filter(o=>o.offsetParent).map(o=>o.textContent.slice(0,90))]")); break
            pg.wait_for_timeout(300)
            turns+=1
        log=pg.evaluate("duel.log.join(' | ')")
        print(f'run {run}: turns={turns} over={pg.evaluate("duel.over")} fusionesJugador={log.count("Invocación por Fusión! Tú")} fusionesIA={log.count("Invocación por Fusión! IA")} errs={errs}')
        pg.close()
    b.close()
