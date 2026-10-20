from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const cs=[
  {id:'n_harp', kind:'spell', name:'Plumero Red', image:null, finish:'normal', spell:{subtype:'Normal',effectText:'',func:'destroyAllOppST',value:0}},
  {id:'n_ctr', kind:'trap', name:'Destructora Red', image:null, finish:'normal', trap:{subtype:'Continua',cond:'En cualquier momento (libre)',effectText:'',func:'destroyTarget',value:0}},
  {id:'n_mon', kind:'monster', name:'Monstruo Red', image:null, finish:'normal', monster:{attribute:'LUZ',race:'Guerrero',category:'Normal',isExtra:false,level:4,atk:1500,def:1000,materials:'',effectText:'',trigger:'none'}},
  {id:'n_lava', kind:'monster', name:'Golem Red', image:null, finish:'normal', monster:{attribute:'FUEGO',race:'Demonio',category:'Efecto',isExtra:false,level:8,atk:3000,def:2500,materials:'',effectText:'',trigger:'none',handEffect:'lavaGolem',handValue:1000}}];
  cs.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    B.evaluate("(()=>{ duel.player.stZones=[{cardId:'n_ctr',faceup:false,setThisTurn:false},null,null,null,null]; renderDuel(); })()"); B.wait_for_timeout(600)
    A.evaluate("(()=>{ duel.player.hand=['n_harp','n_lava']; duel.player.monsterZones=[{cardId:'n_mon',position:'attack',faceup:true,atkMod:0,defMod:0},null,null,null,null]; renderDuel(); })()"); A.wait_for_timeout(1200)
    A.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('n_harp'))"); A.wait_for_timeout(1500)
    opts=B.locator('.choice-btn').all_inner_texts()
    check('B puede responder al Plumero con su trampa', any('Destructora Red' in o for o in opts), opts)
    B.locator('.choice-btn', has_text='Destructora Red').first.click(); B.wait_for_timeout(1500)
    if A.locator('.choice-btn', has_text='Pasar').count(): A.locator('.choice-btn', has_text='Pasar').first.click()
    A.wait_for_timeout(2500)
    check('Mientras B elige objetivo, A NO resuelve el Plumero', not A.evaluate("duel.log.some(m=>/Plumero Red|se destruyen/.test(m) && /destruyen \\d/.test(m))"), A.evaluate("duel.log.slice(0,5)"))
    tgt=B.locator('.choice-btn').all_inner_texts(); print('   objetivo:', tgt)
    B.locator('.choice-btn').first.click(); B.wait_for_timeout(4000)
    check('La trampa continua de B resolvió y luego el Plumero la destruyó (en el dispositivo de B)', B.evaluate("!duel.player.stZones.some(Boolean) && duel.player.gy.includes('n_ctr')"), B.evaluate("duel.log.slice(0,6)"))
    check('A ve el efecto de la trampa de B (perdió su monstruo)', A.evaluate("!duel.player.monsterZones.some(Boolean)"), A.evaluate("duel.log.slice(0,6)"))
    # Golem de Lava por red
    B.evaluate("(()=>{ duel.player.monsterZones=[{cardId:'n_mon',position:'attack',faceup:true,atkMod:0,defMod:0},{cardId:'n_mon',position:'attack',faceup:true,atkMod:0,defMod:0},null,null,null]; renderDuel(); })()"); B.wait_for_timeout(1500)
    A.evaluate("duel.player.normalSummonUsed=false"); A.evaluate("tryLavaGolem(duel.player, duel.player.hand.indexOf('n_lava'), findCardDef('n_lava'))"); A.wait_for_timeout(300)
    for _ in range(2):
        A.locator('.choice-btn').first.click(); A.wait_for_timeout(400)
    B.wait_for_timeout(2000)
    check('Golem de Lava aparece en el campo de B, con sus 2 monstruos tributados', B.evaluate("duel.player.monsterZones.filter(Boolean).map(z=>z.cardId)")==['n_lava'] and B.evaluate("duel.player.monsterZones.find(Boolean).lavaGolem")==True, B.evaluate("duel.player.monsterZones.map(z=>z&&z.cardId)"))
    lp=B.evaluate("duel.player.lp"); B.evaluate("processFieldDrawbacks(duel.player)")
    check('El Golem quema a B en su turno', B.evaluate("duel.player.lp")==lp-1000)
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
