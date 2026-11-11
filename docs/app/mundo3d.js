// ═══════════ La oficina en 3D: un mundo que se puede recorrer ═══════════
// Three.js r128 (ya cargado por el panel). Todo lo que se ve sale de oficina.json,
// oficina_datos.json y estado.json: cada trabajador, la cinta de producción con los
// vídeos reales, el Manual, la pizarra de mejora, los encargos y la promoción.
let M3=null;
const M3_VISTA={th:-0.62,ph:0.96,r:36,tx:0,tz:0.5};
const ZONAS={
 pre:{t:"Preproducción",c:"#9b87f5",x:-8.6,z:-0.4,w:7.6,d:7.4},
 pro:{t:"Producción",c:"#5aa2ff",x:0.2,z:-0.4,w:8.4,d:7.4},
 dis:{t:"Distribución",c:"#3987e5",x:8.9,z:-0.4,w:6.2,d:7.4},
};
const PUESTOS3D={
 estratega:{x:-10.5,z:-2.2,zona:"pre"},director:{x:-6.8,z:-2.2,zona:"pre"},seo:{x:-8.6,z:1.9,zona:"pre"},
 fotografia:{x:-1.9,z:-2.2,zona:"pro"},motion:{x:2.3,z:-2.2,zona:"pro"},sonido:{x:-1.9,z:1.9,zona:"pro"},editor:{x:2.3,z:1.9,zona:"pro"},
 social:{x:7.3,z:-2.2,zona:"dis"},paid:{x:10.5,z:-2.2,zona:"dis"},
};
const ESTACIONES=[["propuesto","Guion",["propuesto"]],["aprobado","Voz",["aprobado"]],["voz","Escena 3D",["voz","rehacer"]],["escena","Render",["escena","renderizando"]],["revision","Tu revisión",["revision"]]];
const OBJ3D={
 reunion:{x:0,z:6.6,t:"Sala de reuniones",d:"Cada lunes el equipo repasa la semana, propone ideas y mejoras y vota."},
 manual:{x:-12.6,z:6.2,t:"Manual vivo",d:"Las reglas que la oficina ha aprendido de tus datos."},
 pizarra:{x:-14.3,z:-1,t:"Mejora del día",d:"Lo que los datos dicen hoy de la cámara, la voz, los gráficos y el sonido."},
 buzon:{x:12.2,z:6.2,t:"Buzón de encargos",d:"Lo que le pides a la oficina. Lo recoge la siguiente pasada."},
 cohete:{x:9,z:2.6,t:"Plataforma de promoción",d:"Vídeos que despegan solos y se pueden empujar con poco dinero."},
 pantalla:{x:0,z:-9.75,t:"Pantalla de resultados",d:"Cómo van los vídeos frente a lo normal."},
 cinta:{x:0,z:-7.2,t:"Cinta de producción",d:"Tus vídeos reales, en la fase en la que está cada uno."},
};
const RECORRIDO=[
 {o:"cinta",t:"La cinta de producción",d:"Cada caja es uno de tus vídeos. Avanzan de izquierda a derecha: guion, voz, escena 3D, render y tu revisión. Toca una caja para ver cuál es."},
 {p:"estratega",t:"1 · Estrategia elige el tema",d:"Mira tendencias, comentarios y lo que mejor ha funcionado, y propone qué vídeo hacer."},
 {p:"director",t:"2 · Dirección escribe el guion",d:"Con el gancho, el juego de la cifra y el cierre. Las líneas de colores son revisiones: Estrategia, SEO y Gráficos le corrigen antes de que te llegue."},
 {p:"seo",t:"3 · SEO prepara cada red",d:"Título y pie distintos para TikTok, Instagram y YouTube."},
 {p:"fotografia",t:"4 · Producción lo hace realidad",d:"Cámara plantea los planos, Gráficos los contadores, Sonido la voz y los efectos, y Montaje lo sincroniza todo. Se revisan entre ellos con la hoja de contactos."},
 {o:"pizarra",t:"5 · Cada día aprenden",d:"El auditor mide la voz y la escena de cada vídeo y lo cruza con las vistas. Aquí aparece qué potenciar y qué corregir; los trabajadores lo aplican en la siguiente pasada."},
 {o:"manual",t:"6 · El Manual vivo",d:"Lo que se confirma con los datos se convierte en regla. Tú decides qué pasa a ser ley."},
 {o:"reunion",t:"7 · La reunión de los lunes",d:"Los nueve proponen ideas y mejoras a sus compañeros, se vota, y las mejores van al banco de ideas."},
 {p:"social",t:"8 · Distribución",d:"Comunidad responde y convierte preguntas en vídeos; Promoción detecta lo que despega."},
 {o:"buzon",t:"9 · Tú mandas",d:"Deja aquí cualquier encargo y la oficina te contesta en la siguiente pasada."},
];

function mundoStop(){if(!M3)return;cancelAnimationFrame(M3.raf);M3.ro&&M3.ro.disconnect();M3.io&&M3.io.disconnect();removeEventListener("keydown",M3.tecla);try{M3.r.dispose()}catch(e){}M3=null}
if(typeof heroStop==="function"){const _hs=heroStop;heroStop=function(){_hs();mundoStop()}}

function mundoHTML(){
  return `<div class="ofi3d fade" id="ofi3d">
   <canvas aria-label="Oficina en 3D: arrastra para girar, toca a un trabajador para ver qué hace"></canvas>
   <div class="m3-etqs"></div>
   <div class="m3-barra">
    <button class="btn peq" data-m3="tour">${ic("play","s")}Recorrido guiado</button>
    <button class="btn sec peq" data-m3="general">${ic("home","s")}Vista general</button>
    <button class="btn sec peq" data-m3="lineas">${ic("refresh","s")}Revisiones</button>
   </div>
   <div class="m3-ayuda">${ic("info","s")}<span>Arrastra para girar · rueda o pellizco para acercar · toca a alguien</span></div>
   <div class="m3-info" hidden></div>
   <div class="m3-tip" hidden></div>
   <div class="m3-carga">Montando la oficina…</div>
  </div>`;
}

function texCanvas(w,h,pinta){const c=document.createElement("canvas");c.width=w;c.height=h;const g=c.getContext("2d");pinta(g,w,h);const t=new THREE.CanvasTexture(c);t.anisotropy=4;return t}
function rr(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath()}
function textoAjustado(g,txt,x,y,maxW,lh,maxL){const pal=String(txt).split(" ");let l="",n=0;for(const p of pal){const t=l?l+" "+p:p;if(g.measureText(t).width>maxW&&l){g.fillText(l,x,y+n*lh);n++;l=p;if(n>=maxL-1){l=pal.slice(pal.indexOf(p)).join(" ");while(g.measureText(l+"…").width>maxW&&l.length)l=l.slice(0,-1);if(l!==pal.slice(pal.indexOf(p)).join(" "))l+="…";break}}else l=t}if(l)g.fillText(l,x,y+n*lh);return n+1}

async function mundo3d(cont){
  mundoStop();
  if(!cont)return;
  const canvas=cont.querySelector("canvas");
  let r;try{if(!window.THREE)throw 0;r=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false})}catch(e){cont.innerHTML=`<div class="vacio">${ic("alert")}<b>Tu navegador no puede mostrar la oficina en 3D</b>Abajo tienes las fichas del equipo.</div>`;return}
  try{await document.fonts?.ready}catch(e){}
  const rm=matchMedia("(prefers-reduced-motion: reduce)").matches;
  r.setPixelRatio(Math.min(devicePixelRatio||1,2));r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;r.outputEncoding=THREE.sRGBEncoding;
  const sc=new THREE.Scene();sc.background=new THREE.Color("#0d0f15");sc.fog=new THREE.Fog("#0d0f15",48,90);
  const cam=new THREE.PerspectiveCamera(34,1,0.5,200);
  sc.add(new THREE.HemisphereLight("#cfd8ff","#2a2218",0.75));
  const sol=new THREE.DirectionalLight("#fff4e0",0.85);sol.position.set(-12,24,14);sol.castShadow=true;sol.shadow.mapSize.set(1536,1536);
  Object.assign(sol.shadow.camera,{left:-20,right:20,top:16,bottom:-16,near:1,far:70});sol.shadow.bias=-0.0005;sc.add(sol);
  const luzCalida=new THREE.PointLight("#ffd23f",0.45,26);luzCalida.position.set(0,5,6.6);sc.add(luzCalida);

  const mats={};const mat=(c,o={})=>{const k=c+JSON.stringify(o);return mats[k]||(mats[k]=new THREE.MeshLambertMaterial({color:c,...o}))};
  const malla=(geo,c,x,y,z,o={})=>{const m=new THREE.Mesh(geo,typeof c==="string"?mat(c):c);m.position.set(x,y,z);m.castShadow=o.sombra!==false;m.receiveShadow=true;(o.padre||sc).add(m);return m};
  const caja=(w,h,d,c,x,y,z,o)=>malla(new THREE.BoxGeometry(w,h,d),c,x,y,z,o);
  const cil=(rt,rb,h,c,x,y,z,o={})=>malla(new THREE.CylinderGeometry(rt,rb,h,o.seg||20),c,x,y,z,o);
  const esf=(rad,c,x,y,z,o={})=>malla(new THREE.SphereGeometry(rad,o.seg||20,14),c,x,y,z,o);
  const clicables=[],etiquetas=[],anim=[];
  const clic=(obj,info)=>{obj.traverse(o=>{if(o.isMesh){o.userData.info=info;clicables.push(o)}});return obj};

  // ── Suelo, paredes y zonas ──
  const suelo=caja(32,0.4,24,"#1b1f2a",0,-0.2,0,{sombra:false});suelo.receiveShadow=true;
  const tSuelo=texCanvas(512,384,(g,w,h)=>{g.fillStyle="#1b1f2a";g.fillRect(0,0,w,h);g.strokeStyle="rgba(255,255,255,.045)";g.lineWidth=2;for(let x=0;x<=w;x+=32){g.beginPath();g.moveTo(x,0);g.lineTo(x,h);g.stroke()}for(let y=0;y<=h;y+=32){g.beginPath();g.moveTo(0,y);g.lineTo(w,y);g.stroke()}});
  const sTop=new THREE.Mesh(new THREE.PlaneGeometry(32,24),new THREE.MeshLambertMaterial({map:tSuelo}));sTop.rotation.x=-Math.PI/2;sTop.position.y=0.005;sTop.receiveShadow=true;sc.add(sTop);
  caja(32,7,0.4,"#232838",0,3.3,-12,{sombra:false});caja(0.4,7,24,"#20242f",-16,3.3,0,{sombra:false});
  for(const x of [-11,-5,5,11]){caja(3.6,2.4,0.1,"#2f3a55",x,4.4,-11.78,{sombra:false});caja(3.6,2.4,0.05,new THREE.MeshBasicMaterial({color:"#6b88c9",transparent:true,opacity:.25}),x,4.4,-11.7,{sombra:false})}
  // logotipo en la pared
  const tLogo=texCanvas(512,128,(g,w,h)=>{g.fillStyle="#ffd23f";rr(g,8,14,100,100,24);g.fill();g.fillStyle="#15151a";g.font="800 46px 'Space Grotesk'";g.textAlign="center";g.textBaseline="middle";g.fillText("60s",58,66);g.fillStyle="#f4f3ef";g.textAlign="left";g.font="700 52px 'Space Grotesk'";g.fillText("explicadoen60s",130,58);g.fillStyle="#9496a3";g.font="500 26px Inter";g.fillText("La oficina",132,100)});
  const logo=new THREE.Mesh(new THREE.PlaneGeometry(8,2),new THREE.MeshBasicMaterial({map:tLogo,transparent:true}));logo.position.set(-15.78,5.2,-6.5);logo.rotation.y=Math.PI/2;sc.add(logo);
  for(const [k,z] of Object.entries(ZONAS)){
    const alfombra=caja(z.w,0.06,z.d,mat(z.c,{transparent:true,opacity:.16}),z.x,0.03,z.z,{sombra:false});alfombra.castShadow=false;
    const tz=texCanvas(512,96,(g,w,h)=>{g.fillStyle=z.c;g.font="700 54px 'Space Grotesk'";g.textAlign="center";g.textBaseline="middle";g.fillText(z.t.toUpperCase(),w/2,h/2)});
    const p=new THREE.Mesh(new THREE.PlaneGeometry(4.2,0.8),new THREE.MeshBasicMaterial({map:tz,transparent:true,opacity:.85}));p.rotation.x=-Math.PI/2;p.position.set(z.x,0.07,z.z+z.d/2-0.55);sc.add(p);
  }
  // plantas
  for(const [x,z] of [[-14.6,-10.4],[14.4,-10.4],[-14.6,9.8],[5.4,9.6]]){cil(0.45,0.35,0.8,"#7a5a3c",x,0.4,z);esf(0.85,"#3f8f4f",x,1.5,z);esf(0.6,"#4fa65f",x+0.3,2.1,z-0.2)}

  // ── Trabajadores ──
  const equipo=OFI.equipo,P_=OFD.puestos||{},rep=OFD.reputacion||{},pieles=["#f1c7a3","#d9a07a","#b97a56","#8d5a3b","#f5d2b5","#c68c64","#e8b48f","#a06a48","#f0c19a"];
  const cabezas={};
  equipo.forEach((e,i)=>{
    const pos=PUESTOS3D[e.id];if(!pos)return;
    const g=new THREE.Group();g.position.set(pos.x,0,pos.z);sc.add(g);
    // mesa
    caja(2.6,0.12,1.4,"#e7dcc8",0,1.0,0.35,{padre:g});
    for(const [dx,dz] of [[-1.15,-0.2],[1.15,-0.2],[-1.15,0.9],[1.15,0.9]])caja(0.1,1.0,0.1,"#9c8f7a",dx,0.5,dz,{padre:g});
    // monitor (mira al trabajador) con su número en la pantalla
    const k=P_[e.id]?.kpi,niv=kpiNivel(k);
    caja(1.5,0.95,0.08,"#141820",0,1.75,0.85,{padre:g});cil(0.05,0.05,0.4,"#141820",0,1.25,0.85,{padre:g,seg:8});
    const tMon=texCanvas(300,190,(gg,w,h)=>{gg.fillStyle="#0e1320";gg.fillRect(0,0,w,h);gg.fillStyle=e.color;gg.fillRect(0,0,w,10);gg.fillStyle="#9496a3";gg.font="600 20px Inter";gg.fillText((k?.nombre||"").slice(0,26),14,46);
      gg.fillStyle=niv==="ok"?"#34c77b":niv==="warn"?"#f5a524":niv==="err"?"#f05252":"#f4f3ef";gg.font="700 64px 'Space Grotesk'";gg.fillText(fmtKpi(k),14,118);
      if(k?.meta!=null&&k.valor!=null){gg.fillStyle="#262a36";gg.fillRect(14,146,w-28,10);gg.fillStyle=gg.fillStyle=niv==="ok"?"#34c77b":niv==="warn"?"#f5a524":"#f05252";gg.fillRect(14,146,(w-28)*Math.min(1,k.valor/k.meta),10)}});
    const pant=new THREE.Mesh(new THREE.PlaneGeometry(1.38,0.84),new THREE.MeshBasicMaterial({map:tMon}));pant.position.set(0,1.75,0.805);pant.rotation.y=Math.PI;g.add(pant);
    // silla
    cil(0.55,0.55,0.12,"#2b2f3c",0,0.62,-0.75,{padre:g});caja(1.0,0.9,0.12,"#2b2f3c",0,1.1,-1.25,{padre:g});cil(0.06,0.06,0.55,"#555b6b",0,0.32,-0.75,{padre:g,seg:8});
    // aro de estado bajo la silla
    const aro=new THREE.Mesh(new THREE.RingGeometry(0.9,1.08,40),new THREE.MeshBasicMaterial({color:niv==="ok"?"#34c77b":niv==="warn"?"#f5a524":niv==="err"?"#f05252":"#5f6271",transparent:true,opacity:.7,side:THREE.DoubleSide}));aro.rotation.x=-Math.PI/2;aro.position.set(0,0.04,-0.75);g.add(aro);
    // persona (sentada, de cara a la cámara, trabajando en el monitor de espaldas a nosotros… girada para que se le vea)
    const per=new THREE.Group();per.position.set(0,0,-0.7);g.add(per);
    cil(0.42,0.5,1.05,e.color,0,1.25,0,{padre:per});
    esf(0.42,e.color,0,1.78,0,{padre:per});
    const piel=pieles[i%pieles.length];
    const cabeza=esf(0.4,piel,0,2.32,0,{padre:per});
    const pelo=new THREE.Mesh(new THREE.SphereGeometry(0.42,20,12,0,Math.PI*2,0,Math.PI*0.5),mat(["#2b1d14","#4a3222","#111","#6b4a2e","#c9a26b"][i%5]));pelo.position.set(0,2.36,-0.02);pelo.castShadow=true;per.add(pelo);
    for(const s of [-1,1]){esf(0.06,"#15151a",0.14*s,2.36,0.36,{padre:per,seg:8,sombra:false})}
    const brazos=[];for(const s of [-1,1]){const b=new THREE.Group();b.position.set(0.5*s,1.6,0);per.add(b);cil(0.11,0.11,0.75,e.color,0,-0.3,0.18,{padre:b,seg:10}).rotation.x=-1.0;esf(0.13,piel,0,-0.55,0.52,{padre:b,seg:10});brazos.push(b)}
    // accesorio de su oficio
    accesorio(e.id,g,{caja,cil,esf,mat});
    cabezas[e.id]=new THREE.Vector3(pos.x,3.2,pos.z-0.7);
    clic(g,{tipo:"puesto",id:e.id});
    const pend=P_[e.id]?.pendiente||0;
    etiquetas.push({pos:new THREE.Vector3(pos.x,3.35,pos.z-0.7),html:`<span class="m3-dot" style="background:${e.color}"></span>${esc(e.nombre)}${pend?`<span class="m3-pend">${pend}</span>`:""}`,id:e.id,clase:"persona"});
    const ritmo=pend?2.2:1;
    anim.push(t=>{if(rm)return;per.position.y=Math.sin(t*1.6+i)*0.03;brazos[0].rotation.x=Math.sin(t*9*ritmo+i)*0.18;brazos[1].rotation.x=Math.sin(t*9*ritmo+i+1.7)*0.18;cabeza.rotation.y=Math.sin(t*0.5+i*1.3)*0.35;aro.material.opacity=.45+.3*(0.5+0.5*Math.sin(t*2+i))});
  });

  // ── Cinta de producción con los vídeos reales ──
  const cinta=new THREE.Group();sc.add(cinta);
  caja(24,0.5,1.6,"#2a2f3d",0,0.75,-7.2,{padre:cinta});
  const tBanda=texCanvas(512,32,(g,w,h)=>{g.fillStyle="#15181f";g.fillRect(0,0,w,h);g.fillStyle="#262b38";for(let x=0;x<w;x+=32)g.fillRect(x,0,14,h)});tBanda.wrapS=THREE.RepeatWrapping;tBanda.repeat.set(12,1);
  const banda=new THREE.Mesh(new THREE.PlaneGeometry(24,1.4),new THREE.MeshLambertMaterial({map:tBanda}));banda.rotation.x=-Math.PI/2;banda.position.set(0,1.01,-7.2);banda.receiveShadow=true;cinta.add(banda);
  for(let x=-11.5;x<=11.5;x+=2.3)caja(0.14,0.75,1.4,"#3a4152",x,0.38,-7.2,{padre:cinta,sombra:false});
  clic(cinta,{tipo:"obj",id:"cinta"});
  const estCol=["#ffd23f","#34c77b","#5aa2ff","#d55181","#f5a524"];
  ESTACIONES.forEach(([k,t,estados],i)=>{
    const x=-9.6+i*4.8,vs=PROD.filter(v=>estados.includes(v.estado));
    // arco de la estación
    caja(0.16,2.6,0.16,"#4a5266",x-1.5,1.3,-8.1,{padre:cinta});caja(0.16,2.6,0.16,"#4a5266",x+1.5,1.3,-8.1,{padre:cinta});
    const tEst=texCanvas(320,96,(g,w,h)=>{g.fillStyle="#141820";rr(g,0,0,w,h,18);g.fill();g.fillStyle=estCol[i];g.font="700 40px 'Space Grotesk'";g.textAlign="center";g.fillText(t,w/2,44);g.fillStyle="#c9c9d1";g.font="600 26px Inter";g.fillText(`${vs.length} vídeo${vs.length===1?"":"s"}`,w/2,80)});
    const cartel=new THREE.Mesh(new THREE.PlaneGeometry(3.2,0.96),new THREE.MeshBasicMaterial({map:tEst,transparent:true}));cartel.position.set(x,2.95,-8.05);cinta.add(cartel);
    vs.slice(0,8).forEach((v,j)=>{
      const fila=j%4,piso=Math.floor(j/4);
      const bx=caja(0.62,0.5,0.62,estCol[i],x-1.0+fila*0.66,1.27+piso*0.52,-7.2,{padre:cinta});
      caja(0.64,0.08,0.2,"#f4f3ef",bx.position.x,bx.position.y+0.06,-7.2,{padre:cinta,sombra:false});
      clic(bx,{tipo:"video",id:v.id});
      anim.push(t=>{if(rm)return;bx.position.y=1.27+piso*0.52+Math.max(0,Math.sin(t*2.4+j+i*1.3))*0.06});
    });
    if(vs.length>8)etiquetas.push({pos:new THREE.Vector3(x,2.4,-7.2),html:`+${vs.length-8}`,clase:"mini"});
  });
  // caja viajera: un vídeo recorriendo la cinta
  const viajera=caja(0.55,0.45,0.55,"#ffd23f",-11,1.25,-7.2,{padre:cinta});
  anim.push(t=>{if(rm)return;const u=(t*0.06)%1;viajera.position.x=-11.5+23*u;viajera.material.color.set(estCol[Math.min(4,Math.floor(u*5))]);tBanda.offset.x=-t*0.12});

  // ── Pantalla de resultados en la pared ──
  const dir=P_.director?.kpi,est=P_.estratega?.kpi;
  const tPan=texCanvas(900,360,(g,w,h)=>{g.fillStyle="#0b0f19";g.fillRect(0,0,w,h);g.strokeStyle="#ffd23f";g.lineWidth=6;g.strokeRect(3,3,w-6,h-6);
    g.fillStyle="#9496a3";g.font="600 30px Inter";g.fillText("ÚLTIMOS 14 DÍAS",40,62);
    const cols=[["Frente a lo normal",fmtKpi(dir)],["Por encima de lo normal",fmtKpi(est)],["Vídeos analizados",String(OFD.maduros??"—")]];
    cols.forEach(([t,v],i)=>{const x=40+i*290;g.fillStyle="#f4f3ef";g.font="700 96px 'Space Grotesk'";g.fillText(v,x,190);g.fillStyle="#c9c9d1";g.font="500 26px Inter";g.fillText(t,x,236)});
    g.fillStyle="#5f6271";g.font="500 24px Inter";g.fillText(OFD.actualizado?"Datos "+hace(OFD.actualizado):"",40,316)});
  caja(9.4,3.8,0.2,"#141820",0,4.3,-11.7,{sombra:false});
  const pan=new THREE.Mesh(new THREE.PlaneGeometry(9,3.6),new THREE.MeshBasicMaterial({map:tPan}));pan.position.set(0,4.3,-11.58);sc.add(pan);clic(pan,{tipo:"obj",id:"pantalla"});

  // ── Pizarra de la mejora del día (pared izquierda) ──
  const mej=OFD.mejora||{},hall=(mej.hallazgos||[]).slice(0,4),exps=OFI.experimentos||[];
  const tPiz=texCanvas(800,560,(g,w,h)=>{g.fillStyle="#f4f3ef";g.fillRect(0,0,w,h);g.fillStyle="#15151a";g.font="700 44px 'Space Grotesk'";g.fillText("Mejora del día",34,62);
    g.fillStyle="#6b6e7a";g.font="500 22px Inter";g.fillText(`${exps.filter(x=>x.estado==="activo").length} experimentos en marcha · ${mej.medidos||0} vídeos auditados`,36,98);
    let y=150;hall.forEach(hh=>{const rol=rolDe(hh.rol);g.fillStyle=rol.color;g.beginPath();g.arc(48,y-8,12,0,7);g.fill();g.fillStyle="#15151a";g.font="600 24px Inter";const n=textoAjustado(g,hh.texto,74,y,w-110,30,3);y+=n*30+22});
    if(!hall.length){g.fillStyle="#6b6e7a";g.font="500 26px Inter";g.fillText("Esperando datos del auditor…",36,160)}});
  caja(0.2,3.6,5.4,"#c9c2b4",-15.75,3.2,-1,{sombra:false});
  const piz=new THREE.Mesh(new THREE.PlaneGeometry(5.1,3.4),new THREE.MeshBasicMaterial({map:tPiz}));piz.position.set(-15.63,3.2,-1);piz.rotation.y=Math.PI/2;sc.add(piz);clic(piz,{tipo:"obj",id:"pizarra"});

  // ── Estantería del Manual vivo ──
  const est3=new THREE.Group();est3.position.set(OBJ3D.manual.x,0,OBJ3D.manual.z);sc.add(est3);
  caja(3.2,3.6,0.9,"#6b4f36",0,1.8,0,{padre:est3});for(const y of [0.9,1.9,2.9])caja(3,0.08,0.8,"#8a6a4a",0,y,0.05,{padre:est3});
  const reglas=OFI.manual.filter(m=>m.estado!=="descartada");
  reglas.slice(0,24).forEach((m,i)=>{const fila=Math.floor(i/8),col=i%8;const alto=0.62+((i*37)%5)*0.04;
    const c=m.estado==="ley"?"#ffd23f":m.estado==="propuesta"?"#34c77b":"#5aa2ff";caja(0.28,alto,0.55,c,-1.2+col*0.34,0.95+fila+alto/2,0.12,{padre:est3})});
  clic(est3,{tipo:"obj",id:"manual"});
  etiquetas.push({pos:new THREE.Vector3(OBJ3D.manual.x,4.1,OBJ3D.manual.z),html:`${ic("book","s")}Manual vivo <span class="m3-pend am">${OFI.manual.filter(m=>m.estado==="ley").length} leyes</span>`,clase:"objeto",obj:"manual"});

  // ── Sala de reuniones ──
  const sala=new THREE.Group();sala.position.set(OBJ3D.reunion.x,0,OBJ3D.reunion.z);sc.add(sala);
  cil(2.3,2.3,0.14,"#e7dcc8",0,1.02,0,{padre:sala,seg:40});cil(0.25,0.4,1.0,"#9c8f7a",0,0.5,0,{padre:sala});
  equipo.forEach((e,i)=>{const a=i/equipo.length*Math.PI*2;cil(0.35,0.35,0.1,e.color,Math.cos(a)*3,0.6,Math.sin(a)*3,{padre:sala,seg:14});caja(0.6,0.6,0.08,e.color,Math.cos(a)*3.35,0.95,Math.sin(a)*3.35,{padre:sala}).lookAt(sala.position.x,0.95,sala.position.z)});
  const tRe=texCanvas(256,256,(g,w,h)=>{g.fillStyle="#ffd23f";g.beginPath();g.arc(128,128,120,0,7);g.fill();g.fillStyle="#15151a";g.textAlign="center";g.font="700 34px 'Space Grotesk'";g.fillText("LUNES",128,112);g.font="600 30px Inter";g.fillText("11:37",128,156)});
  const disco=new THREE.Mesh(new THREE.CircleGeometry(1.1,40),new THREE.MeshBasicMaterial({map:tRe,transparent:true}));disco.rotation.x=-Math.PI/2;disco.position.y=1.1;sala.add(disco);
  clic(sala,{tipo:"obj",id:"reunion"});
  etiquetas.push({pos:new THREE.Vector3(OBJ3D.reunion.x,2.6,OBJ3D.reunion.z),html:`${ic("users","s")}Reunión · ${fmtDiaC(proximaReunion())}`,clase:"objeto",obj:"reunion"});

  // ── Buzón de encargos ──
  const bz=new THREE.Group();bz.position.set(OBJ3D.buzon.x,0,OBJ3D.buzon.z);sc.add(bz);
  cil(0.12,0.12,1.4,"#555b6b",0,0.7,0,{padre:bz,seg:8});caja(1.3,0.9,0.8,"#d55181",0,1.8,0,{padre:bz});
  const nEnc=OFI.encargos.filter(e=>e.estado!=="hecho").length;
  for(let i=0;i<Math.min(nEnc,5);i++)caja(0.9,0.05,0.6,"#f4f3ef",0,2.3+i*0.07,0.05,{padre:bz,sombra:false});
  const bandera=caja(0.08,0.6,0.08,"#ffd23f",0.7,2.2,0,{padre:bz});
  anim.push(t=>{if(!rm&&nEnc)bandera.rotation.z=Math.sin(t*3)*0.25});
  clic(bz,{tipo:"obj",id:"buzon"});
  etiquetas.push({pos:new THREE.Vector3(OBJ3D.buzon.x,3.1,OBJ3D.buzon.z),html:`${ic("send","s")}Encargos${nEnc?`<span class="m3-pend">${nEnc}</span>`:""}`,clase:"objeto",obj:"buzon"});

  // ── Plataforma de promoción ──
  const cand=(OFD.paid_candidatos||[]).filter(c=>!c.decidido).length;
  const pl=new THREE.Group();pl.position.set(OBJ3D.cohete.x,0,OBJ3D.cohete.z);sc.add(pl);
  cil(1.2,1.4,0.3,"#3a4152",0,0.15,0,{padre:pl,seg:30});
  const cohete=new THREE.Group();pl.add(cohete);
  cil(0.32,0.38,1.5,"#f4f3ef",0,1.15,0,{padre:cohete,seg:16});malla(new THREE.ConeGeometry(0.32,0.6,16),"#f05252",0,2.2,0,{padre:cohete});
  for(let i=0;i<3;i++){const a=i/3*Math.PI*2;caja(0.08,0.5,0.4,"#f05252",Math.cos(a)*0.38,0.6,Math.sin(a)*0.38,{padre:cohete}).rotation.y=-a}
  const llama=malla(new THREE.ConeGeometry(0.22,0.6,12),new THREE.MeshBasicMaterial({color:"#ffb703"}),0,0.15,0,{padre:cohete,sombra:false});llama.rotation.x=Math.PI;
  anim.push(t=>{if(rm)return;const s=cand?1:0.25;llama.scale.set(1,s*(0.8+0.3*Math.sin(t*20)),1);cohete.position.y=cand?Math.abs(Math.sin(t*1.4))*0.25:0});
  clic(pl,{tipo:"obj",id:"cohete"});
  etiquetas.push({pos:new THREE.Vector3(OBJ3D.cohete.x,3.2,OBJ3D.cohete.z),html:`${ic("rocket","s")}Promoción${cand?`<span class="m3-pend">${cand}</span>`:""}`,clase:"objeto",obj:"cohete"});
  etiquetas.push({pos:new THREE.Vector3(OBJ3D.pizarra.x+0.4,5.3,OBJ3D.pizarra.z),html:`${ic("spark","s")}Mejora del día`,clase:"objeto",obj:"pizarra"});
  etiquetas.push({pos:new THREE.Vector3(-9.6,3.9,-7.2),html:`${ic("film","s")}Cinta de producción`,clase:"objeto",obj:"cinta"});

  // ── Revisiones: sobres que viajan del que revisa al revisado ──
  const lineas=[];
  for(const e of equipo)for(const d of e.revisa||[]){
    const a=cabezas[e.id],b=cabezas[d];if(!a||!b)continue;
    const medio=a.clone().add(b).multiplyScalar(0.5);medio.y+=2.2+a.distanceTo(b)*0.12;
    const curva=new THREE.QuadraticBezierCurve3(a,medio,b);
    const lin=new THREE.Line(new THREE.BufferGeometry().setFromPoints(curva.getPoints(40)),new THREE.LineBasicMaterial({color:e.color,transparent:true,opacity:.28}));sc.add(lin);
    const sobre=esf(0.13,new THREE.MeshBasicMaterial({color:e.color}),0,0,0,{sombra:false,seg:10});
    const fase=Math.random();lineas.push({de:e.id,a:d,lin,sobre,curva,fase});
  }
  let verLineas=true;
  anim.push(t=>{for(const L of lineas){const u=(t*0.18+L.fase)%1;L.sobre.position.copy(L.curva.getPoint(u));const foco=!SEL||SEL===L.de||SEL===L.a;L.sobre.visible=verLineas&&foco;L.lin.visible=verLineas;L.lin.material.opacity=foco?(SEL?.75:.28):.06}});

  // ── Etiquetas HTML que siguen a los objetos ──
  const capa=cont.querySelector(".m3-etqs");
  capa.innerHTML=etiquetas.map((e,i)=>`<button class="m3-etq ${e.clase}" data-i="${i}">${e.html}</button>`).join("");
  pintarIconos(capa);
  const els=[...capa.children];
  els.forEach((el,i)=>el.onclick=()=>{const e=etiquetas[i];if(e.id)seleccionar({tipo:"puesto",id:e.id});else if(e.obj)seleccionar({tipo:"obj",id:e.obj})});

  // ── Cámara orbital con el ratón y con los dedos ──
  const V=Object.assign({},M3_VISTA),obj=Object.assign({},V);let SEL=null;
  const fijar=(o)=>Object.assign(obj,o);
  let arr=null,movido=0;const ptrs=new Map();let pinch=null;
  canvas.addEventListener("pointerdown",e=>{canvas.setPointerCapture(e.pointerId);ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});arr={x:e.clientX,y:e.clientY};movido=0;if(ptrs.size===2){const [p,q]=[...ptrs.values()];pinch={d:Math.hypot(p.x-q.x,p.y-q.y),r:obj.r}}});
  canvas.addEventListener("pointermove",e=>{
    if(ptrs.has(e.pointerId))ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(pinch&&ptrs.size===2){const [p,q]=[...ptrs.values()];obj.r=Math.min(52,Math.max(12,pinch.r*pinch.d/Math.max(20,Math.hypot(p.x-q.x,p.y-q.y))));movido=99;return}
    if(arr){const dx=e.clientX-arr.x,dy=e.clientY-arr.y;movido+=Math.abs(dx)+Math.abs(dy);obj.th-=dx*0.006;obj.ph=Math.min(1.32,Math.max(0.42,obj.ph-dy*0.005));arr={x:e.clientX,y:e.clientY};if(movido>6)ocultarTip3()}
    else hover(e)});
  const fin=e=>{ptrs.delete(e.pointerId);if(ptrs.size<2)pinch=null;if(arr&&movido<6&&e.type==="pointerup")tocar(e);if(!ptrs.size)arr=null};
  canvas.addEventListener("pointerup",fin);canvas.addEventListener("pointercancel",fin);canvas.addEventListener("pointerleave",e=>{if(!ptrs.size)ocultarTip3()});
  canvas.addEventListener("wheel",e=>{e.preventDefault();obj.r=Math.min(52,Math.max(12,obj.r*(1+Math.sign(e.deltaY)*0.09)))},{passive:false});
  const ray=new THREE.Raycaster(),ndc=new THREE.Vector2();
  const pick=e=>{const b=canvas.getBoundingClientRect();ndc.set((e.clientX-b.left)/b.width*2-1,-((e.clientY-b.top)/b.height)*2+1);ray.setFromCamera(ndc,cam);const h=ray.intersectObjects(clicables,false)[0];return h?.object.userData.info||null};
  const tip=cont.querySelector(".m3-tip");
  function ocultarTip3(){tip.hidden=true;canvas.style.cursor="grab"}
  function hover(e){const i=pick(e);if(!i){ocultarTip3();return}canvas.style.cursor="pointer";const b=cont.getBoundingClientRect();tip.hidden=false;tip.innerHTML=textoInfo(i,true);tip.style.left=Math.min(b.width-240,e.clientX-b.left+14)+"px";tip.style.top=(e.clientY-b.top+14)+"px"}
  function tocar(e){const i=pick(e);if(i)seleccionar(i);else{SEL=null;cerrarInfo()}}

  const info=cont.querySelector(".m3-info");
  function textoInfo(i,corto){
    if(i.tipo==="puesto"){const e=rolDe(i.id),p=P_[i.id]||{};return corto?`<b>${esc(e.nombre)}</b><small>${esc(e.puesto)}</small><span>${esc(p.ahora||"")}</span>`:""}
    if(i.tipo==="video"){const v=PROD.find(x=>x.id===i.id);return `<b>${esc(v?.titulo||i.id)}</b><small>${esc(FASES[v?.estado]||"")}</small>`}
    const o=OBJ3D[i.id];return `<b>${esc(o?.t||"")}</b><small>${esc(o?.d||"")}</small>`;
  }
  function cerrarInfo(){info.hidden=true;SEL=null;els.forEach(el=>el.classList.remove("on","atenua"))}
  function seleccionar(i){
    ocultarTip3();
    if(i.tipo==="puesto"){
      SEL=i.id;const p=PUESTOS3D[i.id],e=rolDe(i.id),d=P_[i.id]||{},k=d.kpi,rp=rep[i.id]||{};
      fijar({tx:p.x,tz:p.z,r:15,ph:0.9});
      const recs=Object.values(OFD.mejora?.recomendaciones||{}).flat().filter(x=>x.rol===i.id&&x.tipo==="mejorar").length;
      const acts=OFI.actividad.filter(a=>a.rol===i.id).slice(-2).reverse();
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button>
        <div class="ofi-cab">${avatarRol(i.id,40)}<div><b>${esc(e.nombre)}</b><small>${esc(e.puesto)}</small></div></div>
        <p class="m3-mision">${esc(e.mision||"")}</p>
        <div class="m3-fila">${ic("clock","s")}<span>${esc(d.ahora||"—")}</span></div>
        ${k?`<div class="m3-fila">${ic("target","s")}<span>${esc(k.nombre)}: <b class="${kpiNivel(k)}">${fmtKpi(k)}</b>${k.meta!=null?` · objetivo ${fmtKpi({...k,valor:k.meta})}`:""}</span></div>`:""}
        ${d.foco?`<div class="m3-fila foco">${ic("spark","s")}<span><b>Su foco hoy:</b> ${esc(d.foco)}</span></div>`:""}
        ${recs?`<div class="m3-fila">${ic("alert","s")}<span>${recs} cosas por mejorar en vídeos en marcha</span></div>`:""}
        <div class="m3-fila">${ic("star","s")}<span>Voto ×${String(rp.peso??1).replace(".",",")} · ${rp.n?`acierta ${rp.aciertos}/${rp.n}`:"sin predicciones aún"}</span></div>
        <div class="m3-fila">${ic("refresh","s")}<span>Revisa a ${(e.revisa||[]).map(x=>esc(rolDe(x).nombre)).join(", ")}</span></div>
        ${acts.map(a=>`<div class="m3-cita">«${esc(a.texto.slice(0,150))}»<small>${hace(a.fecha)}</small></div>`).join("")}
        <div class="m3-acc"><button class="btn peq" data-a="enc">${ic("send","s")}Encargarle algo</button><button class="btn sec peq" data-a="ficha">Ficha completa</button></div>`;
      info.querySelector('[data-a="enc"]').onclick=()=>nuevoEncargo(i.id);info.querySelector('[data-a="ficha"]').onclick=()=>verPuesto(i.id);
    }else if(i.tipo==="video"){
      const v=PROD.find(x=>x.id===i.id)||{};SEL=null;fijar({tx:0,tz:-6.5,r:17,ph:0.85});
      const recs=(OFD.mejora?.recomendaciones||{})[i.id]||[],revs=v.revisiones||[];
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button><b class="m3-tit">${esc(v.titulo||i.id)}</b><small class="mut">${esc(FASES[v.estado]||"")} · formato ${esc(v.formato||"?")}</small>
        ${revs.length?`<div class="m3-fila">${ic("users","s")}<span>${revs.filter(r=>r.veredicto==="ok").length}/${revs.length} revisiones a favor</span></div>`:""}
        ${recs.slice(0,5).map(x=>`<div class="m3-fila ${x.tipo}">${avatarRol(x.rol,22)}<span>${x.tipo==="mejorar"?"<b>Mejorar:</b> ":"<b>Potenciar:</b> "}${esc(x.texto)}</span></div>`).join("")||`<p class="mut peq">El auditor lo medirá en cuanto tenga voz y escena.</p>`}
        <div class="m3-acc"><a class="btn peq" href="#/prod/${v.estado==="propuesto"?"guiones":v.estado==="revision"?"borradores":"marcha"}">Abrir en Producción</a></div>`;
    }else{
      const o=OBJ3D[i.id];SEL=null;fijar({tx:o.x*0.85,tz:o.z*0.9,r:16,ph:0.88});
      const dest={manual:["manual","Abrir el Manual vivo"],reunion:["reuniones","Ver las actas"],buzon:["encargos","Encargar algo"],cohete:["promocion","Ver candidatos"],pizarra:["mejora","Ver la mejora diaria"],pantalla:["predicciones","Ver predicciones"],cinta:["","Abrir Producción"]}[i.id]||["",""];
      let extra="";
      if(i.id==="pizarra")extra=(OFD.mejora?.hallazgos||[]).slice(0,3).map(h=>`<div class="m3-fila">${avatarRol(h.rol,22)}<span>${esc(h.texto)}</span></div>`).join("");
      if(i.id==="manual")extra=OFI.manual.filter(m=>m.estado==="ley").slice(0,4).map(m=>`<div class="m3-fila">${ic("check","s")}<span>${esc(m.texto)}</span></div>`).join("");
      if(i.id==="reunion"){const u=OFI.reuniones[OFI.reuniones.length-1];extra=u?`<div class="m3-fila">${ic("report","s")}<span>Última: ${fmtDiaC(u.fecha)} · ${esc(u.resumen||"")}</span></div>`:`<p class="mut peq">La primera será el ${fmtDiaC(proximaReunion())}.</p>`}
      if(i.id==="cinta")extra=ESTACIONES.map(([k,t,es])=>`<div class="m3-fila"><span><b>${t}:</b> ${PROD.filter(v=>es.includes(v.estado)).length}</span></div>`).join("");
      info.innerHTML=`<button class="ib m3-x" aria-label="Cerrar">${ic("x","s")}</button><b class="m3-tit">${esc(o.t)}</b><p class="m3-mision">${esc(o.d)}</p>${extra}
        <div class="m3-acc"><a class="btn peq" href="${dest[0]?`#/ofi/${dest[0]}`:"#/prod"}">${dest[1]}</a></div>`;
    }
    info.hidden=false;pintarIconos(info);info.querySelector(".m3-x").onclick=()=>{cerrarInfo();fijar({...M3_VISTA})};
    els.forEach((el,k)=>{const e=etiquetas[k];el.classList.toggle("on",(e.id&&e.id===SEL)||(e.obj&&e.obj===i.id));el.classList.toggle("atenua",!!SEL&&e.clase==="persona"&&e.id!==SEL&&!(rolDe(SEL).revisa||[]).includes(e.id)&&!(rolDe(SEL).le_revisan||[]).includes(e.id))});
  }

  // ── Recorrido guiado ──
  let paso=-1;
  function verPaso(n){paso=n;const s=RECORRIDO[n];if(!s){paso=-1;cerrarInfo();fijar({...M3_VISTA});return}
    if(s.p)seleccionar({tipo:"puesto",id:s.p});else seleccionar({tipo:"obj",id:s.o});
    info.insertAdjacentHTML("afterbegin",`<div class="m3-paso"><small>Paso ${n+1} de ${RECORRIDO.length}</small><b>${esc(s.t)}</b><p>${esc(s.d)}</p><div class="m3-acc"><button class="btn sec peq" data-t="-1" ${n?"":"disabled"}>${ic("left","s")}Anterior</button><button class="btn peq" data-t="1">${n<RECORRIDO.length-1?"Siguiente":"Terminar"}${ic("right","s")}</button></div></div>`);
    pintarIconos(info);info.querySelectorAll("[data-t]").forEach(b=>b.onclick=()=>verPaso(paso+ +b.dataset.t))}
  cont.querySelectorAll("[data-m3]").forEach(b=>b.onclick=()=>{const a=b.dataset.m3;
    if(a==="tour")verPaso(0);else if(a==="general"){paso=-1;cerrarInfo();fijar({...M3_VISTA})}else if(a==="lineas"){verLineas=!verLineas;b.classList.toggle("on",verLineas)}});
  cont.querySelector('[data-m3="lineas"]').classList.add("on");
  const tecla=e=>{if(!cont.isConnected)return;if(e.key==="Escape"&&!info.hidden){cerrarInfo();fijar({...M3_VISTA})}};addEventListener("keydown",tecla);

  // ── Tamaño, visibilidad y bucle ──
  const ajustar=()=>{const w=cont.clientWidth,h=cont.clientHeight;r.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();if(w<640&&V.r===M3_VISTA.r){obj.r=V.r=48}};
  const ro=new ResizeObserver(ajustar);ro.observe(cont);ajustar();
  let visible=true;const io=new IntersectionObserver(es=>{visible=es[0].isIntersecting});io.observe(cont);
  M3={r,ro,io,raf:0,tecla};
  const t0=performance.now(),tmp=new THREE.Vector3();let ultimo=0;
  cont.querySelector(".m3-carga").remove();
  const bucle=now=>{
    if(!canvas.isConnected)return mundoStop();
    M3.raf=requestAnimationFrame(bucle);
    if(!visible||document.hidden)return;
    const t=(now-t0)/1000,dt=Math.min(.05,(now-ultimo)/1000||.016);ultimo=now;
    const k=1-Math.pow(0.0025,dt);for(const c of ["th","ph","r","tx","tz"])V[c]+=(obj[c]-V[c])*k;
    if(!rm&&!arr&&!SEL&&paso<0&&info.hidden)obj.th+=dt*0.025;
    cam.position.set(V.tx+V.r*Math.sin(V.th)*Math.sin(V.ph),V.r*Math.cos(V.ph),V.tz+V.r*Math.cos(V.th)*Math.sin(V.ph));cam.lookAt(V.tx,0.8,V.tz);
    for(const f of anim)f(t);
    r.render(sc,cam);
    const W=cont.clientWidth,H=cont.clientHeight,lejos=V.r>40;
    etiquetas.forEach((e,i)=>{const el=els[i];tmp.copy(e.pos).project(cam);const fuera=tmp.z>1||Math.abs(tmp.x)>1.1||Math.abs(tmp.y)>1.1;
      if(fuera||(lejos&&e.clase==="mini")){el.style.display="none";return}el.style.display="";el.style.transform=`translate(-50%,-100%) translate(${(tmp.x*.5+.5)*W}px,${(-tmp.y*.5+.5)*H}px)`;el.style.zIndex=String(1000-Math.round(tmp.z*900))});
  };
  M3.raf=requestAnimationFrame(bucle);
}

function accesorio(id,g,{caja,cil,esf,mat}){
  const o={padre:g};
  if(id==="director"){caja(0.7,0.45,0.05,"#15151a",0.85,1.3,0.1,o);const t=caja(0.72,0.1,0.06,"#f4f3ef",0.85,1.57,0.1,o);t.rotation.z=0.25}
  else if(id==="fotografia"){caja(0.5,0.35,0.35,"#15151a",-0.85,1.25,0.2,o);cil(0.13,0.15,0.3,"#2f3a55",-0.85,1.25,0.0,o).rotation.x=Math.PI/2;caja(0.05,0.9,0.05,"#555b6b",-1.4,0.45,-1.4,o)}
  else if(id==="sonido"){const t=new THREE.Mesh(new THREE.TorusGeometry(0.45,0.06,8,24,Math.PI),mat("#15151a"));t.position.set(0,2.35,-0.7);g.add(t);esf(0.14,"#34c77b",-0.44,2.32,-0.7,o);esf(0.14,"#34c77b",0.44,2.32,-0.7,o);cil(0.04,0.04,0.5,"#888",0.95,1.3,0.2,o)}
  else if(id==="editor"){for(const x of [-0.95,-0.6]){cil(0.18,0.18,0.06,"#f5a524",x,1.12,0.25,o).rotation.x=0}}
  else if(id==="motion"){cil(0.32,0.32,0.04,"#f4f3ef",0.85,1.08,0.15,o);["#f05252","#ffd23f","#5aa2ff","#34c77b"].forEach((c,i)=>esf(0.06,c,0.75+(i%2)*0.2,1.12,0.05+Math.floor(i/2)*0.2,{...o,seg:8}))}
  else if(id==="estratega"){for(const [r,c] of [[0.45,"#f05252"],[0.32,"#f4f3ef"],[0.18,"#f05252"]]){const d=cil(r,r,0.04,c,-0.85,1.55,0.3,o);d.rotation.x=Math.PI/2;d.position.z=0.3+(0.45-r)*0.05}}
  else if(id==="social"){esf(0.25,"#3987e5",0.9,1.45,0.2,o);caja(0.6,0.4,0.05,"#f4f3ef",-0.85,1.3,0.2,o)}
  else if(id==="paid"){cil(0.1,0.12,0.45,"#f4f3ef",0.9,1.32,0.2,o);const c=new THREE.Mesh(new THREE.ConeGeometry(0.1,0.2,10),mat("#f05252"));c.position.set(0.9,1.65,0.2);g.add(c);cil(0.18,0.18,0.08,"#ffd23f",-0.85,1.1,0.2,o)}
  else if(id==="seo"){const t=new THREE.Mesh(new THREE.TorusGeometry(0.2,0.04,8,20),mat("#2fb5a8"));t.position.set(0.85,1.4,0.15);g.add(t);caja(0.06,0.35,0.06,"#2fb5a8",1.02,1.18,0.15,o).rotation.z=0.6}
}
