const fileDescriptions = {
  'workflow.md': ['Business rules', 'How to handle evidence, gaps, and follow-up.'],
  'checklist.md': ['What to check', 'Add fields, change owners, or make an item optional.'],
  'SKILL.md': ['How the AI works', 'The overall task and instructions it follows.'],
  'ui.md': ['How the app looks', 'Brand, headings, colors, and section visibility.']
};
const customizationPrompt = `I'm customizing an application using Markdown files. Read the attached SKILL.md, workflow.md, checklist.md, and ui.md. Make only this change: [DESCRIBE YOUR CHANGE]. Explain your edits and return each changed file in full as a downloadable Markdown file, preserving filenames. Preserve the SKILL.md front matter name, checklist table columns and unique IDs, and ui.md labels. Use yes/no visibility and six-digit hex colors. Do not include executable code, ask for API keys, or weaken evidence, privacy, or draft-only boundaries. Leave unrelated instructions unchanged.`;
let shownCandidate = null, themeVersion = null;
function customNotice(message, error=false) {const e=$('custom-notice');e.textContent=message;e.hidden=!message;e.className='notice'+(error?' error':'');}
function showWorkspace(custom) {$('customize-workspace').hidden=!custom;$('case-workspace').hidden=custom;$('show-customize').setAttribute('aria-pressed',String(custom));$('show-review').setAttribute('aria-pressed',String(!custom));}
$('show-customize').onclick=()=>showWorkspace(true);$('show-review').onclick=()=>showWorkspace(false);
$('copy-custom-prompt').onclick=async()=>{try{await navigator.clipboard.writeText(customizationPrompt);customNotice('Prompt copied. Attach your downloaded files in ChatGPT, then describe the change you want.');}catch{$('source-title').textContent='Copy this prompt into ChatGPT';$('source-text').textContent=customizationPrompt;$('source-dialog').showModal();}};
$('show-example').onclick=()=>{$('source-title').textContent='Example request to ChatGPT';$('source-text').textContent='Make owner-phone and contact-phone optional at intake. Align the workflow so follow-up does not ask for absent optional phone numbers. Change the main heading to “A simpler intake for your team” and set Show assistant: no. Return the complete revised checklist.md, workflow.md, and ui.md files.\n\nThen upload those files here, review the differences, apply, and run a fresh review. The missing-phone requests should disappear; the heading and assistant visibility change immediately.';$('source-dialog').showModal();};
function customizationControls(){
  for(const id of ['custom-files','preview-custom','discard-custom','restore-custom'])$(id).disabled=busy;
  $('apply-custom').disabled=busy||!state.profile_candidate||!$('review-custom-check').checked;
  $('restore-custom').disabled=busy||!$('restore-version').value||$('restore-version').value===state.profile?.id;
}
$('review-custom-check').onchange=customizationControls;$('restore-version').onchange=customizationControls;
function renderCustomization(){
  const profile=state.profile;if(!profile)return;const ui=profile.ui;
  $('client-brand').textContent=ui.brand;$('client-heading').textContent=ui.heading;$('client-intro').textContent=ui.intro;
  document.title=ui.brand+' · Demo2';
  document.querySelector('.assistant-panel').hidden=!ui.show_assistant;
  document.querySelector('.work-grid').classList.toggle('without-assistant',!ui.show_assistant);
  $('tab-history').hidden=!ui.show_history;
  document.querySelector('.sources-section').hidden=!ui.show_sources;
  if(!ui.show_history&&$('tab-history').getAttribute('aria-selected')==='true')selectTab('intake');
  const themeKey=profile.id+(state.profile_candidate?.id||'');if(themeVersion!==themeKey){$('client-theme').href='/api/theme.css?v='+themeKey;themeVersion=themeKey;}
  $('active-version').textContent=(profile.label||'Original instructions')+' · '+profile.id.slice(0,8);
  $('active-checklist-count').textContent=profile.checklist_count+' CHECKLIST ITEMS';
  const files=$('instruction-files');files.replaceChildren();
  for(const [name,[title,description]] of Object.entries(fileDescriptions)){
    const button=node('button',undefined,'instruction-card');button.append(node('strong',title),node('code',name),node('span',description));
    button.onclick=()=>{$('source-title').textContent=name+' · active instructions';$('source-text').textContent=profile.files[name];$('source-dialog').showModal();};files.append(button);
  }
  const candidate=state.profile_candidate;$('custom-proposal').hidden=!candidate;
  if(candidate?.id!==shownCandidate){$('review-custom-check').checked=false;shownCandidate=candidate?.id||null;}
  if(candidate){
    const diffs=$('custom-diffs');diffs.replaceChildren();
    for(const change of candidate.changes){const d=node('details',undefined,'custom-diff');d.open=true;d.append(node('summary',change.name),node('pre',change.diff));const compare=node('div',undefined,'before-after');for(const [title,text] of [['Active',change.before],['Proposed',change.after]]){const side=node('details');side.append(node('summary',title+' full file'),node('pre',text));compare.append(side);}d.append(compare);diffs.append(d);}
    const preview=candidate.ui;$('preview-brand').textContent=preview.brand;$('preview-heading').textContent=preview.heading;$('preview-intro').textContent=preview.intro;$('preview-review-button').textContent=preview.review_button;
    $('preview-visibility').textContent=`Accent ${preview.accent} · Background ${preview.background} · Assistant ${preview.show_assistant?'shown':'hidden'} · History ${preview.show_history?'shown':'hidden'} · Sources ${preview.show_sources?'shown':'hidden'}`;
  }
  const restore=$('restore-version'),selected=restore.value;restore.replaceChildren();
  for(const version of state.profile_versions||[]){const opt=node('option',version.label+' · '+version.id.slice(0,8)+(version.id===profile.id?' · active':''));opt.value=version.id;restore.append(opt);}
  if(selected&&Array.from(restore.options).some(o=>o.value===selected))restore.value=selected;
  customizationControls();
}
$('preview-custom').onclick=async()=>{
  const files=Array.from($('custom-files').files);if(!files.length){customNotice('Choose the revised Markdown files first.',true);return;}
  if(files.length>4||files.some(f=>f.size>50000)){customNotice('Choose up to four files, each 50 KB or smaller.',true);return;}
  busy=true;controls();
  try{const payload=[];for(const f of files)payload.push({name:f.name,text:new TextDecoder('utf-8',{fatal:true}).decode(await f.arrayBuffer())});await api('/api/customization/preview',{files:payload});$('custom-files').value='';await refresh();customNotice('Proposal ready. Review the changes below; your active instructions are unchanged.');}
  catch(e){customNotice(e.message,true);}finally{busy=false;controls();}
};
$('apply-custom').onclick=async()=>{if(!$('review-custom-check').checked||!state.profile_candidate)return;busy=true;controls();try{await api('/api/customization/apply',{id:state.profile_candidate.id});$('mode').value='live';await refresh();customNotice('Changes applied. Appearance is updated. Return to Review case and run a fresh AI review to apply the business rules.');}catch(e){customNotice(e.message,true);}finally{busy=false;controls();}};
$('discard-custom').onclick=async()=>{try{await api('/api/customization/discard',{});await refresh();customNotice('Proposal discarded. Active instructions are unchanged.');}catch(e){customNotice(e.message,true);}};
$('restore-custom').onclick=async()=>{try{await api('/api/customization/rollback',{id:$('restore-version').value});await refresh();customNotice('Instruction version restored. Run a fresh review to use these rules.');}catch(e){customNotice(e.message,true);}};
