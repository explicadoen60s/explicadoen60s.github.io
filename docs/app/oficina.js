// ═══════════ La oficina: el equipo que produce, se corrige y aprende solo ═══════════
// Lee produccion/oficina.json (lo escriben Claude y el panel) y produccion/oficina_datos.json
// (lo calcula produccion/oficina.py cada hora con las estadísticas).
P.users='<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>';
P.book='<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>';
P.send='<path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4Z"/>';
P.dice='<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1"/><circle cx="15.5" cy="15.5" r="1"/><circle cx="15.5" cy="8.5" r="1"/><circle cx="8.5" cy="15.5" r="1"/>';

let OFI=null,OFD=null,OFI_FILTRO="todos";
const TIPO_ACT={revision:["Revisión","info"],propuesta:["Propuesta","acc"],mejora:["Mejora","ok"],analisis:["Análisis","info"],reunion:["Reunión","acc"],aviso:["Aviso","warn"],encargo:["Encargo","ok"],prediccion:["Predicción",""]};
const VEREDICTO={a_favor:["Los datos la apoyan","ok"],en_contra:["Los datos la contradicen","err"],sin_efecto:["Sin efecto claro","warn"],faltan_datos:["Faltan vídeos para saberlo","" ]};
const ESTADO_MANUAL={ley:"Ley",hipotesis:"En prueba",propuesta:"Propuesta del equipo",descartada:"Descartada"};
const CAMPOS_FILTRO=[["formato","Formato (A, B o C)","igual"],["juego","Lleva juego de la cifra","igual",true],["comentario","Responde a un comentario","igual",true],["serie","Serie «Lo que esconde tu ciudad»","igual",true],["titulo_pregunta","Título en forma de pregunta","igual",true],["titulo_cifra","Título con una cifra","igual",true],["duracion","Dura menos de… (segundos)","menor"],["tendencia","Sale de una tendencia","igual",true],["idea","Sale del banco de ideas","igual",true],["cotidiano","Nota «cotidiano» mayor que…","mayor"],["ensenar","Nota «enséñalo» mayor que…","mayor"]];

const rolDe=id=>(OFI?.equipo||[]).find(e=>e.id===id)||{id,nombre:id==="tu"?"Tú":id||"Equipo",puesto:"",icono:"user",color:"#9496a3"};
const avatarRol=(id,t=34)=>{const r=rolDe(id);return `<span class="ofi-av" style="--c:${r.color};width:${t}px;height:${t}px" title="${esc(r.nombre)}">${ic(r.icono,"s")}</span>`};
const fmtKpi=k=>{if(!k||k.valor==null)return "—";const v=k.valor;return k.fmt==="pct"?pct(v,0):k.fmt==="x"?fmtX(v):k.fmt==="s"?String(v).replace(".",",")+" s":k.fmt==="dec"?String(v).replace(".",","):fmtN(v)};
const kpiNivel=k=>k?.valor==null||k.meta==null?"":(k.nombre.startsWith("Duración")?(Math.abs(k.valor-k.meta)<=6?"ok":"warn"):k.valor>=k.meta?"ok":k.valor>=k.meta*.7?"warn":"err");
const hoyISO=()=>new Date().toISOString();

async function cargarOficina(){
  const [o,d]=await Promise.all([json("produccion/oficina.json",{opcional:true,ttl:15000}),json("produccion/oficina_datos.json",{opcional:true,ttl:30000})]);
  OFI=o||{equipo:[],actividad:[],manual:[],reuniones:[],predicciones:{},encargos:[],paid:[]};OFD=d||{};
  for(const k of ["actividad","manual","reuniones","encargos","paid","experimentos","diario","canal","acuerdos","jornadas"])OFI[k]=OFI[k]||[];OFI.predicciones=OFI.predicciones||{};
  return [OFI,OFD];
}
function pendientesOficina(){
  const enc=OFI.encargos.filter(e=>e.estado!=="hecho").length,prop=OFI.manual.filter(m=>m.estado==="propuesta").length;
  const paid=(OFD.paid_candidatos||[]).filter(c=>!c.decidido).length;
  return {enc,prop,paid,total:prop+paid};
}
function proximaReunion(){const p=partes(new Date());const dia=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].indexOf(p.weekday);let d=(7-dia)%7;if(d===0&&+p.hour>=12)d=7;const f=new Date(Date.now()+d*864e5);const q=partes(f);return aIso(`${q.year}-${q.month}-${q.day}T11:37`)}

async function vistaOfi(sub){
  const [,est]=await Promise.all([cargarOficina(),json("produccion/estado.json",{ttl:15000})]);PROD=est?.videos||PROD;
  const pend=pendientesOficina();contarSeccion("ofi",pend.total);
  acciones(`<span class="mut peq" style="align-self:center">${OFD.actualizado?"Datos "+hace(OFD.actualizado):"Sin datos todavía"}</span><button class="btn" onclick="nuevoEncargo()">${ic("send","s")}Encargar algo</button>`);
  const nMan=OFI.manual.filter(m=>m.estado==="propuesta").length;
  const nExp=(OFI.experimentos||[]).filter(x=>x.estado==="activo").length;
  const ultJ=OFI.jornadas[OFI.jornadas.length-1],nCanal=OFI.canal.filter(m=>ultJ&&m.jornada===(ultJ.fecha||"").slice(0,10)).length;
  let h=segmentos("ofi",[["equipo","Centro de control"],["canal","Canal",nCanal],["mejora","Mejora diaria",nExp],["manual","Manual vivo",nMan],["reuniones","Reuniones"],["encargos","Encargos",pend.enc],["promocion","Promoción",pend.paid],["predicciones","Predicciones"],["actividad","Actividad"]],sub);
  if(sub==="manual")h+=ofiManual();
  else if(sub==="reuniones")h+=ofiReuniones();
  else if(sub==="encargos")h+=ofiEncargos();
  else if(sub==="promocion")h+=ofiPromocion();
  else if(sub==="predicciones")h+=ofiPredicciones();
  else if(sub==="actividad")h+=ofiActividad();
  else if(sub==="mejora")h+=ofiMejora();
  else if(sub==="canal")h+=ofiCanal();
  else h+=ofiEquipo();
  app.innerHTML=h;animarKpis();
  if(!sub||sub==="equipo")despuesDePintar=()=>mundo3d($("#ofi3d"));
}

// ── Equipo ──
function ofiEquipo(){
  if(!OFI.equipo.length)return `<div class="card">${vacio("users","La oficina está vacía","Falta produccion/oficina.json en el repositorio.")}</div>`;
  const P_=OFD.puestos||{},rep=OFD.reputacion||{};
  const pendTot=Object.values(P_).reduce((s,p)=>s+(p.pendiente||0),0);
  const leyes=OFI.manual.filter(m=>m.estado==="ley").length,hip=OFI.manual.filter(m=>m.estado==="hipotesis").length;
  const ult=OFI.reuniones[OFI.reuniones.length-1],pr=proximaReunion();
  const accs=Object.values(rep).filter(r=>r.n);const accMed=accs.length?accs.reduce((s,r)=>s+r.aciertos,0)/accs.reduce((s,r)=>s+r.n,0):null;
  let h=`<div class="grid g4">${kpi("Tareas en la mesa",pendTot,"sumando los 9 puestos","list")}${kpi("Reglas aprendidas",leyes,`${hip} más en prueba`,"book")}${kpi("Mejoras propuestas",OFI.actividad.filter(a=>a.tipo==="mejora"||a.tipo==="propuesta").length,"entre compañeros","idea")}
   <div class="card kpi fade"><div class="lab">${ic("users","s")}Próxima reunión</div><div class="val" style="font-size:22px">${fmtDiaC(pr)}</div><div class="pie">${ult?`Última: ${fmtDiaC(ult.fecha)}`:"Será la primera"}${accMed!=null?` · aciertan el ${pct(accMed,0)}`:""}</div></div></div>`;
  h=mundoHTML()+h;
  h+=`<div class="card fade ofi-flujo-card"><div class="h3">${ic("refresh")}Cómo se pasa el trabajo<span class="sub">Cada entrega la revisan dos compañeros antes de llegarte; tú decides en los tres puntos amarillos</span></div>${flujoOficina()}</div>`;
  h+=`<div class="h3 ofi-subt">${ic("users")}Fichas del equipo<span class="sub">Toca una para ver todo lo que hace</span></div><div class="ofi-equipo">`+OFI.equipo.map(e=>{const p=P_[e.id]||{},k=p.kpi,r=rep[e.id]||{},act=OFI.actividad.filter(a=>a.rol===e.id).slice(-1)[0];
    const niv=kpiNivel(k),ancho=k?.valor!=null&&k.meta?Math.min(100,k.valor/k.meta*100):0;
    return `<button class="card ofi-tarj fade" style="--c:${e.color}" onclick="verPuesto('${e.id}')">
     <div class="ofi-cab">${avatarRol(e.id,42)}<div style="min-width:0;flex:1"><b>${esc(e.nombre)}</b><small>${esc(e.puesto)}</small></div>${p.pendiente?`<span class="badge" title="Tareas pendientes">${p.pendiente}</span>`:""}</div>
     <div class="ofi-ahora">${ic("clock","s")}<span>${esc(p.ahora||"Esperando datos de la próxima pasada")}</span></div>
     ${k?`<div class="ofi-kpi"><div><small>${esc(k.nombre)}</small><b class="${niv}">${fmtKpi(k)}</b>${k.meta!=null?`<small> / objetivo ${fmtKpi({...k,valor:k.meta})}</small>`:""}</div>${k.meta!=null?`<div class="barra"><i class="${niv}" style="width:${ancho}%"></i></div>`:""}<small class="mut">${esc(k.pie||"")}</small></div>`:""}
     <div class="ofi-pie"><span title="Peso de su voto en las reuniones (sube si acierta sus predicciones)">${ic("star","s")}voto ×${String(r.peso??1).replace(".",",")}</span><span>${r.n?`acierta ${r.aciertos}/${r.n}`:"sin predicciones aún"}</span><span class="ofi-revisa">revisa a ${(e.revisa||[]).map(x=>avatarRol(x,20)).join("")}</span></div>
     ${p.foco?`<div class="ofi-foco">${ic("spark","s")}<span>${esc(p.foco)}</span></div>`:""}
     ${act?`<div class="ofi-ult">«${esc(act.texto.slice(0,140))}${act.texto.length>140?"…":""}»<small>${hace(act.fecha)}</small></div>`:""}
    </button>`}).join("")+`</div>`;
  if((OFD.segundas_partes||[]).length)h+=`<div class="card fade"><div class="h3">${ic("rocket")}Piden segunda parte<span class="sub">Más de 10 veces lo normal: el equipo de Estrategia la propondrá en la próxima pasada</span></div>${OFD.segundas_partes.map(s=>`<div class="fila">${redPill(s.red)}<span class="t"><b>${esc(s.titulo||s.video)}</b><small>${fmtX(s.rel)} lo normal · ${fmtN(s.vistas)} vistas</small></span></div>`).join("")}</div>`;
  return h;
}
function flujoOficina(){
  const pasos=[["estratega","Elige tema"],["director","Escribe guion"],[["seo","motion","estratega"],"Revisión cruzada"],["tu","Apruebas guion"],["sonido","Voz y ritmo"],["fotografia","Planos"],["motion","Gráficos"],["editor","Montaje"],[["editor","fotografia"],"Hoja de contactos"],["tu","Apruebas vídeo"],[["seo","social"],"Publica"],["paid","Empuja lo que despega"],[["estratega","social"],"Datos → Manual"]];
  return `<div class="ofi-flujo">${pasos.map(([r,t],i)=>{const rs=Array.isArray(r)?r:[r];const tu=r==="tu";
    return `<div class="ofi-paso ${tu?"tu":""}"><div class="ofi-avs">${tu?`<span class="ofi-av tu">${ic("user","s")}</span>`:rs.map(x=>avatarRol(x,26)).join("")}</div><small>${t}</small></div>${i<pasos.length-1?`<span class="ofi-flecha">${ic("right","s")}</span>`:""}`}).join("")}<span class="ofi-flecha">${ic("refresh","s")}</span></div>`;
}
function verPuesto(id){
  const e=rolDe(id),p=(OFD.puestos||{})[id]||{},acts=OFI.actividad.filter(a=>a.rol===id||a.para===id).slice(-25).reverse(),enc=OFI.encargos.filter(x=>x.rol===id&&x.estado!=="hecho");
  modal(`<div class="ofi-cab" style="margin-bottom:10px">${avatarRol(id,48)}<div><h2 style="font-size:20px">${esc(e.nombre)}</h2><small class="mut">${esc(e.puesto)}</small></div></div>
   <p>${esc(e.mision||"")}</p>${e.regla_de_oro?`<div class="msg info">${ic("star","s")}<div><b>Su regla de oro:</b> ${esc(e.regla_de_oro)}</div></div>`:""}
   <dl class="kv"><dt>Entrega</dt><dd>${(e.entrega||[]).map(x=>`<span class="pill">${esc(x)}</span>`).join(" ")}</dd><dt>Revisa a</dt><dd>${(e.revisa||[]).map(x=>esc(rolDe(x).nombre)).join(", ")}</dd><dt>Le revisan</dt><dd>${(e.le_revisan||[]).map(x=>esc(rolDe(x).nombre)).join(", ")}</dd><dt>Ahora</dt><dd>${esc(p.ahora||"—")}</dd></dl>
   ${enc.length?`<label>Encargos pendientes</label>${enc.map(x=>`<div class="fila"><span class="t"><b>${esc(x.texto)}</b><small>${hace(x.fecha)}</small></span></div>`).join("")}`:""}
   <label>Su actividad</label><div style="max-height:320px;overflow:auto">${acts.length?acts.map(filaActividad).join(""):`<p class="mut peq">Todavía no ha dejado nada por escrito.</p>`}</div>
   <div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap"><button class="btn" data-x="enc">${ic("send","s")}Encargarle algo</button><button class="btn sec" data-x="cerrar">Cerrar</button></div>`,{alAbrir:(m,cerrar)=>{m.querySelector('[data-x="cerrar"]').onclick=()=>cerrar();m.querySelector('[data-x="enc"]').onclick=()=>{cerrar();nuevoEncargo(id)}}});
}
function filaActividad(a){const t=TIPO_ACT[a.tipo]||[a.tipo||"Nota",""];const v=a.video?(PROD.find(x=>x.id===a.video)?.titulo||a.video):"";
  return `<div class="fila ofi-act">${avatarRol(a.rol,30)}<span class="t"><span class="ofi-txt">${a.para?`<b class="ofi-de">${esc(rolDe(a.rol).nombre)} → ${esc(rolDe(a.para).nombre)}</b> `:`<b class="ofi-de">${esc(rolDe(a.rol).nombre)}</b> `}${esc(a.texto)}</span><small><span class="pill ${t[1]}">${t[0]}</span>${v?`<span>${esc(v.slice(0,60))}</span>`:""}<span>${hace(a.fecha)}</span>${a.estado?`<span class="pill ${a.estado==="aplicada"?"ok":a.estado==="rechazada"?"err":""}">${esc(a.estado)}</span>`:""}</small></span></div>`}

// ── Manual vivo ──
function ofiManual(){
  const ev=OFD.manual||{},grupos=[["propuesta","Propuestas del equipo","Reglas que el equipo quiere añadir: decides tú"],["ley","Leyes","Se aplican en todos los guiones y escenas"],["hipotesis","En prueba","Se comprueban solas con cada vídeo publicado; cuando los datos las apoyan, te proponen hacerlas ley"],["descartada","Descartadas",""]];
  let h=`<div class="msg info">${ic("book","s")}<div>El <b>Manual vivo</b> es la memoria de la oficina. Cada regla con un <b>filtro</b> se mide sola cada hora: compara los vídeos que la cumplen con los que no (vistas frente a lo normal en su red, con al menos ${3} vídeos a cada lado). Las leyes se escriben en <code>CLAUDE.md</code> en la siguiente pasada.</div></div>`;
  for(const [k,t,d] of grupos){const ms=OFI.manual.map((m,i)=>({...m,i})).filter(m=>(m.estado||"hipotesis")===k);if(!ms.length&&k!=="hipotesis")continue;
    h+=`<div class="card fade ${k==="descartada"?"plano":""}"><div class="h3">${ic(k==="ley"?"check":k==="propuesta"?"idea":k==="descartada"?"x":"dice")}${t}<span class="sub">${d}</span></div>`;
    h+=k==="descartada"?`<details><summary>${ms.length} reglas</summary>${ms.map(m=>reglaManual(m,ev[m.id])).join("")}</details>`:(ms.map(m=>reglaManual(m,ev[m.id])).join("")||`<p class="mut peq">Nada en prueba ahora mismo.</p>`);
    if(k==="hipotesis")h+=`<button class="btn sec peq" style="margin-top:10px" onclick="nuevaRegla()">${ic("plus","s")}Proponer una regla para probar</button>`;
    h+=`</div>`}
  const sen=(OFD.senales||[]).filter(s=>!OFI.manual.some(m=>JSON.stringify(m.filtro)===JSON.stringify(s.filtro)));
  if(sen.length)h+=`<div class="card fade"><div class="h3">${ic("spark")}Señales que han salido solas<span class="sub">Patrones que ya se ven en los datos y nadie ha convertido en regla</span></div>${sen.map((s,i)=>`<div class="fila"><span class="pill ${s.veredicto==="a_favor"?"ok":"err"}">${fmtX(s.ratio)}</span><span class="t"><b>${esc(s.senal)}</b><small>${s.n_si} vídeos lo cumplen (${fmtX(s.med_si)} lo normal) frente a ${s.n_no} que no (${fmtX(s.med_no)})</small></span><button class="btn sec peq" onclick="senalARegla(${i})">${ic("plus","s")}Probarla</button></div>`).join("")}</div>`;
  return h;
}
function reglaManual(m,e){
  const v=e?VEREDICTO[e.veredicto]:null;
  const barra=e&&e.med_si!=null&&e.med_no!=null?(()=>{const mx=Math.max(e.med_si,e.med_no,1);return `<div class="ofi-ev"><div><small>Con esto · ${e.n_si} vídeos</small><div class="barra"><i style="width:${e.med_si/mx*100}%"></i></div><b>${fmtX(e.med_si)}</b></div><div><small>Sin esto · ${e.n_no} vídeos</small><div class="barra gris"><i style="width:${e.med_no/mx*100}%"></i></div><b>${fmtX(e.med_no)}</b></div></div>`})():"";
  const sugerir=m.estado==="hipotesis"&&e?.veredicto==="a_favor"?`<button class="btn ok peq" onclick="cambiarRegla(${m.i},'ley')">${ic("check","s")}Hacerla ley</button>`:"";
  const alarma=m.estado==="ley"&&e?.veredicto==="en_contra"?`<div class="msg warn">${ic("alert","s")}<div>Los datos ya no apoyan esta ley. ¿La pasamos a prueba?</div></div>`:"";
  const btns=m.estado==="propuesta"?`<button class="btn ok peq" onclick="cambiarRegla(${m.i},'ley')">${ic("check","s")}Aceptar como ley</button><button class="btn sec peq" onclick="cambiarRegla(${m.i},'hipotesis')">${ic("dice","s")}Probarla primero</button><button class="btn fantasma peq" onclick="cambiarRegla(${m.i},'descartada')">${ic("x","s")}Descartar</button>`
   :m.estado==="ley"?`<button class="btn fantasma peq" onclick="cambiarRegla(${m.i},'hipotesis')">${ic("dice","s")}Volver a prueba</button>`
   :m.estado==="descartada"?`<button class="btn fantasma peq" onclick="cambiarRegla(${m.i},'hipotesis')">${ic("refresh","s")}Recuperar</button>`
   :`${sugerir}<button class="btn fantasma peq" onclick="cambiarRegla(${m.i},'descartada')">${ic("x","s")}Descartar</button>`;
  return `<div class="ofi-regla">${avatarRol(m.por,30)}<div style="flex:1;min-width:0"><b>${esc(m.texto)}</b><small class="mut">${esc(rolDe(m.por).nombre)} · ${m.creada?fmtDiaC(m.creada):""}${m.origen?` · ${esc(m.origen)}`:""}</small>
   ${v?`<div style="margin-top:6px"><span class="pill ${v[1]}">${v[0]}${e.ratio!=null?` · ${fmtX(e.ratio)}`:""}</span></div>`:m.filtro?"":`<div style="margin-top:6px"><span class="pill">Regla de criterio: no se mide sola</span></div>`}${barra}${alarma}
   <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">${btns}</div></div></div>`;
}
async function cambiarRegla(i,estado){const m=OFI.manual[i];
  await accion(()=>editarJson("produccion/oficina.json",d=>{const r=d.manual.find(x=>x.id===m.id);if(!r)return;r.estado=estado;r.decidida=hoyISO();r.decidida_por=usuario;
    (d.actividad=d.actividad||[]).push({fecha:hoyISO(),rol:"tu",tipo:"reunion",texto:`${estado==="ley"?"Hace ley":estado==="descartada"?"Descarta":"Pone en prueba"}: «${r.texto}»`})},`Panel: regla ${m.id} → ${estado} [skip ci]`),estado==="ley"?"Ahora es ley: el equipo la aplicará desde la próxima pasada.":"Guardado.")}
async function nuevaRegla(pre){
  modal(`<h2 style="font-size:19px">Proponer una regla</h2><p class="mut peq">Escríbela como una afirmación que se pueda comprobar. Si eliges cómo medirla, la oficina la comprobará sola con cada vídeo.</p>
   <label>La regla</label><textarea id="nr_t" placeholder="Los vídeos que empiezan con una pregunta funcionan mejor">${esc(pre?.texto||"")}</textarea>
   <label>Cómo se mide</label><select id="nr_c"><option value="">No se mide sola (regla de criterio)</option>${CAMPOS_FILTRO.map(([c,t])=>`<option value="${c}" ${pre?.filtro?.campo===c?"selected":""}>${t}</option>`).join("")}</select>
   <div id="nr_vw"><label>Valor</label><input id="nr_v" value="${esc(pre?.filtro?(pre.filtro.igual??pre.filtro.menor??pre.filtro.mayor??""):"")}" placeholder="C · 65 · 8"></div>
   <label>¿Quién la defiende?</label><select id="nr_r">${OFI.equipo.map(e=>`<option value="${e.id}" ${pre?.por===e.id?"selected":""}>${esc(e.nombre)}</option>`).join("")}<option value="tu">Tú</option></select>
   <div style="display:flex;gap:8px;margin-top:16px"><button class="btn" data-x="ok">${ic("check","s")}Ponerla en prueba</button><button class="btn sec" data-x="no">Cancelar</button></div>`,{alAbrir:(m,cerrar)=>{
    const sel=m.querySelector("#nr_c"),vw=m.querySelector("#nr_vw"),pinta=()=>{const c=CAMPOS_FILTRO.find(x=>x[0]===sel.value);vw.style.display=c&&c[3]===undefined?"":"none"};sel.onchange=pinta;pinta();
    m.querySelector('[data-x="no"]').onclick=()=>cerrar();
    m.querySelector('[data-x="ok"]').onclick=async()=>{const t=m.querySelector("#nr_t").value.trim();if(!t)return;const c=CAMPOS_FILTRO.find(x=>x[0]===sel.value);let filtro=null;
      if(c){let v=c[3]!==undefined?c[3]:m.querySelector("#nr_v").value.trim();if(c[2]!=="igual"||/^\d+([.,]\d+)?$/.test(v))v=typeof v==="string"&&v!==""&&!isNaN(+v.replace(",","."))?+v.replace(",","."):v;filtro={campo:c[0],[c[2]]:v}}
      cerrar();const por=m.querySelector("#nr_r").value;
      await accion(()=>editarJson("produccion/oficina.json",d=>{(d.manual=d.manual||[]).push({id:"m"+Date.now().toString(36),texto:t,estado:"hipotesis",por,creada:hoyISO().slice(0,10),origen:pre?.origen||"Propuesta desde el panel",...(filtro?{filtro}:{})})},"Panel: regla nueva en prueba [skip ci]"),"Regla en prueba. Se mide sola cada hora.")}}});
}
function senalARegla(i){const s=(OFD.senales||[]).filter(s=>!OFI.manual.some(m=>JSON.stringify(m.filtro)===JSON.stringify(s.filtro)))[i];if(!s)return;
  nuevaRegla({texto:`${s.senal}: ${s.veredicto==="a_favor"?"rinde más":"rinde menos"} que el resto.`,filtro:s.filtro,por:"estratega",origen:`Señal automática: ${fmtX(s.ratio)} con ${s.n_si} vídeos`})}

// ── Reuniones ──
function ofiReuniones(){
  const rs=[...OFI.reuniones].reverse();
  let h=`<div class="card fade"><div class="h3">${ic("users")}Reunión semanal<span class="sub">Cada lunes a las 11:37 el equipo repasa la semana, cada puesto propone ideas y mejoras a sus compañeros y se vota</span></div>
   <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><span class="pill acc">${ic("clock","s")}Próxima: ${fmtDiaC(proximaReunion())} a las 11:37</span><button class="btn sec peq" onclick="convocarReunion()">${ic("send","s")}Convocar una extraordinaria</button></div></div>`;
  if(!rs.length)return h+`<div class="card">${vacio("users","Aún no ha habido reuniones","El acta de la primera aparecerá aquí con las ideas votadas y las decisiones.")}</div>`;
  return h+rs.map((r,k)=>actaReunion(r,k===0)).join("");
}
function actaReunion(r,abierta){
  const ideas=[...(r.ideas||[])].sort((a,b)=>(b.puntos??0)-(a.puntos??0));
  const cuerpo=`${r.resumen?`<p style="font-size:15px">${esc(r.resumen)}</p>`:""}
   ${(r.repaso||[]).length?`<label>Repaso de la semana</label>${r.repaso.map(x=>`<div class="fila">${avatarRol(x.rol||"estratega",26)}<span class="t"><span class="ofi-txt">${esc(x.texto||x)}</span></span></div>`).join("")}`:""}
   ${ideas.length?`<label>Ideas votadas (impacto × confianza × facilidad, ponderado por el acierto de cada puesto)</label><div class="tablewrap"><table><thead><tr><th></th><th>Idea</th><th>I</th><th>C</th><th>F</th><th>Votos</th><th>Puntos</th><th></th></tr></thead><tbody>${ideas.map(i=>`<tr><td>${avatarRol(i.rol,26)}</td><td style="white-space:normal;min-width:220px"><b>${esc(i.idea)}</b>${i.por_que?`<br><small class="mut">${esc(i.por_que)}</small>`:""}</td><td>${i.ice?.i??"—"}</td><td>${i.ice?.c??"—"}</td><td>${i.ice?.f??"—"}</td><td>${(i.votos||[]).map(v=>avatarRol(v,20)).join("")}</td><td><b>${i.puntos!=null?String(i.puntos).replace(".",","):"—"}</b></td><td>${i.elegida?`<span class="pill ok">${ic("check","s")}Al banco</span>`:""}</td></tr>`).join("")}</tbody></table></div>`:""}
   ${(r.mejoras||[]).length?`<label>Mejoras que se han propuesto entre ellos</label>${r.mejoras.map(m=>`<div class="fila">${avatarRol(m.de,26)}<span class="t"><span class="ofi-txt"><b class="ofi-de">${esc(rolDe(m.de).nombre)} → ${esc(rolDe(m.para).nombre)}</b> ${esc(m.texto)}</span><small>${m.estado?`<span class="pill ${m.estado==="aceptada"?"ok":m.estado==="rechazada"?"err":""}">${esc(m.estado)}</span>`:""}${m.respuesta?esc(m.respuesta):""}</small></span></div>`).join("")}`:""}
   ${(r.decisiones||[]).length?`<label>Decisiones</label><ul class="ofi-lista">${r.decisiones.map(d=>`<li>${esc(d)}</li>`).join("")}</ul>`:""}
   ${(r.reglas||[]).length?`<label>Reglas nuevas al Manual</label><ul class="ofi-lista">${r.reglas.map(d=>`<li>${esc(d)}</li>`).join("")}</ul>`:""}`;
  return `<div class="card fade"><details ${abierta?"open":""}><summary class="h3" style="cursor:pointer">${ic("report")}${r.tipo==="extraordinaria"?"Reunión extraordinaria":"Reunión semanal"} · ${fmtDiaC(r.fecha)}<span class="sub">${(r.ideas||[]).length} ideas · ${(r.mejoras||[]).length} mejoras · ${(r.decisiones||[]).length} decisiones</span></summary>${cuerpo}</details></div>`;
}
async function convocarReunion(){const t=await pedir("¿De qué tiene que hablar el equipo?",{texto:"La próxima pasada de Claude hará una reunión extraordinaria con todos los puestos sobre esto.",largo:true,chips:["Por qué ha bajado esta semana","Ideas para una serie nueva","Cómo conseguir más comentarios","Qué vídeo promocionar"]});if(!t)return;
  await accion(()=>editarJson("produccion/oficina.json",d=>{(d.encargos=d.encargos||[]).push({id:"e"+Date.now().toString(36),tipo:"reunion",rol:"todos",texto:t,por:usuario,fecha:hoyISO(),estado:"pendiente"})},"Panel: reunión extraordinaria [skip ci]"),"Convocada para la próxima pasada.")}

// ── Encargos ──
function ofiEncargos(){
  const pend=OFI.encargos.filter(e=>e.estado!=="hecho").reverse(),hechos=OFI.encargos.filter(e=>e.estado==="hecho").reverse();
  const fila=e=>`<div class="fila">${e.rol&&e.rol!=="todos"?avatarRol(e.rol,30):`<span class="ofi-av" style="--c:#9496a3;width:30px;height:30px">${ic("users","s")}</span>`}<span class="t"><span class="ofi-txt"><b class="ofi-de">${e.tipo==="reunion"?"Reunión: ":""}${e.rol&&e.rol!=="todos"?esc(rolDe(e.rol).nombre):"Todo el equipo"}</b> ${esc(e.texto)}</span><small>${hace(e.fecha)}${e.por?` · ${esc(e.por.split("_")[0])}`:""}${e.respuesta?`</small><div class="msg ok" style="margin:6px 0 0">${ic("check","s")}<div>${esc(e.respuesta)}</div></div><small>`:""}</small></span>${e.estado!=="hecho"?`<button class="ib peligro" title="Quitar" onclick="quitarEncargo('${esc(e.id)}')">${ic("trash","s")}</button>`:""}</div>`;
  return `<div class="card fade"><div class="h3">${ic("send")}Encargar algo a la oficina<span class="sub">Lo recoge la próxima pasada (${fmtHora(proximaPasada())}) y te contesta aquí</span></div>
   <textarea id="enc_t" placeholder="Quiero una serie sobre cosas de la cocina · Mejorad los ganchos de los guiones C · ¿Por qué el vídeo del ticket fue tan mal?"></textarea>
   <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center"><select id="enc_r" style="width:auto;flex:1;min-width:180px"><option value="todos">Todo el equipo</option>${OFI.equipo.map(e=>`<option value="${e.id}">${esc(e.nombre)} · ${esc(e.puesto)}</option>`).join("")}</select><button class="btn" onclick="guardarEncargo()">${ic("send","s")}Encargar</button></div></div>
   <div class="card fade"><div class="h3">${ic("clock")}Pendientes<span class="sub">${pend.length}</span></div>${pend.map(fila).join("")||`<p class="mut peq">Nada pendiente.</p>`}</div>
   ${hechos.length?`<div class="card fade"><div class="h3">${ic("check")}Hechos</div>${hechos.slice(0,30).map(fila).join("")}</div>`:""}`;
}
async function guardarEncargo(rol,texto){texto=texto??$("#enc_t")?.value.trim();rol=rol??$("#enc_r")?.value;if(!texto)return toast("Escribe qué quieres encargar","err");
  await accion(()=>editarJson("produccion/oficina.json",d=>{(d.encargos=d.encargos||[]).push({id:"e"+Date.now().toString(36),rol:rol||"todos",texto,por:usuario,fecha:hoyISO(),estado:"pendiente"})},"Panel: encargo a la oficina [skip ci]"),"Encargado. Lo harán en la próxima pasada.",{recargar:RUTA.s==="ofi"})}
async function nuevoEncargo(rol){const n=rol?rolDe(rol).nombre:"la oficina";const t=await pedir(`¿Qué le encargas a ${n}?`,{texto:"Lo recoge la próxima pasada de Claude y te contesta en Oficina → Encargos.",largo:true});if(!t)return;await guardarEncargo(rol||"todos",t)}
async function quitarEncargo(id){if(!await confirmar("¿Quitar este encargo?","",{si:"Quitar",peligro:true}))return;await accion(()=>editarJson("produccion/oficina.json",d=>{d.encargos=d.encargos.filter(e=>e.id!==id)},"Panel: encargo quitado [skip ci]"),"Quitado")}

// ── Promoción (Paid Media) ──
function ofiPromocion(){
  const cand=OFD.paid_candidatos||[],res=OFD.paid_resultados||[];
  return `<div class="msg info">${ic("rocket","s")}<div><b>Regla de Promoción:</b> solo se paga para empujar lo que ya despega solo (3 veces lo normal o más en sus primeros 5 días y con buena interacción). Se lanza a mano desde la app: en TikTok, «Promocionar» en el vídeo; en Instagram, «Promocionar» en el reel. Cuando lo lances, márcalo aquí para que la oficina mida si compensó.</div></div>
   <div class="card fade"><div class="h3">${ic("rocket")}Candidatos ahora<span class="sub">Se recalculan cada hora</span></div>
   ${cand.length?cand.map((c,i)=>`<div class="fila">${redPill(c.red)}<span class="t"><b>${esc(c.titulo||"")}</b><small>${fmtX(c.rel)} lo normal · ${fmtN(c.vistas)} vistas en ${c.horas} h · interacción ${pct(c.inter)} · objetivo: ${esc(c.objetivo)}</small></span>
     ${c.decidido?`<span class="pill ${c.decidido==="lanzado"?"ok":""}">${c.decidido==="lanzado"?"Lanzada":"Descartada"}</span>`:`<span class="pill acc">${c.presupuesto} €</span><button class="btn ok peq" onclick="decidirPaid(${i},'lanzado')">Lanzada</button><button class="btn fantasma peq" onclick="decidirPaid(${i},'descartado')">No</button>`}${c.url?`<a class="ib" href="${esc(c.url)}" target="_blank" rel="noopener" title="Abrir">${ic("ext","s")}</a>`:""}</div>`).join(""):vacio("rocket","Ningún vídeo está despegando ahora mismo","Mejor no gastar: cuando uno pase de 3 veces lo normal aparecerá aquí con un presupuesto sugerido.")}</div>
   ${res.length?`<div class="card fade"><div class="h3">${ic("chart")}Resultado de las promociones</div><div class="tablewrap"><table><thead><tr><th>Vídeo</th><th>Gasto</th><th>Vistas al lanzar</th><th>Ahora</th><th>Ganadas</th><th>€ por 1.000 vistas</th></tr></thead><tbody>${res.map(r=>`<tr><td style="white-space:normal">${redPill(r.red)} ${esc((r.titulo||"").slice(0,60))}</td><td>${r.gasto??"—"} €</td><td>${fmtN(r.vistas_al_lanzar)}</td><td>${fmtN(r.vistas)}</td><td>${fmtN(r.ganadas)}</td><td><b>${r.coste_mil!=null?String(r.coste_mil).replace(".",","):"—"}</b></td></tr>`).join("")}</tbody></table></div></div>`:""}`;
}
async function decidirPaid(i,estado){const c=(OFD.paid_candidatos||[])[i];if(!c)return;let gasto=null;
  if(estado==="lanzado"){const g=await pedir("¿Cuánto has invertido?",{texto:"En euros. Sirve para calcular cuánto cuesta cada 1.000 vistas extra.",valor:String(c.presupuesto),tipo:"number",si:"Guardar"});if(g==null||g==="")return;gasto=+String(g).replace(",",".")}
  await accion(()=>editarJson("produccion/oficina.json",d=>{d.paid=(d.paid||[]).filter(p=>!(p.red===c.red&&p.id===c.id));d.paid.push({red:c.red,id:c.id,video:c.video,titulo:c.titulo,estado,gasto,vistas_al_lanzar:c.vistas,fecha:hoyISO(),por:usuario});
    (d.actividad=d.actividad||[]).push({fecha:hoyISO(),rol:"paid",tipo:"aviso",video:c.video,texto:estado==="lanzado"?`Promoción lanzada en ${NOMBRE[c.red]} con ${gasto} €: «${(c.titulo||"").slice(0,60)}»`:`Descartada la promoción de «${(c.titulo||"").slice(0,60)}»`})},`Panel: promoción ${estado} [skip ci]`),estado==="lanzado"?"Apuntado. La oficina medirá si compensó.":"Descartado.")}

// ── Predicciones ──
function ofiPredicciones(){
  const rep=OFD.reputacion||{},res=OFD.predicciones||{},rank=OFI.equipo.map(e=>({e,r:rep[e.id]||{}})).sort((a,b)=>(b.r.peso??1)-(a.r.peso??1));
  const abiertas=Object.entries(OFI.predicciones).filter(([id])=>!res[id]).reverse();
  return `<div class="msg info">${ic("dice","s")}<div>Antes de que un guion llegue al panel, cada puesto apuesta cuántas veces lo normal hará el vídeo. Cuando lleva 48 h publicado se compara con la realidad: quien acierta más, <b>pesa más</b> en las votaciones de las reuniones (de ×0,5 a ×2).</div></div>
   <div class="card fade"><div class="h3">${ic("star")}Quién acierta más</div>${rank.map(({e,r})=>`<div class="fila">${avatarRol(e.id,30)}<span class="t"><b>${esc(e.nombre)}</b><small>${r.n?`${r.aciertos} de ${r.n} aciertos · error medio ${r.error_medio!=null?String(r.error_medio).replace(".",","):"—"}`:"Aún sin vídeos que puntuar"}</small></span><div style="width:120px"><div class="barra"><i style="width:${((r.peso??1)/2)*100}%"></i></div></div><b class="num">×${String(r.peso??1).replace(".",",")}</b></div>`).join("")}</div>
   ${abiertas.length?`<div class="card fade"><div class="h3">${ic("clock")}Apuestas abiertas<span class="sub">Se resuelven cuando el vídeo lleve 48 h publicado</span></div>${abiertas.slice(0,15).map(([id,p])=>filaPred(id,p,null)).join("")}</div>`:""}
   ${Object.keys(res).length?`<div class="card fade"><div class="h3">${ic("check")}Resueltas</div>${Object.entries(res).reverse().slice(0,20).map(([id,r])=>filaPred(id,OFI.predicciones[id]||{},r)).join("")}</div>`:""}`;
}
function filaPred(id,p,r){const v=PROD.find(x=>x.id===id);const roles=Object.entries(p.roles||{});
  return `<div class="fila" style="display:block"><div style="display:flex;gap:10px;align-items:center"><span class="t"><b>${esc(v?.titulo||id)}</b></span>${r?`<span class="pill ${r.real>=1?"ok":"err"}">Real: ${fmtX(r.real)}</span>`:""}</div>
   <div class="ofi-preds">${roles.map(([rol,q])=>{const pr=typeof q==="object"?q.rel:q,ok=r?.roles?.[rol]?.ok;return `<span class="ofi-pred ${ok===true?"ok":ok===false?"err":""}" title="${esc(typeof q==="object"&&q.nota?q.nota:"")}">${avatarRol(rol,20)}${fmtX(pr)}</span>`}).join("")}</div></div>`}

// ── Actividad ──
function ofiActividad(){
  const acts=OFI.actividad.filter(a=>OFI_FILTRO==="todos"||a.rol===OFI_FILTRO||a.para===OFI_FILTRO).slice(-150).reverse();
  return `<div class="chips" style="margin-bottom:14px"><button class="chip ${OFI_FILTRO==="todos"?"on":""}" onclick="OFI_FILTRO='todos';ir('ofi','actividad',true)">Todos</button>${OFI.equipo.map(e=>`<button class="chip ${OFI_FILTRO===e.id?"on":""}" onclick="OFI_FILTRO='${e.id}';ir('ofi','actividad',true)"><i style="background:${e.color}"></i>${esc(e.nombre)}</button>`).join("")}</div>
   <div class="card fade">${acts.map(filaActividad).join("")||vacio("users","Sin actividad todavía","Aquí queda todo lo que el equipo revisa, propone y mejora.")}</div>`;
}

// ── En las fichas de Producción ──
function bloqueOficina(v){
  if(!OFI)return "";
  const revs=v.revisiones||[],comp=((OFD?.compuertas||{})[v.id]||[]).filter(c=>c.nivel!=="ok"),pred=OFI.predicciones?.[v.id],seo=v.seo;
  if(!revs.length&&!comp.length&&!pred&&!seo)return "";
  const ok=revs.filter(r=>r.veredicto==="ok").length;
  return `<details class="ofi-bloque" ${revs.some(r=>r.veredicto!=="ok"&&!r.aplicada)||comp.some(c=>c.nivel==="error")?"open":""}><summary>${ic("users","s")}<b>La oficina opina</b><span class="mut peq">${revs.length?`${ok}/${revs.length} revisiones a favor`:""}${comp.length?` · ${comp.length} avisos automáticos`:""}${pred?` · apuestan ${fmtX(mediana(Object.values(pred.roles||{}).map(q=>typeof q==="object"?q.rel:q)))}`:""}</span></summary>
   ${revs.map(r=>`<div class="fila">${avatarRol(r.rol,28)}<span class="t"><span class="ofi-txt"><b class="ofi-de">${esc(rolDe(r.rol).nombre)}</b>${r.fase?` <span class="pill">${esc(r.fase)}</span>`:""} <span class="pill ${r.veredicto==="ok"?"ok":"warn"}">${r.veredicto==="ok"?"De acuerdo":"Propone cambios"}</span> ${esc(r.nota||"")}</span>${r.propuesta?`<small>${ic("idea","s")}${esc(r.propuesta)}${r.aplicada!=null?` <span class="pill ${r.aplicada?"ok":""}">${r.aplicada?"aplicada":"no aplicada"}</span>`:""}${r.respuesta?` · ${esc(r.respuesta)}`:""}</small>`:""}</span></div>`).join("")}
   ${comp.map(c=>`<div class="fila">${avatarRol(c.rol,28)}<span class="t"><span class="ofi-txt"><span class="pill ${c.nivel==="error"?"err":"warn"}">${c.nivel==="error"?"Bloquea":"Aviso"}</span> ${esc(c.texto)}</span></span></div>`).join("")}
   ${seo?`<label>Títulos por red (SEO)</label>${REDES.filter(r=>seo[r]).map(r=>`<div class="fila">${redPill(r)}<span class="t"><span class="ofi-txt"><b class="ofi-de">${esc(seo[r].titulo||v.titulo)}</b> ${esc(seo[r].texto||"")}</span>${(seo[r].tags||[]).length?`<small>${seo[r].tags.map(t=>"#"+esc(t)).join(" ")}</small>`:""}</span></div>`).join("")}`:""}
  </details>`;
}

// ── Mejora diaria ──
function ofiMejora(){
  const M=OFD.mejora||{},hall=M.hallazgos||[],recs=M.recomendaciones||{},evx=M.experimentos||{},ref=M.referencia||{},met=M.metricas||{};
  const exps=[...(OFI.experimentos||[])].reverse(),diario=[...(OFI.diario||[])].reverse();
  let h=`<div class="msg info">${ic("spark","s")}<div><b>Así se mejora sola la oficina, cada día.</b> El auditor mide la voz (ritmo, pausas, energía del gancho), la escena 3D (cámara, primeros planos, animaciones), los gráficos (contadores, etiquetas) y el sonido (efectos) de los ${M.medidos||0} vídeos, y lo cruza con las vistas frente a lo normal de su semana. Cada pasada, los puestos aplican lo que funciona, prueban un cambio nuevo y apuntan lo aprendido.</div></div>`;
  // diario
  h+=`<div class="card fade"><div class="h3">${ic("report")}Diario de mejora<span class="sub">Lo que la oficina aprende y cambia en cada pasada</span></div>${diario.length?diario.slice(0,7).map((d,k)=>`<details ${k===0?"open":""} class="ofi-diario"><summary><b>${fmtDiaC(d.fecha)}</b> · ${esc(d.resumen||"")}</summary>
    ${(d.aprendido||[]).length?`<label>Aprendido</label><ul class="ofi-lista">${d.aprendido.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`:""}
    ${(d.cambios||[]).length?`<label>Cambios aplicados</label>${d.cambios.map(c=>`<div class="fila">${avatarRol(c.rol,26)}<span class="t"><span class="ofi-txt">${esc(c.texto)}</span></span></div>`).join("")}`:""}</details>`).join(""):`<p class="mut peq">La primera entrada llegará con la próxima pasada (${fmtHora(proximaPasada())}).</p>`}</div>`;
  // hallazgos
  h+=`<div class="card fade"><div class="h3">${ic("eye")}Lo que tienen los vídeos que funcionan<span class="sub">Mitad por encima de la mediana frente a mitad por debajo · se recalcula con cada recogida</span></div>${hall.length?hall.map((x,i)=>{const r=rolDe(x.rol);const ya=OFI.manual.some(m=>m.filtro?.campo===x.metrica);return `<div class="ofi-hall">${avatarRol(x.rol,32)}<div style="flex:1;min-width:0"><span class="ofi-txt">${esc(x.texto)}</span><small class="mut">${esc(r.nombre)} · ${x.n_si}+${x.n_no} vídeos${x.sorpresa?` · <span class="pill warn">sorpresa</span>`:""}</small><div class="barra" style="margin-top:6px;max-width:360px"><i style="width:${Math.min(100,(x.ratio-1)/2*100)}%"></i></div></div><b class="num">${fmtX(x.ratio)}</b>${ya?`<span class="pill ok">en el Manual</span>`:`<button class="btn sec peq" onclick="hallazgoARegla(${i})">${ic("plus","s")}Probar como regla</button>`}</div>`}).join(""):vacio("eye","Aún no hay hallazgos","Hacen falta al menos 8 vídeos medidos con 48 h publicados.")}</div>`;
  // experimentos
  h+=`<div class="card fade"><div class="h3">${ic("dice")}Experimentos<span class="sub">Un cambio concreto que se prueba en los próximos vídeos y se juzga solo con los datos</span></div>${exps.length?exps.map(x=>{const e=evx[x.id]||{},est=x.estado==="activo"?(e.veredicto||"esperando"):x.estado;const cl={ganado:"ok",perdido:"err",neutro:"warn"}[est]||"";
    return `<div class="fila">${avatarRol(x.rol,30)}<span class="t"><span class="ofi-txt"><b class="ofi-de">${esc(x.cambio||"")}</b>${x.hipotesis?` · ${esc(x.hipotesis)}`:""}</span><small>${esc(rolDe(x.rol).nombre)} · desde ${x.desde?fmtDiaC(x.desde):"—"} · ${(x.videos||[]).length} vídeos${e.maduros?` · ${e.maduros} con datos, mediana ${fmtX(e.mediana)}`:""}${x.conclusion?` · ${esc(x.conclusion)}`:""}</small></span><span class="pill ${cl}">${{activo:"En marcha",esperando:"Esperando datos",ganado:"Funciona",perdido:"No funciona",neutro:"Sin efecto"}[est]||esc(est)}</span></div>`}).join(""):`<p class="mut peq">La próxima pasada abrirá el primero con el hallazgo más fuerte.</p>`}</div>`;
  // por vídeo
  const vivos=Object.keys(recs).map(id=>({v:PROD.find(x=>x.id===id),id,r:recs[id]})).filter(x=>x.v).sort((a,b)=>(["propuesto","aprobado","voz","rehacer","escena","revision"].indexOf(a.v.estado)+1||9)-(["propuesto","aprobado","voz","rehacer","escena","revision"].indexOf(b.v.estado)+1||9));
  h+=`<div class="card fade"><div class="h3">${ic("film")}Qué potenciar y qué corregir, vídeo a vídeo<span class="sub">Vídeos en marcha y publicados esta semana</span></div>${vivos.length?vivos.slice(0,14).map(({v,r})=>{const mal=r.filter(x=>x.tipo==="mejorar"),bien=r.filter(x=>x.tipo==="potenciar");
    return `<details class="ofi-diario"><summary><b>${esc(v.titulo)}</b> <span class="pill">${esc(FASES[v.estado]||v.estado)}</span> <span class="pill ${mal.length?"warn":"ok"}">${mal.length} por mejorar</span> <span class="pill ok">${bien.length} bien</span></summary>${[...mal,...bien].map(x=>`<div class="fila">${avatarRol(x.rol,26)}<span class="t"><span class="ofi-txt"><span class="pill ${x.tipo==="mejorar"?"warn":"ok"}">${x.tipo==="mejorar"?"Mejorar":"Potenciar"}</span> ${esc(x.texto)}</span></span></div>`).join("")}</details>`}).join(""):`<p class="mut peq">Sin vídeos que revisar ahora mismo.</p>`}</div>`;
  // referencia
  const filas=Object.entries(ref).filter(([k])=>met[k]);
  if(filas.length)h+=`<div class="card fade"><div class="h3">${ic("star")}Así son tus mejores vídeos<span class="sub">Mediana del mejor cuarto frente al resto</span></div><div class="tablewrap"><table><thead><tr><th>Medida</th><th>Puesto</th><th>Mejor cuarto</th><th>Resto</th></tr></thead><tbody>${filas.map(([k,v])=>`<tr><td>${esc(met[k].nombre)}</td><td>${avatarRol(met[k].rol,22)} ${esc(rolDe(met[k].rol).nombre)}</td><td><b>${String(v.top).replace(".",",")}</b> ${esc(met[k].unidad||"")}</td><td>${String(v.resto).replace(".",",")} ${esc(met[k].unidad||"")}</td></tr>`).join("")}</tbody></table></div></div>`;
  return h;
}
async function hallazgoARegla(i){const x=(OFD.mejora?.hallazgos||[])[i];if(!x)return;
  const filtro=x.umbral==null?{campo:x.metrica,igual:x.direccion==="mas"}:{campo:x.metrica,[x.direccion==="mas"?"mayor":"menor"]:x.umbral};
  await accion(()=>editarJson("produccion/oficina.json",d=>{(d.manual=d.manual||[]).push({id:"m"+Date.now().toString(36),texto:x.texto,estado:"hipotesis",por:x.rol,creada:hoyISO().slice(0,10),origen:`Auditoría técnica: ${fmtX(x.ratio)} con ${x.n_si}+${x.n_no} vídeos`,filtro})},"Panel: hallazgo técnico al Manual [skip ci]"),"En prueba en el Manual vivo.")}

// ── Canal: lo que se escriben los agentes ──
const TIPO_MSG={peticion:["Petición","acc"],propuesta:["Propuesta","info"],aviso:["Aviso","warn"],pregunta:["Pregunta",""],dato:["Dato",""]};
const DECISION={acepto:["Acepta","ok"],matizo:["Matiza","info"],rechazo:["Rechaza","err"],respondo:["Responde",""]};
let CANAL_FILTRO="todos";
function estadoJornada(){
  const j=OFI.jornadas[OFI.jornadas.length-1];
  const btn=`<button class="btn sec peq" onclick="accion(()=>lanzarFlujo('jornada.yml'),'Jornada en marcha: los nueve agentes tardan 3-6 minutos.',{recargar:false})">${ic("play","s")}Lanzar jornada ahora</button>`;
  if(!j)return `<div class="card fade"><div class="h3">${ic("users")}Jornada diaria<span class="sub">Cada día a las 07:17</span></div><p class="mut peq">Todavía no ha habido ninguna jornada.</p>${btn}</div>`;
  if(j.estado==="sin_clave")return `<div class="card fade"><div class="h3">${ic("alert")}La jornada necesita una clave<span class="sub">${hace(j.fecha)}</span></div>
    <div class="msg warn">${ic("info","s")}<div>Para que los nueve agentes trabajen solos cada día en GitHub, añade tu clave de la API de Claude como secreto <b>ANTHROPIC_API_KEY</b> en GitHub → el repositorio → <i>Settings → Secrets and variables → Actions → New repository secret</i>. Mientras tanto, la jornada la hace la pasada de la mañana con los agentes de Claude Code.</div></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn sec peq" href="https://github.com/${O}/${R}/settings/secrets/actions/new" target="_blank" rel="noopener">${ic("ext","s")}Abrir los secretos de GitHub</a>${btn}</div></div>`;
  const t=j.tokens||{};
  return `<div class="card fade"><div class="h3">${ic("users")}Última jornada · ${fmtDiaC(j.fecha)} a las ${fmtHora(j.fecha)}<span class="sub">${esc(j.modelo||"")}${j.llamadas?` · ${j.llamadas} llamadas`:""}${j.euros!=null?` · ${String(j.euros).replace(".",",")} €`:""}</span></div>
   <div class="grid g4" style="margin-bottom:10px">${[["Mensajes",j.mensajes],["Acuerdos nuevos",j.acuerdos],["Revisiones",j.revisiones],["Lecciones a las fichas",j.aprendizajes]].map(([a,b])=>`<div class="ofi-mini"><b>${b??0}</b><small>${a}</small></div>`).join("")}</div>
   ${(j.errores||[]).length?`<div class="msg warn">${ic("alert","s")}<div>${j.errores.map(esc).join("<br>")}</div></div>`:""}
   <details><summary class="peq">Lo que vio cada agente</summary>${Object.entries(j.resumenes||{}).filter(([,t])=>t).map(([r,t])=>`<div class="fila">${avatarRol(r,26)}<span class="t"><span class="ofi-txt"><b class="ofi-de">${esc(rolDe(r).nombre)}</b> ${esc(t)}</span></span></div>`).join("")}</details>
   <div style="margin-top:10px">${btn}</div></div>`;
}
function ofiCanal(){
  const vig=OFI.acuerdos.filter(a=>a.estado==="vigente").reverse();
  const msgs=OFI.canal.filter(m=>CANAL_FILTRO==="todos"||m.de===CANAL_FILTRO||m.para===CANAL_FILTRO||(m.respuestas||[]).some(r=>r.de===CANAL_FILTRO)).slice().reverse();
  const porDia={};for(const m of msgs)(porDia[m.jornada||m.fecha.slice(0,10)]=porDia[m.jornada||m.fecha.slice(0,10)]||[]).push(m);
  let h=estadoJornada();
  h+=`<div class="card fade"><div class="h3">${ic("check")}Acuerdos vigentes<span class="sub">Lo que un agente se ha comprometido a hacer porque otro se lo pidió. La producción los cumple como normas.</span></div>
   ${vig.length?vig.map(a=>`<div class="fila">${avatarRol(a.rol,30)}<span class="t"><span class="ofi-txt"><b class="ofi-de">${esc(rolDe(a.rol).nombre)}</b> ${esc(a.texto)}</span><small>pedido por ${esc(rolDe(a.pedido_por).nombre)} · desde ${fmtDiaC(a.desde)}</small></span><button class="btn fantasma peq" onclick="retirarAcuerdo('${esc(a.id)}')">${ic("x","s")}Retirar</button></div>`).join(""):`<p class="mut peq">Aún no hay acuerdos. Saldrán de la primera jornada.</p>`}</div>`;
  h+=`<div class="chips" style="margin-bottom:14px"><button class="chip ${CANAL_FILTRO==="todos"?"on":""}" onclick="CANAL_FILTRO='todos';ir('ofi','canal',true)">Todos</button>${OFI.equipo.map(e=>`<button class="chip ${CANAL_FILTRO===e.id?"on":""}" onclick="CANAL_FILTRO='${e.id}';ir('ofi','canal',true)"><i style="background:${e.color}"></i>${esc(e.nombre)}</button>`).join("")}</div>`;
  if(!msgs.length)return h+`<div class="card">${vacio("chat","El canal está vacío","Aquí aparecerá todo lo que los agentes se escriben en cada jornada, con sus respuestas.")}</div>`;
  for(const [dia,ms] of Object.entries(porDia).slice(0,10)){
    h+=`<div class="card fade"><div class="h3">${ic("chat")}Jornada del ${fmtDiaC(dia)}<span class="sub">${ms.length} mensajes · ${ms.reduce((s,m)=>s+(m.respuestas||[]).length,0)} respuestas</span></div>${ms.map(mensajeCanal).join("")}</div>`;
  }
  return h;
}
function mensajeCanal(m){
  const t=TIPO_MSG[m.tipo]||[m.tipo,""],v=m.video?PROD.find(x=>x.id===m.video):null;
  return `<div class="ofi-msg"><div class="ofi-msg-cab">${avatarRol(m.de,30)}<b>${esc(rolDe(m.de).nombre)}</b>${ic("right","s")}${m.para==="todos"?`<b>Todo el equipo</b>`:`${avatarRol(m.para,22)}<b>${esc(rolDe(m.para).nombre)}</b>`}<span class="pill ${t[1]}">${t[0]}</span>${v?`<span class="pill">${esc(v.titulo.slice(0,40))}</span>`:""}<small class="mut">${fmtHora(m.fecha)}</small></div>
   <div class="ofi-msg-cuerpo"><b>${esc(m.asunto||"")}</b><p>${esc(m.texto)}</p></div>
   ${(m.respuestas||[]).map(r=>{const d=DECISION[r.decision]||[r.decision,""];return `<div class="ofi-resp">${avatarRol(r.de,24)}<div><div><b>${esc(rolDe(r.de).nombre)}</b> <span class="pill ${d[1]}">${d[0]}</span></div><p>${esc(r.texto)}</p>${r.compromiso?`<div class="ofi-comp">${ic("check","s")}<span><b>Se compromete:</b> ${esc(r.compromiso)}</span></div>`:""}</div></div>`}).join("")}</div>`;
}
async function retirarAcuerdo(id){if(!await confirmar("¿Retirar este acuerdo?","La producción dejará de aplicarlo.",{si:"Retirar",peligro:true}))return;
  await accion(()=>editarJson("produccion/oficina.json",d=>{const a=(d.acuerdos||[]).find(x=>x.id===id);if(a){a.estado="retirado";a.retirado_por=usuario}},"Panel: acuerdo retirado [skip ci]"),"Retirado")}
