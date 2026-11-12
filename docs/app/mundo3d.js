// ═══════════ Centro de control 3D de la oficina ═══════════
// Three.js r128. Todo sale de datos reales: oficina.json (equipo, canal, acuerdos, jornadas),
// oficina_datos.json (números de cada puesto, mejora) y estado.json (vídeos en producción).
let M3=null;
const M3_VISTA={th:0.42,ph:1.02,r:40,tx:0,tz:0};
const M3_ORDEN=["estratega","director","seo",null,"fotografia","motion","sonido","editor",null,"social","paid",null];
const M3_DEP={estratega:"PREPRODUCCIÓN",director:"PREPRODUCCIÓN",seo:"PREPRODUCCIÓN",fotografia:"PRODUCCIÓN",motion:"PRODUCCIÓN",sonido:"PRODUCCIÓN",editor:"PRODUCCIÓN",social:"DISTRIBUCIÓN",paid:"DISTRIBUCIÓN"};
const M3_DEPS=[["PREPRODUCCIÓN",0,2,"#9b87f5"],["PRODUCCIÓN",4,7,"#5aa2ff"],["DISTRIBUCIÓN",9,10,"#2fb5a8"]];
const M3_FASES=[["Guion",["propuesto"],"#ffd23f"],["Voz",["aprobado"],"#34c77b"],["Escena 3D",["voz","rehacer"],"#5aa2ff"],["Render",["escena","renderizando"],"#d55181"],["Tu revisión",["revision"],"#f5a524"]];
const M3_R=12.5;

function mundoStop(){if(!M3)return;cancelAnimationFrame(M3.raf);M3.ro&&M3.ro.disconnect();M3.io&&M3.io.disconnect();removeEventListener("keydown",M3.tecla);try{M3.r.dispose()}catch(e){}M3=null}
if(typeof heroStop==="function"){const _hs=heroStop;heroStop=function(){_hs();mundoStop()}}

function mundoHTML(){
  return `<div class="ofi3d fade" id="ofi3d">
   <canvas aria-label="Centro de control de la oficina en 3D: arrastra para girar, toca una estación para ver su trabajo"></canvas>
   <div class="m3-hud"></div>
   <div class="m3-barra">
    <button class="btn peq" data-m3="replay">${ic("play","s")}Reproducir jornada</button>
    <button class="btn sec peq" data-m3="general">${ic("home","s")}Vista general</button>
    <button class="btn sec peq on" data-m3="lineas">${ic("chat","s")}Comunicaciones</button>
   </div>
   <div class="m3-ayuda">${ic("info","s")}<span>Arrastra para girar · rueda o pellizco para acercar · toca una estación, un vídeo o un mensaje</span></div>
   <div class="m3-feed" hidden></div>
   <div class="m3-info" hidden></div>
   <div class="m3-tip" hidden></div>
   <div class="m3-carga">Iniciando el centro de control…</div>
  </div>`;
}

function texCanvas(w,h,pinta){const c=document.createElement("canvas");c.width=w;c.height=h;const g=c.getContext("2d");pinta(g,w,h);const t=new THREE.CanvasTexture(c);t.anisotropy=8;t.encoding=THREE.sRGBEncoding;return t}
function rr(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath()}
function recorta(g,t,w){t=String(t??"");if(g.measureText(t).width<=w)return t;while(t.length&&g.measureText(t+"…").width>w)t=t.slice(0,-1);return t+"…"}
function lineas(g,t,x,y,w,lh,max){const p=String(t||"").split(/\s+/);let l="",n=0;for(let i=0;i<p.length;i++){const z=l?l+" "+p[i]:p[i];if(g.measureText(z).width>w&&l){if(n===max-1){g.fillText(recorta(g,l+" "+p.slice(i).join(" "),w),x,y+n*lh);return n+1}g.fillText(l,x,y+n*lh);n++;l=p[i]}else l=z}if(l)g.fillText(l,x,y+n*lh);return n+1}
const colNivel=n=>n==="ok"?"#34c77b":n==="warn"?"#f5a524":n==="err"?"#f05252":"#9496a3";
let BRILLO=null;function brillo(){return BRILLO||(BRILLO=texCanvas(128,128,(g)=>{const r=g.createRadialGradient(64,64,0,64,64,64);r.addColorStop(0,"rgba(255,255,255,1)");r.addColorStop(.25,"rgba(255,255,255,.55)");r.addColorStop(1,"rgba(255,255,255,0)");g.fillStyle=r;g.fillRect(0,0,128,128)}))}

async function mundo3d(cont){
  mundoStop();if(!cont)return;
  const canvas=cont.querySelector("canvas");
  let r;try{if(!window.THREE)throw 0;r=new THREE.WebGLRenderer({canvas,antialias:true})}catch(e){cont.innerHTML=`<div class="vacio">${ic("alert")}<b>Tu navegador no puede mostrar el centro de control en 3D</b>Abajo tienes las fichas del equipo.</div>`;return}
  try{await document.fonts?.ready}catch(e){}
  const rm=matchMedia("(prefers-reduced-motion: reduce)").matches;
  r.setPixelRatio(Math.min(devicePixelRatio||1,2));r.outputEncoding=THREE.sRGBEncoding;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.05;
  const sc=new THREE.Scene();sc.background=new THREE.Color("#07090d");sc.fog=new THREE.FogExp2("#07090d",0.012);
  const cam=new THREE.PerspectiveCamera(32,1,0.5,300);
  sc.add(new THREE.HemisphereLight("#9fb3d9","#0a0c10",0.55));
  const key=new THREE.DirectionalLight("#ffffff",0.7);key.position.set(10,30,18);sc.add(key);
  const nucleoLuz=new THREE.PointLight("#ffd23f",0.6,30);nucleoLuz.position.set(0,4,0);sc.add(nucleoLuz);
  const std=(c,o={})=>new THREE.MeshStandardMaterial({color:c,metalness:.35,roughness:.55,...o});
  const basic=(c,o={})=>new THREE.MeshBasicMaterial({color:c,...o});
  const add=(geo,m,x,y,z,padre=sc)=>{const o=new THREE.Mesh(geo,m);o.position.set(x,y,z);padre.add(o);return o};
  const clicables=[],anim=[];
  const clic=(o,info)=>{o.traverse(c=>{if(c.isMesh||c.isSprite){c.userData.info=info;clicables.push(c)}});return o};
  const equipo=OFI.equipo,P_=OFD.puestos||{},rep=OFD.reputacion||{};
  const ultJ=OFI.jornadas[OFI.jornadas.length-1];
  const diaJ=[...new Set(OFI.canal.map(m=>m.jornada))].sort().pop();
  const hoyMsgs=OFI.canal.filter(m=>m.jornada===diaJ);
  const acuerdos=OFI.acuerdos.filter(a=>a.estado==="vigente");

  // ── Suelo: plataforma circular con retícula fina ──
  const tSuelo=texCanvas(2048,2048,(g,w,h)=>{g.fillStyle="#0b0e14";g.fillRect(0,0,w,h);const c=w/2;
    g.strokeStyle="rgba(140,160,200,.07)";g.lineWidth=2;for(let k=1;k<=13;k++){g.beginPath();g.arc(c,c,k*76,0,7);g.stroke()}
    for(let k=0;k<72;k++){const a=k/72*Math.PI*2;g.beginPath();g.moveTo(c+Math.cos(a)*150,c+Math.sin(a)*150);g.lineTo(c+Math.cos(a)*990,c+Math.sin(a)*990);g.stroke()}
    g.strokeStyle="rgba(255,210,63,.18)";g.lineWidth=4;g.beginPath();g.arc(c,c,990,0,7);g.stroke()});
  const suelo=add(new THREE.CircleGeometry(26,96),new THREE.MeshStandardMaterial({map:tSuelo,metalness:.2,roughness:.9}),0,0,0);suelo.rotation.x=-Math.PI/2;
  add(new THREE.CylinderGeometry(26,26.4,0.6,96,1,true),std("#0e121a"),0,-0.3,0);
  // arcos de departamento
  const ang=i=>-Math.PI/2-(i/M3_ORDEN.length)*Math.PI*2+Math.PI*0.08;
  for(const [nom,a,b,c] of M3_DEPS){const t0=ang(b)-0.16,t1=ang(a)+0.16;
    const arco=add(new THREE.RingGeometry(16.6,16.75,64,1,t0,t1-t0),basic(c,{transparent:true,opacity:.75,side:THREE.DoubleSide}),0,0.02,0);arco.rotation.x=-Math.PI/2;
    const tm=(t0+t1)/2,tl=texCanvas(1024,128,(g,w,h)=>{g.fillStyle=c;g.font="600 64px Inter";g.textAlign="center";g.textBaseline="middle";g.fillText(nom.split("").join(" "),w/2,h/2)});
    const et=add(new THREE.PlaneGeometry(7,0.88),basic("#fff",{map:tl,transparent:true,opacity:.85}),Math.cos(tm)*17.7,0.03,-Math.sin(tm)*17.7);et.rotation.x=-Math.PI/2;et.rotation.z=tm-Math.PI/2}

  // ── Estaciones ──
  const est={};
  M3_ORDEN.forEach((id,i)=>{if(!id)return;const e=equipo.find(x=>x.id===id);if(!e)return;
    const a=ang(i),x=Math.cos(a)*M3_R,z=-Math.sin(a)*M3_R,g=new THREE.Group();g.position.set(x,0,z);g.rotation.y=Math.atan2(-x,-z);sc.add(g);
    const d=P_[id]||{},k=d.kpi,niv=kpiNivel(k),col=new THREE.Color(e.color);
    add(new THREE.CylinderGeometry(2.1,2.3,0.4,6),std("#141a24"),0,0.2,0,g);
    const borde=add(new THREE.RingGeometry(2.12,2.22,6),basic(e.color,{transparent:true,opacity:.9,side:THREE.DoubleSide}),0,0.41,0,g);borde.rotation.x=-Math.PI/2;borde.rotation.z=Math.PI/6;
    add(new THREE.BoxGeometry(0.5,1.0,0.5),std("#1b2230"),0,0.9,0.15,g);
    const consola=add(new THREE.BoxGeometry(2.6,0.1,1.1),std("#1e2635",{metalness:.5}),0,1.45,0.2,g);consola.rotation.x=-0.28;
    const tira=add(new THREE.BoxGeometry(2.6,0.03,0.05),basic(e.color),0,1.5,0.76,g);tira.rotation.x=-0.28;
    const led=add(new THREE.SphereGeometry(0.11,16,12),basic(colNivel(niv)),1.05,1.62,0.45,g);
    // haz de actividad: más intenso cuanto más ha hablado hoy
    const act=hoyMsgs.filter(m=>m.de===id||m.para===id||(m.respuestas||[]).some(r=>r.de===id)).length;
    const haz=add(new THREE.CylinderGeometry(0.05,0.05,7,8,1,true),basic(e.color,{transparent:true,opacity:act?.35:.08,blending:THREE.AdditiveBlending,depthWrite:false}),0,4.4,-0.6,g);
    const halo=new THREE.Sprite(new THREE.SpriteMaterial({map:brillo(),color:col,transparent:true,opacity:act?.5:.15,blending:THREE.AdditiveBlending,depthWrite:false}));halo.scale.set(2.2,2.2,1);halo.position.set(0,0.6,0);g.add(halo);
    // panel de datos (mira siempre a la cámara)
    const panel=new THREE.Group();panel.position.set(x,4.7,z);panel.scale.setScalar(1.22);sc.add(panel);
    const bandeja=hoyMsgs.filter(m=>m.para===id||m.para==="todos").length,susAc=acuerdos.filter(a=>a.rol===id).length,pend=d.pendiente||0;
    const tP=texCanvas(1024,680,(gg,w,h)=>{gg.fillStyle="rgba(12,16,24,.92)";rr(gg,0,0,w,h,28);gg.fill();gg.strokeStyle="rgba(255,255,255,.10)";gg.lineWidth=3;rr(gg,1.5,1.5,w-3,h-3,28);gg.stroke();
      gg.fillStyle=e.color;gg.fillRect(40,46,10,96);
      gg.fillStyle="#7d8294";gg.font="600 26px Inter";gg.fillText(M3_DEP[id].split("").join(" "),70,64);
      gg.fillStyle="#f4f3ef";gg.font="700 54px 'Space Grotesk'";gg.fillText(recorta(gg,e.nombre,880),68,120);
      gg.fillStyle="#9ea3b5";gg.font="500 26px Inter";gg.fillText(recorta(gg,e.puesto,900),70,162);
      gg.fillStyle="rgba(255,255,255,.07)";gg.fillRect(40,192,w-80,2);
      gg.fillStyle="#7d8294";gg.font="600 24px Inter";gg.fillText(recorta(gg,(k?.nombre||"Indicador").toUpperCase(),620),40,240);
      gg.fillStyle=colNivel(niv);gg.font="700 96px 'Space Grotesk'";gg.fillText(fmtKpi(k),36,334);
      if(k?.meta!=null&&k.valor!=null){gg.fillStyle="#232a38";gg.fillRect(40,360,w-80,8);gg.fillStyle=colNivel(niv);gg.fillRect(40,360,(w-80)*Math.min(1,k.valor/k.meta),8);gg.fillStyle="#7d8294";gg.font="500 22px Inter";gg.textAlign="right";gg.fillText("objetivo "+fmtKpi({...k,valor:k.meta}),w-40,334);gg.textAlign="left"}
      gg.fillStyle="#c9ccd6";gg.font="500 27px Inter";lineas(gg,d.ahora||"Sin datos todavía",40,418,w-80,36,2);
      if(d.foco){gg.fillStyle="#ffd23f";gg.font="600 22px Inter";lineas(gg,"FOCO · "+d.foco,40,500,w-80,30,2)}
      const cols=[["BANDEJA",bandeja],["ACUERDOS",susAc],["PENDIENTE",pend],["VOTO",`×${String(rep[id]?.peso??1).replace(".",",")}`]];
      cols.forEach(([t,v],j)=>{const cx=40+j*(w-80)/4;gg.fillStyle="#f4f3ef";gg.font="700 38px 'Space Grotesk'";gg.fillText(String(v),cx,640);gg.fillStyle="#6b7083";gg.font="600 18px Inter";gg.fillText(t,cx,596)})});
    const pm=add(new THREE.PlaneGeometry(4.6,3.05),basic("#fff",{map:tP,transparent:true,side:THREE.DoubleSide}),0,0,0,panel);
    const marco=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(4.64,3.09)),new THREE.LineBasicMaterial({color:e.color,transparent:true,opacity:.35}));panel.add(marco);
    clic(g,{tipo:"puesto",id});clic(panel,{tipo:"puesto",id});
    est[id]={g,panel,pos:new THREE.Vector3(x,1.7,z),led,haz,halo,borde,act};
    const f=i*0.7;anim.push(t=>{if(rm)return;haz.material.opacity=(act?.25:.06)+(act?.15:.03)*Math.sin(t*2+f);led.scale.setScalar(1+0.15*Math.sin(t*3+f))});
  });

  // ── Núcleo: producción ──
  const nucleo=new THREE.Group();sc.add(nucleo);
  add(new THREE.CylinderGeometry(4.8,5.1,0.5,64),std("#121722"),0,0.25,0,nucleo);
  const fases=M3_FASES.map(([n,es,c])=>({n,c,v:PROD.filter(v=>es.includes(v.estado))}));
  const total=fases.reduce((s,f)=>s+f.v.length,0);
  const chips=[];
  fases.forEach((f,i)=>{const t0=Math.PI/2-i*Math.PI*2/5-0.04,len=Math.PI*2/5-0.08;
    const seg=add(new THREE.RingGeometry(3.6,4.5,40,1,t0-len,len),basic(f.c,{transparent:true,opacity:.22,side:THREE.DoubleSide}),0,0.52,0,nucleo);seg.rotation.x=-Math.PI/2;
    const bord=add(new THREE.RingGeometry(4.45,4.55,40,1,t0-len,len),basic(f.c,{side:THREE.DoubleSide}),0,0.53,0,nucleo);bord.rotation.x=-Math.PI/2;
    const tm=t0-len/2,tl=texCanvas(512,160,(g,w,h)=>{g.fillStyle=f.c;g.font="700 54px 'Space Grotesk'";g.textAlign="center";g.fillText(f.n.toUpperCase(),w/2,66);g.fillStyle="#c9ccd6";g.font="600 40px Inter";g.fillText(`${f.v.length} vídeo${f.v.length===1?"":"s"}`,w/2,128)});
    const et=add(new THREE.PlaneGeometry(2.4,0.75),basic("#fff",{map:tl,transparent:true}),Math.cos(tm)*5.9,0.56,-Math.sin(tm)*5.9,nucleo);et.rotation.x=-Math.PI/2;et.rotation.z=tm-Math.PI/2;
    f.v.slice(0,10).forEach((v,j)=>{const n=Math.min(10,f.v.length),aa=t0-len*(j+0.5)/n,rad=4.05;
      const ch=add(new THREE.BoxGeometry(0.42,0.12,0.6),std(f.c,{emissive:new THREE.Color(f.c),emissiveIntensity:.35}),Math.cos(aa)*rad,0.75,-Math.sin(aa)*rad,nucleo);ch.rotation.y=aa;
      clic(ch,{tipo:"video",id:v.id});chips.push(ch);const ff=j+i*3;anim.push(t=>{if(!rm)ch.position.y=0.75+0.06*Math.sin(t*2+ff)})});
  });
  const anillo=add(new THREE.TorusGeometry(2.4,0.03,8,96),basic("#ffd23f",{transparent:true,opacity:.6}),0,2.2,0,nucleo);anillo.rotation.x=Math.PI/2;
  const anillo2=add(new THREE.TorusGeometry(1.7,0.02,8,96),basic("#5aa2ff",{transparent:true,opacity:.5}),0,3.0,0,nucleo);anillo2.rotation.x=Math.PI/2;
  const tN=texCanvas(1024,420,(g,w,h)=>{g.textAlign="center";g.fillStyle="#7d8294";g.font="600 34px Inter";g.fillText("P R O D U C C I Ó N",w/2,60);g.fillStyle="#f4f3ef";g.font="700 150px 'Space Grotesk'";g.fillText(String(total),w/2,210);g.fillStyle="#c9ccd6";g.font="500 36px Inter";g.fillText("vídeos en marcha",w/2,262);
    g.fillStyle="#ffd23f";g.font="600 32px Inter";g.fillText(ultJ?.estado==="hecha"?`Jornada ${fmtDiaC(ultJ.fecha)}: ${ultJ.mensajes} mensajes · ${ultJ.acuerdos} acuerdos`:"Jornada diaria: 07:17",w/2,340)});
  const cartelN=new THREE.Group();cartelN.position.set(0,4.4,0);sc.add(cartelN);add(new THREE.PlaneGeometry(5.2,2.13),basic("#fff",{map:tN,transparent:true,side:THREE.DoubleSide}),0,0,0,cartelN);
  clic(nucleo,{tipo:"nucleo"});clic(cartelN,{tipo:"nucleo"});
  anim.push(t=>{if(rm)return;anillo.rotation.z=t*0.25;anillo2.rotation.z=-t*0.4;anillo.position.y=2.2+0.1*Math.sin(t)});

  // ── Comunicaciones reales: un arco por mensaje y un impulso que viaja ──
  const enlaces=[];
  const posDe=id=>id==="todos"?new THREE.Vector3(0,2.6,0):est[id]?.pos.clone();
  function curva(a,b){const m=a.clone().add(b).multiplyScalar(0.5);m.multiplyScalar(0.45);m.y=3.5+a.distanceTo(b)*0.18;return new THREE.QuadraticBezierCurve3(a,m,b)}
  hoyMsgs.forEach((m,i)=>{const a=posDe(m.de),b=posDe(m.para);if(!a||!b)return;const cv=curva(a,b),col=new THREE.Color(rolDe(m.de).color);
    const lin=new THREE.Line(new THREE.BufferGeometry().setFromPoints(cv.getPoints(48)),new THREE.LineBasicMaterial({color:col,transparent:true,opacity:.22}));sc.add(lin);
    const imp=new THREE.Sprite(new THREE.SpriteMaterial({map:brillo(),color:col,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}));imp.scale.set(0.7,0.7,1);sc.add(imp);
    imp.userData.info={tipo:"mensaje",id:m.id};clicables.push(imp);
    enlaces.push({m,cv,lin,imp,fase:i/Math.max(1,hoyMsgs.length)})});
  let verLineas=true,SEL=null;
  anim.push(t=>{if(REP.activo)return;for(const L of enlaces){const foco=!SEL||SEL===L.m.de||SEL===L.m.para;L.lin.visible=L.imp.visible=verLineas;L.lin.material.opacity=foco?(SEL?.7:.22):.04;L.imp.material.opacity=foco?.95:.1;
    L.imp.position.copy(L.cv.getPoint(rm?0.5:(t*0.12+L.fase)%1))}});

  // ── HUD ──
  const hud=cont.querySelector(".m3-hud"),dirK=P_.director?.kpi;
  hud.innerHTML=`<div><small>Jornada</small><b>${ultJ?.estado==="hecha"?fmtDiaC(ultJ.fecha):ultJ?.estado==="sin_clave"?"Sin clave":"—"}</b></div><div><small>Mensajes</small><b>${hoyMsgs.length}</b></div><div><small>Acuerdos</small><b>${acuerdos.length}</b></div><div><small>Frente a lo normal</small><b>${fmtKpi(dirK)}</b></div>`;

  // ── Cámara orbital ──
  const V=Object.assign({},M3_VISTA),obj=Object.assign({},V);const fijar=o=>Object.assign(obj,o);
  let arr=null,movido=0,pinch=null;const ptrs=new Map();
  canvas.addEventListener("pointerdown",e=>{canvas.setPointerCapture(e.pointerId);ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});arr={x:e.clientX,y:e.clientY};movido=0;if(ptrs.size===2){const [p,q]=[...ptrs.values()];pinch={d:Math.hypot(p.x-q.x,p.y-q.y),r:obj.r}}});
  canvas.addEventListener("pointermove",e=>{if(ptrs.has(e.pointerId))ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(pinch&&ptrs.size===2){const [p,q]=[...ptrs.values()];obj.r=Math.min(60,Math.max(12,pinch.r*pinch.d/Math.max(20,Math.hypot(p.x-q.x,p.y-q.y))));movido=99;return}
    if(arr){const dx=e.clientX-arr.x,dy=e.clientY-arr.y;movido+=Math.abs(dx)+Math.abs(dy);obj.th-=dx*0.006;obj.ph=Math.min(1.35,Math.max(0.35,obj.ph-dy*0.005));arr={x:e.clientX,y:e.clientY};if(movido>6)ocultarTip()}else hover(e)});
  const fin=e=>{ptrs.delete(e.pointerId);if(ptrs.size<2)pinch=null;if(arr&&movido<6&&e.type==="pointerup")tocar(e);if(!ptrs.size)arr=null};
  canvas.addEventListener("pointerup",fin);canvas.addEventListener("pointercancel",fin);canvas.addEventListener("pointerleave",()=>{if(!ptrs.size)ocultarTip()});
  canvas.addEventListener("wheel",e=>{e.preventDefault();obj.r=Math.min(60,Math.max(12,obj.r*(1+Math.sign(e.deltaY)*0.09)))},{passive:false});
  const ray=new THREE.Raycaster(),ndc=new THREE.Vector2();
  const pick=e=>{const b=canvas.getBoundingClientRect();ndc.set((e.clientX-b.left)/b.width*2-1,-((e.clientY-b.top)/b.height)*2+1);ray.setFromCamera(ndc,cam);const h=ray.intersectObjects(clicables.filter(o=>o.visible!==false),false)[0];return h?.object.userData.info||null};
  const tip=cont.querySelector(".m3-tip"),info=cont.querySelector(".m3-info"),feed=cont.querySelector(".m3-feed");
  function ocultarTip(){tip.hidden=true;canvas.style.cursor="grab"}
  function hover(e){const i=pick(e);if(!i){ocultarTip();return}canvas.style.cursor="pointer";const b=cont.getBoundingClientRect();tip.hidden=false;tip.innerHTML=resumen(i);tip.style.left=Math.min(b.width-250,e.clientX-b.left+14)+"px";tip.style.top=(e.clientY-b.top+14)+"px"}
  function tocar(e){const i=pick(e);if(i)seleccionar(i);else if(!REP.activo){cerrarInfo()}}
  function resumen(i){
    if(i.tipo==="puesto"){const e=rolDe(i.id);return `<b>${esc(e.nombre)}</b><small>${esc(e.puesto)}</small>`}
    if(i.tipo==="video"){const v=PROD.find(x=>x.id===i.id);return `<b>${esc(v?.titulo||i.id)}</b><small>${esc(FASES[v?.estado]||"")}</small>`}
    if(i.tipo==="mensaje"){const m=OFI.canal.find(x=>x.id===i.id);return `<b>${esc(rolDe(m?.de).nombre)} → ${m?.para==="todos"?"todos":esc(rolDe(m?.para).nombre)}</b><small>${esc(m?.asunto||"")}</small>`}
    return `<b>Producción</b><small>${total} vídeos en marcha</small>`}
  function cerrarInfo(){info.hidden=true;SEL=null;fijar({...M3_VISTA})}
  function htmlMensaje(m,breve){const t=TIPO_MSG[m.tipo]||[m.tipo,""];return `<div class="m3-msg"><div class="m3-msg-cab">${avatarRol(m.de,24)}<b>${esc(rolDe(m.de).nombre)}</b>${ic("right","s")}${m.para==="todos"?"<b>Todos</b>":`<b>${esc(rolDe(m.para).nombre)}</b>`}<span class="pill ${t[1]}">${t[0]}</span></div><b class="m3-asunto">${esc(m.asunto)}</b><p>${esc(breve?m.texto.slice(0,180):m.texto)}</p>
    ${(m.respuestas||[]).map(r=>{const d=DECISION[r.decision]||[r.decision,""];return `<div class="m3-resp">${avatarRol(r.de,20)}<span class="pill ${d[1]}">${d[0]}</span><span>${esc(breve?r.texto.slice(0,140):r.texto)}${r.compromiso?`<em>Se compromete: ${esc(r.compromiso)}</em>`:""}</span></div>`}).join("")}</div>`}
  function seleccionar(i){
    ocultarTip();
    if(i.tipo==="puesto"){
      SEL=i.id;const s=est[i.id],e=rolDe(i.id),d=P_[i.id]||{},k=d.kpi,rp=rep[i.id]||{};
      fijar({tx:s.pos.x*0.7,tz:s.pos.z*0.7,r:25,ph:1.0,th:Math.atan2(s.pos.x,s.pos.z)+0.35});
      const suyos=hoyMsgs.filter(m=>m.de===i.id||m.para===i.id||m.para==="todos"||(m.respuestas||[]).some(r=>r.de===i.id)),acs=acuerdos.filter(a=>a.rol===i.id);
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button>
        <div class="ofi-cab">${avatarRol(i.id,40)}<div><b>${esc(e.nombre)}</b><small>${esc(e.puesto)}</small></div></div>
        <p class="m3-mision">${esc(e.mision||"")}</p>
        <div class="m3-datos"><div><small>${esc(k?.nombre||"Indicador")}</small><b class="${kpiNivel(k)}">${fmtKpi(k)}</b></div><div><small>Voto</small><b>×${String(rp.peso??1).replace(".",",")}</b></div><div><small>Acuerdos</small><b>${acs.length}</b></div></div>
        <div class="m3-fila">${ic("clock","s")}<span>${esc(d.ahora||"—")}</span></div>
        ${d.foco?`<div class="m3-fila foco">${ic("spark","s")}<span><b>Foco:</b> ${esc(d.foco)}</span></div>`:""}
        ${acs.length?`<div class="m3-sec">Se ha comprometido a</div>${acs.slice(-4).reverse().map(a=>`<div class="m3-fila">${ic("check","s")}<span>${esc(a.texto)} <small class="mut">· lo pidió ${esc(rolDe(a.pedido_por).nombre)}</small></span></div>`).join("")}`:""}
        <div class="m3-sec">Conversaciones de la jornada</div>${suyos.length?suyos.slice(0,6).map(m=>htmlMensaje(m,true)).join(""):`<p class="mut peq">Sin mensajes en la última jornada.</p>`}
        <div class="m3-acc"><button class="btn peq" data-a="enc">${ic("send","s")}Encargarle algo</button><button class="btn sec peq" data-a="ficha">Ficha completa</button><a class="btn sec peq" href="#/ofi/canal">Canal</a></div>`;
      info.querySelector('[data-a="enc"]').onclick=()=>nuevoEncargo(i.id);info.querySelector('[data-a="ficha"]').onclick=()=>verPuesto(i.id);
    }else if(i.tipo==="video"){
      const v=PROD.find(x=>x.id===i.id)||{};SEL=null;fijar({tx:0,tz:0,r:20,ph:0.75});
      const recs=(OFD.mejora?.recomendaciones||{})[i.id]||[],revs=v.revisiones||[];
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button><b class="m3-tit">${esc(v.titulo||i.id)}</b><small class="mut">${esc(FASES[v.estado]||"")} · formato ${esc(v.formato||"?")}</small>
        ${revs.length?`<div class="m3-sec">Revisiones de los agentes</div>${revs.slice(-5).map(r=>`<div class="m3-fila">${avatarRol(r.rol,20)}<span><span class="pill ${r.veredicto==="ok"?"ok":"warn"}">${r.veredicto==="ok"?"De acuerdo":"Cambios"}</span> ${esc(r.nota||"")}</span></div>`).join("")}`:""}
        ${recs.length?`<div class="m3-sec">Auditoría técnica</div>${recs.slice(0,5).map(x=>`<div class="m3-fila ${x.tipo}">${avatarRol(x.rol,20)}<span><b>${x.tipo==="mejorar"?"Mejorar":"Potenciar"}:</b> ${esc(x.texto)}</span></div>`).join("")}`:""}
        <div class="m3-acc"><a class="btn peq" href="#/prod/${v.estado==="propuesto"?"guiones":v.estado==="revision"?"borradores":"marcha"}">Abrir en Producción</a></div>`;
    }else if(i.tipo==="mensaje"){
      const m=OFI.canal.find(x=>x.id===i.id);if(!m)return;SEL=m.de;
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button><div class="m3-sec" style="margin-top:0">Mensaje · ${fmtDiaC(m.fecha)}</div>${htmlMensaje(m,false)}<div class="m3-acc"><a class="btn sec peq" href="#/ofi/canal">Ver todo el canal</a></div>`;
    }else{
      SEL=null;fijar({tx:0,tz:0,r:22,ph:0.7});
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button><b class="m3-tit">Producción</b><p class="m3-mision">Tus vídeos reales, en la fase en la que está cada uno.</p>${fases.map(f=>`<div class="m3-fila"><span class="m3-dot" style="background:${f.c}"></span><span><b>${f.n}:</b> ${f.v.length}${f.v.length?` · ${f.v.slice(0,3).map(v=>esc(v.titulo.slice(0,34))).join(" · ")}`:""}</span></div>`).join("")}<div class="m3-acc"><a class="btn peq" href="#/prod">Abrir Producción</a></div>`;
    }
    info.hidden=false;pintarIconos(info);info.querySelector(".m3-x").onclick=cerrarInfo;
  }

  // ── Reproducir la jornada mensaje a mensaje ──
  const REP={activo:false,pasos:[],i:0,t0:0,pausa:false};
  for(const m of hoyMsgs){REP.pasos.push({m,de:m.de,a:m.para,tipo:"msg"});for(const r of m.respuestas||[])REP.pasos.push({m,r,de:r.de,a:m.de,tipo:"resp"})}
  const repImp=new THREE.Sprite(new THREE.SpriteMaterial({map:brillo(),color:"#ffffff",transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}));repImp.scale.set(1.3,1.3,1);repImp.visible=false;sc.add(repImp);
  const repLin=new THREE.Line(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({color:"#ffffff",transparent:true,opacity:.9}));repLin.visible=false;sc.add(repLin);
  function pintaFeed(){const p=REP.pasos[REP.i];if(!p){pararRep();return}
    const d=p.r?DECISION[p.r.decision]||[p.r.decision,""]:null,t=TIPO_MSG[p.m.tipo]||[p.m.tipo,""];
    feed.innerHTML=`<div class="m3-feed-cab"><small>Jornada del ${fmtDiaC(diaJ)} · ${REP.i+1} de ${REP.pasos.length}</small><div><button class="ib" data-r="ant" aria-label="Anterior">${ic("left","s")}</button><button class="ib" data-r="pausa" aria-label="Pausa">${ic(REP.pausa?"play":"clock","s")}</button><button class="ib" data-r="sig" aria-label="Siguiente">${ic("right","s")}</button><button class="ib" data-r="fin" aria-label="Terminar">${ic("x","s")}</button></div></div>
      <div class="m3-msg-cab">${avatarRol(p.de,24)}<b>${esc(rolDe(p.de).nombre)}</b>${ic("right","s")}${p.a==="todos"?"<b>Todos</b>":`<b>${esc(rolDe(p.a).nombre)}</b>`}${p.r?`<span class="pill ${d[1]}">${d[0]}</span>`:`<span class="pill ${t[1]}">${t[0]}</span>`}</div>
      ${p.r?`<p>${esc(p.r.texto)}</p>${p.r.compromiso?`<div class="ofi-comp">${ic("check","s")}<span><b>Se compromete:</b> ${esc(p.r.compromiso)}</span></div>`:""}`:`<b class="m3-asunto">${esc(p.m.asunto)}</b><p>${esc(p.m.texto)}</p>`}`;
    feed.hidden=false;pintarIconos(feed);
    feed.querySelector('[data-r="ant"]').onclick=()=>{REP.i=Math.max(0,REP.i-1);arrancaPaso()};feed.querySelector('[data-r="sig"]').onclick=()=>{REP.i++;arrancaPaso()};
    feed.querySelector('[data-r="pausa"]').onclick=()=>{REP.pausa=!REP.pausa;pintaFeed()};feed.querySelector('[data-r="fin"]').onclick=pararRep}
  function arrancaPaso(){const p=REP.pasos[REP.i];if(!p)return pararRep();const a=posDe(p.de),b=posDe(p.a);REP.cv=a&&b?curva(a,b):null;
    const col=p.r?colNivel({acepto:"ok",matizo:"warn",rechazo:"err"}[p.r.decision]||""):rolDe(p.de).color;repImp.material.color.set(col);repLin.material.color.set(col);
    if(REP.cv){repLin.geometry.dispose();repLin.geometry=new THREE.BufferGeometry().setFromPoints(REP.cv.getPoints(60))}
    SEL=p.de;const s=est[p.a]||est[p.de];if(s)fijar({tx:s.pos.x*0.25,tz:s.pos.z*0.25,r:30,ph:0.8});REP.t0=performance.now();pintaFeed()}
  function empezarRep(){if(!REP.pasos.length){toast("Aún no hay conversaciones: la primera jornada las creará.","err");return}info.hidden=true;REP.activo=true;REP.i=0;REP.pausa=false;repImp.visible=repLin.visible=true;enlaces.forEach(L=>{L.lin.visible=L.imp.visible=false});arrancaPaso()}
  function pararRep(){REP.activo=false;feed.hidden=true;repImp.visible=repLin.visible=false;SEL=null;fijar({...M3_VISTA});enlaces.forEach(L=>{L.lin.visible=L.imp.visible=verLineas})}
  anim.push(()=>{if(!REP.activo||!REP.cv)return;const el=(performance.now()-REP.t0)/1000;const u=Math.min(1,el/1.6);repImp.position.copy(REP.cv.getPoint(u));
    if(!REP.pausa&&el>5.5){REP.i++;if(REP.i>=REP.pasos.length)pararRep();else arrancaPaso()}});

  cont.querySelectorAll("[data-m3]").forEach(b=>b.onclick=()=>{const a=b.dataset.m3;
    if(a==="replay")REP.activo?pararRep():empezarRep();else if(a==="general"){if(REP.activo)pararRep();info.hidden=true;SEL=null;fijar({...M3_VISTA})}
    else if(a==="lineas"){verLineas=!verLineas;b.classList.toggle("on",verLineas)}});
  if(!REP.pasos.length)cont.querySelector('[data-m3="replay"]').title="Aún no hay conversaciones";
  const tecla=e=>{if(!cont.isConnected)return;if(e.key==="Escape"){if(REP.activo)pararRep();else if(!info.hidden)cerrarInfo()}};addEventListener("keydown",tecla);

  // ── Tamaño, visibilidad y bucle ──
  const ajustar=()=>{const w=cont.clientWidth,h=cont.clientHeight;r.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();if(w<640&&obj.r===M3_VISTA.r)obj.r=V.r=58};
  const ro=new ResizeObserver(ajustar);ro.observe(cont);ajustar();
  let visible=true;const io=new IntersectionObserver(es=>{visible=es[0].isIntersecting});io.observe(cont);
  M3={r,ro,io,raf:0,tecla,sel:seleccionar,rep:empezarRep};cont.querySelector(".m3-carga").remove();
  const t0=performance.now();let ult=0;
  const bucle=now=>{if(!canvas.isConnected)return mundoStop();M3.raf=requestAnimationFrame(bucle);if(!visible||document.hidden)return;
    const t=(now-t0)/1000,dt=Math.min(.05,(now-ult)/1000||.016);ult=now;const k=1-Math.pow(0.003,dt);
    for(const c of ["th","ph","r","tx","tz"])V[c]+=(obj[c]-V[c])*k;
    if(!rm&&!arr&&!SEL&&!REP.activo&&info.hidden)obj.th+=dt*0.02;
    cam.position.set(V.tx+V.r*Math.sin(V.th)*Math.sin(V.ph),V.r*Math.cos(V.ph)+1,V.tz+V.r*Math.cos(V.th)*Math.sin(V.ph));cam.lookAt(V.tx,1.6,V.tz);
    for(const s of Object.values(est))s.panel.quaternion.copy(cam.quaternion);
    for(const [id,s] of Object.entries(est)){const on=!SEL||SEL===id||REP.activo&&REP.pasos[REP.i]&&(REP.pasos[REP.i].a===id||REP.pasos[REP.i].de===id);s.panel.children[0].material.opacity=on?1:.35;s.halo.material.opacity=on?(s.act?.55:.2):.05}
    cartelN.quaternion.copy(cam.quaternion);
    for(const f of anim)f(t);
    r.render(sc,cam)};
  M3.raf=requestAnimationFrame(bucle);
}
