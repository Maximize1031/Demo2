const $ = (id) => document.getElementById(id);
let config = {}, state = {current: null, revisions: [], messages: [], sources: []};
let busy = false, pollTimer, lastError = "", fetching = false, rendered = false;
const labels = {found: "On file", missing: "Missing", review: "Needs confirmation", conflict: "Conflict", optional: "Optional", not_applicable: "Not applicable"};
const titles = {"01-client-brief.md":"Client brief","02-sale-agreement.md":"Sale agreement","03-email-thread.md":"Escrow correspondence","04-preliminary-title.md":"Preliminary title","05-call-notes.md":"Call notes","06-escrow-confirmation.md":"Escrow confirmation","07-operating-agreement.md":"Operating agreement"};
function node(tag, text, className) {const e = document.createElement(tag); if (text !== undefined) e.textContent = text; if (className) e.className = className; return e;}
async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {method: "POST", headers: {"Content-Type":"application/json","X-Intake-Request":"1"},body:JSON.stringify(body)});
  if (!res.ok) {let message = "The request could not finish."; try {const data=await res.json(); message=typeof data.detail==="string"?data.detail:message;} catch {}
    const error = new Error(message); error.status = res.status; throw error;}
  return res.json();
}
function notice(text, error=false, spinning=false) {$("notice").textContent=text;$("notice").hidden=!text;$("notice").className="notice"+(error?" error":"")+(spinning?" busy":"");}
function selectTab(name) {
  document.querySelectorAll("[data-tab]").forEach(b=>{const active=b.dataset.tab===name;b.setAttribute("aria-selected",String(active));b.tabIndex=active?0:-1;$("pane-"+b.dataset.tab).hidden=!active;});
}
document.querySelectorAll("[data-tab]").forEach((button,index,buttons)=>{
  button.onclick=()=>selectTab(button.dataset.tab);
  button.onkeydown=e=>{if(["ArrowRight","ArrowLeft","Home","End"].includes(e.key)){e.preventDefault();const i=e.key==="Home"?0:e.key==="End"?buttons.length-1:(index+(e.key==="ArrowRight"?1:-1)+buttons.length)%buttons.length;buttons[i].focus();selectTab(buttons[i].dataset.tab);}};
});
function finding(row) {
  const card=node("article",undefined,"finding"), top=node("div",undefined,"finding-top");
  top.append(node("h4",row.item),node("span",labels[row.state],"pill "+row.state));
  card.append(top,node("p",row.value));
  const details=node("details");details.append(node("summary","View supporting evidence"),node("p",row.evidence));card.append(details);return card;
}
function renderReview() {
  const current=state.current;
  const caseInfo=state.case||{id:"DEMO-RIVERA-001",name:"Rivera Orchard LLC"};
  $("case-name").textContent=caseInfo.name;$("nav-case").textContent=caseInfo.name;$("case-id").textContent=caseInfo.id;
  $("sample-meta").hidden=!!state.custom;
  $("case-property").textContent=current?.property|| (state.custom?"Upload records to begin":"1250 Orchard Avenue · Pasadena, CA 91103");
  $("data-status").textContent=state.stale?"Evidence or instructions have changed. Run a fresh review to apply them. The results below are from the previous review.":current?`${current.mode==="live"?"AI analyzed":"Saved example covers"} ${current.source_snapshot?.length||state.sources.length} documents · ${new Date(current.created_at*1000).toLocaleString()}`:`${state.sources.length} document${state.sources.length===1?"":"s"} ready · Not yet analyzed`;
  $("data-status").className=state.stale?"error":"";
  $("empty").hidden=!!current;$("intake-content").hidden=!current;
  $("download").hidden=!current;
  for (const [id,key] of [["found-count","found"],["external-count","external"],["internal-count","internal"]]) $(id).textContent=current?current.counts[key]:"—";
  $("source-count").textContent=state.sources.length;
  $("gap-count").textContent=current?current.counts.external+current.counts.internal:"";
  $("revision-label").textContent=current?`${current.phase==="updated"?"Updated":"Initial"} review · ${current.mode==="live"?"Live AI":"Saved rehearsal"} · ${state.revisions.length} revision${state.revisions.length===1?"":"s"}`:"Ready for an initial review";
  const intake=$("intake-content");intake.replaceChildren();
  const evidence=$("evidence-rows");evidence.replaceChildren();
  if(current) {
    const heading=node("div",undefined,"pane-heading"), inner=node("div");
    inner.append(node("h3","What needs attention"),node("p","Ask the right person, and only for what’s still missing."));heading.append(inner);intake.append(heading);
    for(const [owner,title] of [["escrow","Escrow"],["client","Client"],["internal","Your team"]]) {
      const rows=current.rows.filter(r=>r.owner===owner&&["missing","review","conflict"].includes(r.state));
      if(!rows.length)continue;
      const h=node("div",title,"group-heading");h.append(node("span",`${rows.length} checklist item${rows.length===1?"":"s"}`));intake.append(h);
      rows.forEach(r=>intake.append(finding(r)));
    }
    if(!current.counts.external)intake.append(node("p","No external follow-up needed. Complete your internal review before handoff.","muted"));
    const optional=current.rows.filter(r=>["optional","not_applicable"].includes(r.state));
    const details=node("details",undefined,"finding");details.append(node("summary",`${optional.length} optional or not-applicable items · nonblocking`));optional.forEach(r=>details.append(finding(r)));intake.append(details);
    current.rows.forEach(row=>{const d=node("details",undefined,"evidence-item"),s=node("summary");s.append(node("span",row.item),node("span",labels[row.state],"pill "+row.state));d.append(s,node("p",row.value),node("p",row.evidence));evidence.append(d);});
  } else evidence.append(node("p","Run an intake review to see the checklist findings.","muted"));
  const drafts=$("draft-content");drafts.replaceChildren();
  if(current)for(const [key,label] of [["client_email","Client follow-up"],["escrow_email","Escrow follow-up"]]){
    const d=node("article",undefined,"draft"),h=node("div",undefined,"draft-heading"),copy=node("button","Copy draft");
    copy.onclick=async()=>{try{await navigator.clipboard.writeText(current[key]);copy.textContent="Copied";setTimeout(()=>copy.textContent="Copy draft",1600);}catch{notice("Copy is unavailable in this browser. Select the draft text or download the review.",true);}};
    h.append(node("h4",label),copy);d.append(h,node("p","DRAFT · NOT SENT","eyebrow"),node("pre",current[key]));drafts.append(d);
  } else drafts.append(node("p","Your client and escrow drafts will appear after the review.","muted"));
  const history=$("history-content");history.replaceChildren();
  if(!state.revisions.length)history.append(node("p","No reviews yet.","muted"));
  state.revisions.forEach((revision,i)=>{const d=node("details",undefined,"history-item");d.append(node("summary",`Revision ${i+1} · ${revision.mode==="live"?"Fresh AI review":revision.phase==="updated"?"New sample batch":"Initial sample review"}`),node("p",`${new Date(revision.created_at*1000).toLocaleString()} · ${revision.mode==="live"?"Live AI":"Saved rehearsal"} · ${revision.counts.external} external items open`),node("p",revision.changed_items?.length?"Changed findings: "+revision.changed_items.join(", "):i?"No checklist values or statuses changed.":"First assessment"),node("pre",revision.assessment));history.append(d);});
  const container=$("sources");container.replaceChildren();
  state.sources.forEach(source=>{const b=node("button",undefined,"source-card"),text=node("span");text.append(node("strong",titles[source.name]||source.name),node("small",source.origin==="upload"?"Uploaded · synthetic record":"Sample · synthetic record"));b.append(node("span","▤"),text);b.onclick=()=>{$("source-title").textContent=titles[source.name]||source.name;$("source-text").textContent=source.text;$("source-dialog").showModal();};container.append(b);});
  if(state.messages.length) {
    $("chat-messages").replaceChildren();
    state.messages.forEach(m=>{const d=node("div",undefined,"message "+m.role);d.append(node("small",m.role==="user"?"You":"Intake assistant"),node("span",m.content));$("chat-messages").append(d);});
  } else {const welcome=node("div",undefined,"assistant-welcome");welcome.append(node("p","Keep the whole case in view."),node("span",current?.mode==="rehearsal"?"You’re viewing saved rehearsal results. Evidence and drafts are ready to explore. Questions require a Live AI review.":"After a live review, ask about a finding, its supporting evidence, or the next follow-up."));$("chat-messages").replaceChildren(welcome);}
  rendered=true;controls();
  window.renderCustomization?.();
}
function controls() {
  $("run").disabled=busy||(!state.sources.length)||($("mode").value==="live"&&!config.live_available)||($("mode").value==="rehearsal"&&!!state.current);
  $("next").disabled=busy||!!state.custom||!state.current||state.current.phase!=="initial";
  $("next").hidden=!!state.custom;
  $("reset").disabled=busy;
  $("new-case").disabled=busy;
  $("upload-button").disabled=busy||state.current?.mode==="rehearsal";
  $("upload-files").disabled=busy||state.current?.mode==="rehearsal";
  $("mode").disabled=busy||!!state.current;
  $("logout").disabled=busy;
  $("mode").querySelector('[value="live"]').disabled=!config.live_available;
  const canChat=!busy&&!state.stale&&state.current?.mode==="live";
  $("question").disabled=!canChat;$("ask").disabled=!canChat;
  document.querySelectorAll("[data-question]").forEach(b=>b.disabled=!canChat);
  $("mode-note").textContent=$("mode").value==="rehearsal"
    ?"Rehearsal displays previously reviewed example results. No AI request is made."+(config.live_available?"":" Live AI will be available after API setup.")
    :config.live_available?"Live AI reads this batch, runs the intake skill and Python checks, and creates a fresh review.":"Live AI is not configured in this preview. You can customize the UI and instructions now; add the API key to run a fresh review.";
  window.customizationControls?.();
  $("run").textContent=busy&&state.job?.kind==="review"?"Review in progress…":(state.current?.mode==="live"?"Run fresh AI review ↗":(state.profile?.ui.review_button||"Run intake review")+" ↗");
}
async function refresh() {
  if(fetching)return;fetching=true;
  try {
    const next=await api("/api/state");const changed=JSON.stringify(state)!==JSON.stringify(next);state=next;
    busy=!!state.job&&["queued","running"].includes(state.job.status);
    if(state.current)$("mode").value=state.profile_versions?.length?"live":state.current.mode;
    if(changed||!rendered)renderReview();else controls();
    if(busy){notice(state.job.kind==="chat"?"Preparing an answer from this case…":"Reviewing the case and validating the results. You can keep this page open.",false,true);pollTimer=setTimeout(refresh,1600);}
    else if(state.job?.status==="failed"&&lastError!==state.job.id){lastError=state.job.id;notice(state.job.error,true);}
    else if($("notice").classList.contains("busy"))notice("Review complete. Your results are ready.");
  }catch(e){busy=false;controls();if(e.status===401){clearTimeout(pollTimer);$("workspace").hidden=true;$("login").hidden=false;}else{notice(e.message,true);pollTimer=setTimeout(refresh,5000);}}finally{fetching=false;}
}
async function run(phase) {
  busy=true;controls();notice("Starting the intake review…",false,true);
  try{await api("/api/review",{phase,mode:$("mode").value});selectTab("intake");await refresh();}
  catch(e){busy=false;controls();notice(e.message,true);}
}
$("run").onclick=()=>run("initial");$("next").onclick=()=>run("updated");$("mode").onchange=controls;
$("upload-button").onclick=async()=>{
  const files=Array.from($("upload-files").files);
  if(!files.length){notice("Choose Markdown or text files first.",true);return;}
  if(files.some(f=>f.size>100000)||files.length>30){notice("Choose up to 30 files, at most 100 KB each.",true);return;}
  busy=true;controls();
  try{const payload=[];for(const file of files){const text=new TextDecoder("utf-8",{fatal:true}).decode(await file.arrayBuffer());payload.push({name:file.name,text});}
    await api("/api/upload",{files:payload});$("upload-files").value="";$("mode").value="live";notice(`${files.length} file(s) uploaded. Run a fresh AI review to analyze them.`);await refresh();
  }catch(e){notice(e.message,true);}finally{busy=false;controls();}
};
$("new-case").onclick=()=>$("case-dialog").showModal();
$("cancel-case").onclick=()=>$("case-dialog").close();
$("case-form").onsubmit=async e=>{e.preventDefault();try{await api("/api/case",{name:$("new-case-name").value});$("case-dialog").close();$("mode").value="live";notice("Your empty case is ready. Upload synthetic records to begin.");await refresh();}catch(e){$("case-dialog").close();notice(e.message,true);}};
$("reset").onclick=async()=>{if(!confirm("Reset this demo session? Download the review first if you want to keep it."))return;try{await api("/api/reset",{});lastError=state.job?.id||"";notice("");selectTab("intake");await refresh();}catch(e){notice(e.message,true);}};
$("chat-form").onsubmit=async e=>{e.preventDefault();const message=$("question").value.trim();if(!message||busy)return;busy=true;controls();notice("Preparing an answer…",false,true);try{await api("/api/chat",{message});$("question").value="";await refresh();}catch(e){busy=false;controls();notice(e.message,true);}};
document.querySelectorAll("[data-question]").forEach(b=>b.onclick=()=>{$("question").value=b.dataset.question;$("chat-form").requestSubmit();});
$("close-source").onclick=()=>$("source-dialog").close();
$("logout").onclick=async()=>{try{await api("/api/logout",{});location.reload();}catch(e){notice(e.message,true);}};
$("login-form").onsubmit=async e=>{e.preventDefault();$("login-error").textContent="";try{await api("/api/login",{password:$("password").value});$("password").value="";$("login").hidden=true;$("workspace").hidden=false;await refresh();}catch(e){$("login-error").textContent=e.message;}};
async function boot() {
  try {config=await api("/api/config");$("mode").value=config.live_available?"live":"rehearsal";try{state=await api("/api/state");}catch(e){if(e.status!==401)throw e;if(config.password_required){$("login").hidden=false;return;}await api("/api/login",{});}
    $("workspace").hidden=false;await refresh();
  }catch(e){$("login").hidden=false;$("login-error").textContent=e.message;}
}
boot();
