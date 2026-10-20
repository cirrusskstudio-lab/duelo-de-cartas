from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
CARDS = r"""
(function(){
 const M=(id,name,atk,lvl,extra,top)=>Object.assign({id, kind:'monster', name, image:null, finish:'normal',
   monster:Object.assign({attribute:'LUZ',race:'Guerrero',category:'Efecto',isExtra:false,pendulum:false,level:lvl,atk,def:1000,materials:'',effectText:'',trigger:'none'}, extra||{})}, top||{});
 const T=(id,name,func)=>({id, kind:'trap', name, image:null, finish:'normal', trap:{subtype:'Normal',cond:'',effectText:'',func,value:0}});
 const S=(id,name,spell)=>({id, kind:'spell', name, image:null, finish:'normal', spell:Object.assign({subtype:'Normal',effectText:'',func:'none',value:0},spell)});
 window.__C = [
  M('u_sol','Soldado',1000,4), M('u_cab','Caballero',1500,4), M('u_big','Gigante',2500,4),
  M('u_norm','Normal con efecto viejo',1200,4,{category:'Normal', trigger:'draw1'}),
  M('u_sang','Sangan',1000,3,null,{gyEffect:{trigger:'onSend', effect:'draw', value:1, targetCardId:null, restriction:'none', restrictionPhase:'Main1', condition:'', cost:'none', costLp:0}}),
  M('u_gym','Fénix manual',1000,4,null,{gyEffect:{trigger:'manual', effect:'specialSummonSelf', value:0, targetCardId:null, restriction:'oncePerTurn', restrictionPhase:'Main1', condition:'', cost:'none', costLp:0}}),
  T('u_sak','Sakuretsu','destroyAttacker'), T('u_none','Trampa narrativa','none'), T('u_none2','Otra narrativa','none'),
  S('u_narr','Mágica narrativa',{}),
 ];
 window.__C.forEach(c=>{ if(!collection.find(x=>x.id===c.id)) collection.push(c); });
})();
"""
SETUP = r"""
(function(o){
  cleanupAllTokens();
  const player = makeEmptyPlayer('Tú', 8000, false); const ai = makeEmptyPlayer('IA', 8000, true);
  player.deck = Array(30).fill('u_sol'); ai.deck = Array(30).fill('u_sol');
  player.hand = (o.hand||[]).slice(); ai.hand=(o.aiHand||[]).slice();
  (o.field||[]).forEach((id,i)=>{ const z=emptyMonsterState(id,'attack',true); z.summonedThisTurn=false; player.monsterZones[i]=z; });
  (o.aiField||[]).forEach((id,i)=>{ const z=emptyMonsterState(id,'attack',true); z.summonedThisTurn=false; ai.monsterZones[i]=z; });
  (o.st||[]).forEach((id,i)=>{ player.stZones[i]={cardId:id, faceup:false, setThisTurn:false}; });
  (o.aiSt||[]).forEach((id,i)=>{ ai.stZones[i]={cardId:id, faceup:false, setThisTurn:false}; });
  player.gy=(o.gy||[]).slice();
  duel = { player, ai, turn:2, activePlayer:o.active||'player', phase:o.phase||'Main1', over:false, firstTurn:false, log:[], chainLinks:[], handLimit:7, difficulty:'normal' };
  netState.active=false;
  document.getElementById('duelSetupPanel').style.display='none'; document.getElementById('duelBoard').style.display='block';
  renderDuel();
})
"""
res=[]
def check(name, cond, info=''):
    res.append(cond); print(('✅' if cond else '❌'), name, '' if cond else info)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':1000}); errs=[]; dl=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: (dl.append(d.message), d.accept()))
    pg.goto(F); pg.wait_for_timeout(600); pg.evaluate(CARDS); pg.click('button[data-tab="tabDuelo"]')
    def setup(**o): pg.evaluate(SETUP+"(%s)"%__import__('json').dumps(o)); pg.wait_for_timeout(100)
    def crit(text): pg.locator('.critical-decision .choice-btn', has_text=text).first.click(); pg.wait_for_timeout(300)

    # 1. Cadena real en batalla (vs IA)
    setup(field=['u_sol'], aiField=['u_big'], st=['u_sak','u_none2'], aiSt=['u_none'], active='ai', phase='Battle')
    pg.evaluate("Math.random=()=>0")   # la IA siempre responde
    pg.evaluate("performAttack(duel.ai, 0, 0)"); pg.wait_for_timeout(300)
    crit('Activar Sakuretsu')
    pg.wait_for_selector('.critical-decision', timeout=3000)
    title = pg.inner_text('.critical-decision h3')
    st = pg.evaluate("[duel.player.lp, !!duel.ai.monsterZones[0], !!duel.player.monsterZones[0], duel.chainLinks.length]")
    check('La IA responde (CL2) y me pregunta si respondo (CL3)', 'CL2' in title, title)
    check('…mientras tanto la batalla NO se ha resuelto', st==[8000, True, True, 2], st)
    crit('Pasar')
    pg.wait_for_timeout(600)
    st = pg.evaluate("[duel.player.lp, !!duel.ai.monsterZones[0], !!duel.player.monsterZones[0], duel.chainLinks.length]")
    check('Al cerrar la Cadena: Sakuretsu destruye al atacante y no hay daño', st==[8000, False, True, 0], [st, pg.evaluate('duel.log.slice(0,8)')])

    # 2. Trampa que no anula: la batalla ocurre DESPUÉS de resolver la Cadena
    setup(field=['u_sol'], aiField=['u_big'], st=['u_none','u_none2'], aiSt=['u_none'], active='ai', phase='Battle')
    pg.evaluate("Math.random=()=>0")
    pg.evaluate("performAttack(duel.ai, 0, 0)"); pg.wait_for_timeout(300)
    crit('Activar Trampa narrativa')
    pg.wait_for_selector('.critical-decision', timeout=3000)
    check('Batalla en espera durante la Cadena', pg.evaluate("duel.player.lp")==8000 and pg.evaluate("!!duel.player.monsterZones[0]"))
    crit('Pasar'); pg.wait_for_timeout(800)
    check('Después de la Cadena la batalla continúa (Soldado destruido, -1500)', pg.evaluate("[duel.player.lp, !!duel.player.monsterZones[0]]")==[6500, False], pg.evaluate("[duel.player.lp, duel.log.slice(0,6)]"))
    check('Trampa narrativa no hizo nada y fue al Cementerio', 'u_none' in pg.evaluate("duel.player.gy"))

    # 3. Mágica narrativa no hace nada
    setup(hand=['u_narr'], field=['u_sol'])
    pg.evaluate("Math.random=()=>0.99")
    before = pg.evaluate("JSON.stringify([duel.player.lp,duel.ai.lp,duel.player.hand.length,duel.ai.monsterZones,duel.player.monsterZones.map(z=>z&&z.atkMod)])")
    pg.evaluate("tryActivateFromHandSpell(0)"); pg.wait_for_timeout(300)
    after = pg.evaluate("JSON.stringify([duel.player.lp,duel.ai.lp,duel.player.hand.length+1,duel.ai.monsterZones,duel.player.monsterZones.map(z=>z&&z.atkMod)])")
    check('Mágica «Ninguno / narrativo» no cambia nada', before==after, [before, after])

    # 4. Monstruo Normal con efecto guardado por error: no roba
    setup(hand=['u_norm'])
    pg.evaluate("tryNormalSummon(0,'attack',true)"); pg.wait_for_timeout(200)
    check('Monstruo Normal no activa efectos', pg.evaluate("duel.player.hand.length")==0, pg.evaluate("duel.log.slice(0,3)"))

    # 5. Efecto de Cementerio al ser destruido en batalla: ventana propia (no confirm)
    dl.clear()
    setup(field=['u_sang'], aiField=['u_big'], active='ai', phase='Battle')
    pg.evaluate("performAttack(duel.ai, 0, 0)")
    pg.wait_for_selector('.critical-decision:has-text("Sangan")', timeout=3000)
    crit('Activar el efecto'); pg.wait_for_timeout(300)
    check('Sangan: ventana del juego y robo de 1 carta', pg.evaluate("duel.player.hand.length")==1 and not dl, [dl, pg.evaluate("duel.log.slice(0,5)")])

    # 6. Efecto de Cementerio en medio de una Cadena: se ofrece al terminarla
    setup(field=['u_sang'], aiField=['u_big'], st=['u_none'], hand=[], active='player', phase='Main1')
    pg.evaluate("Math.random=()=>0.99")
    pg.evaluate("(()=>{ duel.ai.hand=[]; duel.player.monsterZones[0]=null; sendToGY(duel.player,'u_sang'); })()")
    pg.wait_for_selector('.critical-decision:has-text("Sangan")', timeout=3000)
    crit('Activar el efecto'); pg.wait_for_timeout(200)
    check('Sangan enviado por efecto: se ofrece y funciona', pg.evaluate("duel.player.hand.length")==1)

    # 7. Botón de efectos manuales del Cementerio
    setup(gy=['u_gym'])
    pg.wait_for_timeout(100)
    vis = pg.is_visible('#gyEffectsBtn')
    check('Aparece el botón «Efectos del Cementerio»', vis and '(1)' in pg.inner_text('#gyEffectsBtn'))
    pg.click('#gyEffectsBtn'); pg.wait_for_timeout(150)
    pg.locator('.choice-btn', has_text='Fénix manual').first.click(); pg.wait_for_timeout(400)
    check('El efecto manual se activa (Invocación desde el Cementerio)', pg.evaluate("duel.player.monsterZones.filter(Boolean).length")==1, pg.evaluate("duel.log.slice(0,4)"))
    check('…y el botón se oculta (una vez por turno)', not pg.is_visible('#gyEffectsBtn'))

    # 8. Creador: tras guardar, el efecto vuelve a Ninguno
    pg.click('button[data-tab="tabColeccion"]'); pg.wait_for_timeout(100)
    pg.select_option('#c_kind','spell'); pg.dispatch_event('#c_kind','change'); pg.fill('#c_name','Con efecto'); pg.select_option('#s_func','draw')
    pg.click('#saveCardBtn'); pg.wait_for_timeout(200)
    check('Creador: tras guardar, «Efecto funcional» vuelve a Ninguno', pg.input_value('#s_func')=='none')
    pg.select_option('#c_kind','monster'); pg.dispatch_event('#c_kind','change'); pg.select_option('#m_category','Normal')
    check('Creador: un Monstruo Normal oculta el efecto funcional', not pg.is_visible('#m_trigger') and pg.is_visible('#m_normal_hint'))
    pg.select_option('#m_category','Efecto')
    check('Creador: un Monstruo de Efecto lo muestra', pg.is_visible('#m_trigger'))
    print('errs', errs)
    print(f"{sum(res)}/{len(res)} OK"); b.close()
