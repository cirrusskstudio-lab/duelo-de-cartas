from playwright.sync_api import sync_playwright
from net_helpers import setup_pair
exec(open('test_fusion_net.py').read().split('res=[]')[0].split('from net_helpers import setup_pair')[1])
EXTRA = """(()=>{ const tok={name:'Ficha Red', attribute:'OSCURIDAD', race:'Demonio', level:2, atk:700, def:700, position:'defense', quantity:2, allowedMaterials:{tribute:true}};
  const cs=[{id:'u_tsp', kind:'spell', name:'Mágica de Fichas', image:null, finish:'normal', tokenDef:tok, spell:{subtype:'Normal',effectText:'',func:'generateToken',value:0}},
   {id:'u_ttr', kind:'trap', name:'Trampa de Fichas', image:null, finish:'normal', tokenDef:tok, trap:{subtype:'Normal',cond:'',effectText:'',func:'generateToken',value:0}},
   {id:'u_tmo', kind:'monster', name:'Invocador de Fichas', image:null, finish:'normal', tokenDef:Object.assign({},tok,{quantity:1}), monster:{attribute:'LUZ',race:'Guerrero',category:'Efecto',isExtra:false,pendulum:false,level:4,atk:1000,def:1000,materials:'',effectText:'',trigger:'generateTokenOnSummon',triggerTiming:'onSummon'}}];
  cs.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); }); saveCollection(); })()"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch()
    h,g=setup_pair(b, CARDS+";"+EXTRA, DECK)
    A = h if h.evaluate("duel.activePlayer")=='player' else g
    B = g if A is h else h
    A.evaluate("(()=>{ duel.player.hand=['u_tmo','u_tsp']; duel.player.monsterZones=[null,null,null,null,null]; duel.player.stZones=[{cardId:'u_ttr',faceup:false,setThisTurn:false},null,null,null,null]; renderDuel(); })()")
    A.wait_for_timeout(800)
    A.evaluate("tryNormalSummon(duel.player.hand.indexOf('u_tmo'),'attack',true)"); A.wait_for_timeout(1200)
    tb = B.evaluate("duel.ai.monsterZones.filter(z=>z && /Ficha Red/.test((findCardDef(z.cardId)||{}).name||'')).length")
    check('Monstruo: el rival ve 1 Token', tb==1, B.evaluate("duel.ai.monsterZones.map(z=>z&&(findCardDef(z.cardId)||{}).name)"))
    A.evaluate("tryActivateFromHandSpell(duel.player.hand.indexOf('u_tsp'))"); A.wait_for_timeout(2500)
    tb = B.evaluate("duel.ai.monsterZones.filter(z=>z && /Ficha Red/.test((findCardDef(z.cardId)||{}).name||'')).length")
    check('Mágica: el rival ve 3 Tokens', tb==3, [tb, A.evaluate("duel.log.slice(0,5)")])
    A.evaluate("tryActivateSetST(duel.player, 0)"); A.wait_for_timeout(2500)
    ta = A.evaluate("duel.player.monsterZones.filter(Boolean).length")
    tb = B.evaluate("duel.ai.monsterZones.filter(Boolean).length")
    check('Trampa: campo lleno (5) en ambos lados', ta==5 and tb==5, [ta,tb])
    vis = B.evaluate("[...document.querySelectorAll('#oppMonsterZones .card, .opp-monsters .card')].length")
    print('cards visible opp rows', vis)
    for pg,nm in ((h,'host'),(g,'guest')): check(f'Sin errores JS ({nm})', not pg.errs, pg.errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
