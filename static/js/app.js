const qs = (s, p=document)=>p.querySelector(s);
const qsa = (s, p=document)=>[...p.querySelectorAll(s)];
function toast(msg){ const t=qs('#toast'); t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'), 1800); }
async function api(path, opts={}){
  const o = {headers: {'Content-Type':'application/json','X-CSRFToken': window.CSRF_TOKEN}, credentials:'same-origin', ...opts};
  const r = await fetch(`${window.API}${path}`, o);
  if(!r.ok) throw new Error(await r.text());
  return r.status===204? null : r.json();
}

function taskItem(t){
  const overdue = t.due_at && !t.is_done && new Date(t.due_at) < new Date();
  return `<li class="task" data-id="${t.id}">
    <input type="checkbox" ${t.is_done?'checked':''} class="mark">
    <div>
      <div class="t-title">${t.title}</div>
      <div class="t-desc">${t.description||''}</div>
      <div class="row gap">
        <span class="badge">#${t.id}</span>
        ${t.assignee ? `<span class="badge">@${t.assignee_username}</span>` : ''}
        ${t.due_at ? `<span class="badge ${overdue?'warn':'ok'}">${new Date(t.due_at).toLocaleString()}</span>`:''}
        <span class="badge">${t.list_name}</span>
      </div>
    </div>
    <div class="row gap">
      <button class="btn edit">Редакт.</button>
      <button class="btn danger del">Удалить</button>
    </div>
  </li>`;
}

async function loadTasks(){
    const listId = qs('#listFilter').value;
    const only = qs('#onlyMine').value;
    const q = qs('#search').value.trim();
  
    const params = new URLSearchParams();
    if (listId) params.set('list', listId);
    if (only && only !== 'all') params.set('filter', only);
    if (q) params.set('q', q);
  
    const data = await api(`/tasks/?${params.toString()}`);
    const items = Array.isArray(data) ? data : (data.results || []);
  
    qs('#tasks').innerHTML = items.map(taskItem).join('');
  }

function openModal(t){
  const dlg = qs('#taskModal');
  qs('#modalTitle').textContent = t?.id ? `Редактирование #${t.id}` : 'Новая задача';
  qs('#taskId').value = t?.id || '';
  qs('#title').value = t?.title || '';
  qs('#description').value = t?.description || '';
  qs('#list').value = t?.list || qs('#list').options[0].value;
  qs('#assignee').value = t?.assignee || '';
  qs('#due_at').value = t?.due_at ? t.due_at.slice(0,16) : '';
  dlg.showModal();
}
function closeModal(){ qs('#taskModal').close(); }

async function submitForm(e){
  e.preventDefault();
  const id = qs('#taskId').value;
  const payload = {
    title: qs('#title').value.trim(),
    description: qs('#description').value.trim(),
    list: Number(qs('#list').value),
    assignee: qs('#assignee').value ? Number(qs('#assignee').value) : null,
    due_at: qs('#due_at').value ? new Date(qs('#due_at').value).toISOString() : null,
  };
  if(id){
    await api(`/tasks/${id}/`, { method:'PATCH', body: JSON.stringify(payload) });
    toast('Задача обновлена');
  }else{
    await api(`/tasks/`, { method:'POST', body: JSON.stringify(payload) });
    toast('Задача создана');
  }
  closeModal();
  await loadTasks();
}

document.addEventListener('click', async (e)=>{
  const li = e.target.closest('.task');
  if(e.target.id === 'btn-new') return openModal();
  if(e.target.classList.contains('edit')){
    const id = li.dataset.id;
    const t = await api(`/tasks/${id}/`);
    return openModal(t);
  }
  if(e.target.classList.contains('del')){
    const id = li.dataset.id;
    await api(`/tasks/${id}/`, { method:'DELETE' });
    toast(`Удалена #${id}`);
    await loadTasks();
  }
  if(e.target.classList.contains('mark')){
    const id = li.dataset.id;
    await api(`/tasks/${id}/`, { method:'PATCH', body: JSON.stringify({is_done: e.target.checked}) });
    await loadTasks();
  }
});

qs('#taskForm').addEventListener('submit', submitForm);

['change','keyup'].forEach(ev => qs('#listFilter').addEventListener(ev, loadTasks));
['change','keyup'].forEach(ev => qs('#onlyMine').addEventListener(ev, loadTasks));
['change','keyup'].forEach(ev => qs('#search').addEventListener(ev, loadTasks));

window.addEventListener('DOMContentLoaded', loadTasks);