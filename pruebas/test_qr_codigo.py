# El código de conexión (QR) sale mucho más corto y se decodifica igual; también acepta el formato anterior.
from playwright.sync_api import sync_playwright
F='file:///home/claude/duelo-de-cartas/docs/index.html'
SDP="v=0\r\no=- 4611731400430051336 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\na=extmap-allow-mixed\r\na=msid-semantic: WMS\r\nm=application 9 UDP/DTLS/SCTP webrtc-datachannel\r\nc=IN IP4 0.0.0.0\r\n"+\
 "".join(f"a=candidate:{1000+i} 1 udp 2122260223 192.168.1.{10+i} 5{4000+i} typ host generation 0 network-id 1\r\n" for i in range(3))+\
 "".join(f"a=candidate:{2000+i} 1 udp 2122262783 2806:103e:16:abcd::{i} 5{5000+i} typ host generation 0 network-id 2\r\n" for i in range(3))+\
 "a=candidate:3000 1 udp 1686052607 189.203.10.20 54001 typ srflx raddr 192.168.1.10 rport 54001 generation 0 network-id 1\r\n"+\
 "".join(f"a=candidate:{4000+i} 1 udp 41885439 34.10.20.{30+i} 6{1000+i} typ relay raddr 189.203.10.20 rport 54001 generation 0 network-id 1\r\n" for i in range(4))+\
 "a=ice-ufrag:Ab3d\r\na=ice-pwd:qwertyuiopasdfghjklzxcvb\r\na=ice-options:trickle\r\na=fingerprint:sha-256 6A:2B:3C:4D:5E:6F:70:81:92:A3:B4:C5:D6:E7:F8:09:1A:2B:3C:4D:5E:6F:70:81:92:A3:B4:C5:D6:E7:F8:09\r\na=setup:actpass\r\na=mid:0\r\na=sctp-port:5000\r\na=max-message-size:262144\r\n"
res=[]
def check(n,c,i=''):
    res.append(c); print(('✅' if c else '❌'), n, '' if c else i)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(800)
    r=pg.evaluate("""async (sdp)=>{ const d={type:'offer', sdp};
      const old = btoa(encodeURIComponent(JSON.stringify(d)));
      const neu = await packSignal(d);
      const back = await unpackSignal(neu); const backOld = await unpackSignal(old);
      const pc = new RTCPeerConnection(); let ok=true; try{ await pc.setRemoteDescription(back); }catch(e){ ok=String(e); } pc.close();
      return {old:old.length, neu:neu.length, type:back.type, has:back.sdp.includes('a=fingerprint') && back.sdp.includes('typ srflx') && back.sdp.includes('typ relay'), v6:back.sdp.includes('2806:'), oldOk: backOld.sdp===sdp, ok}; }""", SDP)
    print(r)
    check('El código nuevo es al menos 3 veces más corto', r['neu']*3 <= r['old'], r)
    check('Se decodifica igual (oferta, huella, candidatos útiles)', r['type']=='offer' and r['has'] and not r['v6'], r)
    check('El navegador acepta la descripción decodificada', r['ok'] is True, r)
    check('Sigue leyendo códigos del formato anterior', r['oldOk'])
    check('Sin errores', not errs, errs)
    print(f'{sum(res)}/{len(res)}'); b.close()
