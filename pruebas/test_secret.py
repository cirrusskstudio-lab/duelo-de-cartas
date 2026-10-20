from playwright.sync_api import sync_playwright
exec(open('test_bugs_oct6.py').read().split('res=[]')[0])
import json, sys
SP='/tmp/claude-0/-home-claude/a6468e31-b5a9-51af-b43c-d4587a0deb49/scratchpad/'
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
EXTRA = """(()=>{ const M=(id,name,atk)=>({id, kind:'monster', name, image:null, finish:'normal', monster:{attribute:'TIERRA',race:'Guerrero',category:'Efecto',isExtra:false,pendulum:false,level:4,atk,def:2000,materials:'',effectText:'',trigger:'none'}});
 [M('u_boss','The Final BOSS',3000), M('u_kill','The Legend Killer',2800)].forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); })()"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h,tag in [(1366,900,'desk'),(390,844,'mob')]:
        pg=b.new_page(viewport={'width':w,'height':h}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(F); pg.wait_for_timeout(400); pg.evaluate(CARDS); pg.evaluate(EXTRA); pg.click('button[data-tab="tabDuelo"]')
        pg.evaluate("document.querySelector('header').style.position='static'")
        pg.evaluate(SETUP+"(%s)"%json.dumps(dict(hand=['u_boss','u_kill'], field=['u_sol'], aiField=['u_big','u_cab'], st=['u_sak'])))
        pg.evaluate("window.scrollTo(0, document.getElementById('turnBanner').getBoundingClientRect().top+scrollY-4)")
        pg.evaluate("tryNormalSummon(0,'attack',true)")
        pg.wait_for_timeout(700); pg.screenshot(path=SP+f'sec_intro_boss_{tag}.png')
        check(f'[{tag}] Final Boss: aparece la intro', pg.locator('.secret-intro-boss').count()==1)
        pg.wait_for_timeout(2600); pg.screenshot(path=SP+f'sec_boss_{tag}.png')
        check(f'[{tag}] Emblema del Toro bajo el tablero', pg.locator('#board2d .secret-emblem.secret-boss').count()==1)
        check(f'[{tag}] Coro a los lados', pg.locator('#board2d .secret-chant-boss span').count()>=4)
        # sigue jugable: se puede hacer clic en la zona
        pg.locator('[data-zonekey="player-monster-1"]').click(); pg.wait_for_timeout(200)
        check(f'[{tag}] El tablero sigue respondiendo a clics', pg.locator('.overlay .choice-btn').count()>0)
        pg.evaluate("document.getElementById('modalRoot').innerHTML=''")
        # Legend Killer al mismo tiempo (Invocación Especial para no gastar Normal)
        pg.evaluate("(()=>{ duel.player.hand=[]; const z=emptyMonsterState('u_kill','attack',true); duel.player.monsterZones[2]=z; renderDuel(); })()")
        pg.wait_for_timeout(3000); pg.screenshot(path=SP+f'sec_both_{tag}.png')
        check(f'[{tag}] Ambos emblemas a la vez', pg.locator('#board2d .secret-emblem').count()==2)
        # destruir Final Boss -> se apaga
        pg.evaluate("(()=>{ const i=duel.player.monsterZones.findIndex(z=>z&&z.cardId==='u_boss'); fxDestroyMonster(duel.player,i); renderDuel(); })()")
        pg.wait_for_timeout(1500)
        check(f'[{tag}] Al destruir al Final Boss su emblema desaparece', pg.locator('#board2d .secret-emblem.secret-boss').count()==0 and pg.locator('#board2d .secret-emblem.secret-killer').count()==1)
        pg.screenshot(path=SP+f'sec_killer_{tag}.png')
        pg.evaluate("(()=>{ duel.player.monsterZones=[null,null,null,null,null]; renderDuel(); })()")
        pg.wait_for_timeout(1400)
        check(f'[{tag}] Sin cartas secretas no queda nada', pg.locator('#board2d .secret-emblem, #board2d .secret-chant').count()==0)
        check(f'[{tag}] Sin errores', not errs, errs)
        pg.close()
    b.close()
print(f"{sum(res)}/{len(res)}")
