'use strict';

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { jobs: [], selectedId: null, service: null, creating: false, loading: false, failures: 0 };
  const success = new Set(['completed', 'complete', 'done', 'ready']);
  const stageNames = { research: 'Nghiên cứu nguồn', source: 'Phân tích video nguồn', script: 'Viết lại câu chuyện', content: 'Viết lại câu chuyện', visuals: 'Hình minh họa & animation', visual: 'Hình minh họa & animation', voice: 'Giọng đọc tiếng Anh', sound: 'Nhạc nền & hiệu ứng', audio: 'Nhạc nền & hiệu ứng', qa: 'Kiểm tra hình và tiếng', review: 'Kiểm tra hình và tiếng', export: 'Xuất video', render: 'Dựng & xuất video', agents: 'Điều phối agent' };
  const statusNames = { queued: 'Đang chờ', pending: 'Chưa bắt đầu', running: 'Đang thực hiện', processing: 'Đang thực hiện', completed: 'Hoàn tất', complete: 'Hoàn tất', done: 'Hoàn tất', ready: 'Sẵn sàng', failed: 'Cần xử lý', blocked: 'Đang bị chặn', cancelled: 'Đã dừng', canceled: 'Đã dừng', interrupted: 'Bị gián đoạn' };
  const defaultStages = ['research', 'script', 'visuals', 'voice', 'sound', 'qa', 'export'];
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const safeClass = (v) => String(v || 'pending').toLowerCase().replace(/[^a-z_-]/g, '');
  const label = (v) => statusNames[v] || String(v || 'Chưa bắt đầu');
  const date = (v) => { if (!v) return ''; const d = new Date(v); return Number.isNaN(d.getTime()) ? '' : new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(d); };
  const title = (job) => job.title || 'Video mới · đang đọc nguồn';
  const safeURL = (value) => { if (typeof value !== 'string' || !value.trim()) return null; try { const url = new URL(value, location.origin); return ['http:', 'https:'].includes(url.protocol) ? url.href : null; } catch { return null; } };
  const errorText = (error) => typeof error === 'string' ? error : error?.message || (error ? JSON.stringify(error) : '');
  function notice(message) { $('connection-notice').textContent = message; $('connection-notice').classList.toggle('hidden', !message); }
  function formError(message) { $('form-error').textContent = message; $('form-error').classList.toggle('hidden', !message); }
  async function api(path, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 25000);
    try {
      const response = await fetch(path, { ...options, signal: controller.signal, headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers } });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = data?.detail || data?.error;
        throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(x => x.msg || '').join('; ') : `Yêu cầu chưa thành công (${response.status}).`);
      }
      if (data === null) throw new Error('Máy chủ chưa trả về dữ liệu hợp lệ.');
      return data;
    } catch (e) { if (e.name === 'AbortError') throw new Error('Máy chủ phản hồi chậm. Bạn có thể thử làm mới.'); throw e; }
    finally { clearTimeout(timer); }
  }
  function updateService(service) {
    state.service = service;
    const ready = service.ready === true;
    $('connection-toggle').className = `connection ${ready ? '' : 'wait'}`;
    $('connection-label').textContent = ready ? 'Studio sẵn sàng' : 'Cần chuẩn bị công cụ';
    $('create-button').disabled = state.creating || !ready;
    const names = { ffmpeg: 'Dựng video', yt_dlp: 'Đọc video nguồn', edge_tts: 'Giọng đọc', codex: 'AI agent' };
    $('capabilities').innerHTML = Object.entries(names).map(([key, name]) => {
      const value = service.capabilities?.[key];
      const available = typeof value === 'object' ? value?.available === true || value?.ready === true : Boolean(value);
      return `<div class="cap-row ${available ? '' : 'missing'}"><span>${name}</span><span>${available ? 'Sẵn sàng' : 'Chưa sẵn sàng'}</span></div>`;
    }).join('');
    if (!ready) notice(service.message || 'Một số công cụ chưa sẵn sàng. Mở trạng thái ở góc phải để xem chi tiết; các dự án đã có vẫn được giữ lại.');
    else notice('');
  }
  function renderList() {
    $('job-count').textContent = String(state.jobs.length);
    $('list-count').textContent = `${state.jobs.length} dự án`;
    if (!state.jobs.length) { $('jobs-list').innerHTML = '<p class="list-message">Chưa có dự án nào.<br>Dán link để bắt đầu bản đầu tiên.</p>'; return; }
    $('jobs-list').innerHTML = state.jobs.map(job => `<button type="button" class="job-item ${job.id === state.selectedId ? 'selected' : ''}" data-job-id="${esc(job.id)}" aria-pressed="${job.id === state.selectedId}"><span class="job-item-title">${esc(title(job))}</span><span class="job-item-meta"><span class="job-item-status ${safeClass(job.status)}">${esc(label(job.status))}</span><span>${esc(date(job.created_at))}</span></span></button>`).join('');
  }
  function progress(job) {
    const n = Number(job.progress);
    if (!Number.isFinite(n)) return null;
    return Math.max(0, Math.min(100, Math.round(n > 0 && n < 1 ? n * 100 : n)));
  }
  function renderDetail(job) {
    $('detail-empty').classList.toggle('hidden', Boolean(job));
    $('detail-content').classList.toggle('hidden', !job);
    if (!job) return;
    $('detail-id').textContent = `DỰ ÁN ${job.id}`;
    $('detail-title').textContent = title(job);
    $('detail-status').textContent = label(job.status);
    $('detail-status').className = `status-pill ${safeClass(job.status)}`;
    const source = safeURL(job.url);
    $('detail-source').classList.toggle('hidden', !source);
    if (source) $('detail-source').href = source;
    const pct = progress(job);
    $('progress-label').textContent = stageNames[job.stage] || job.stage || label(job.status);
    $('progress-number').textContent = pct === null ? 'Chưa có dữ liệu tiến độ' : `${pct}%`;
    $('progress-fill').style.width = `${pct ?? 0}%`;
    if (pct === null) $('progress-bar').removeAttribute('aria-valuenow'); else $('progress-bar').setAttribute('aria-valuenow', String(pct));
    $('job-error').textContent = errorText(job.error);
    $('job-error').classList.toggle('hidden', !job.error);
    const stages = Array.isArray(job.stages) && job.stages.length ? job.stages : defaultStages.map(id => ({ id, status: 'pending', label: stageNames[id] }));
    $('agent-list').innerHTML = stages.map((step, i) => {
      const status = safeClass(step.status), completed = success.has(status);
      const marker = completed ? '✓' : ['running', 'processing'].includes(status) ? '●' : ['failed', 'blocked'].includes(status) ? '!' : String(i + 1).padStart(2, '0');
      return `<li class="agent-row ${status}"><span class="agent-indicator" aria-hidden="true">${marker}</span><div><div class="agent-name">${esc(step.label || stageNames[step.id] || step.id)}</div>${step.detail ? `<div class="agent-detail">${esc(errorText(step.detail))}</div>` : ''}</div><span class="agent-status">${esc(label(step.status))}</span></li>`;
    }).join('');
    const video = safeURL(job.video_url), audio = safeURL(job.audio_url), preview = safeURL(job.preview_url);
    $('result-area').classList.toggle('hidden', !(video || audio || preview));
    $('result-caption').textContent = success.has(job.status) ? 'Đầu ra của dự án' : 'Đầu ra đã có · quy trình chưa hoàn tất';
    updateMedia($('video-preview'), video);
    updateMedia($('audio-preview'), audio);
    const links = [];
    if (video) links.push(`<a class="result-link" href="${esc(video)}" download>Tải video ↓</a>`);
    if (audio) links.push(`<a class="result-link" href="${esc(audio)}" download>Tải audio ↓</a>`);
    const credits = safeURL(job.credits_url);
    if (credits) links.push(`<a class="result-link" href="${esc(credits)}" download>Nguồn tư liệu / credit ↓</a>`);
    const thumbnail = safeURL(job.thumbnail_url), title = safeURL(job.title_url);
    if (thumbnail) links.push(`<a class="result-link" href="${esc(thumbnail)}" download>Tải thumbnail ↓</a>`);
    if (title) links.push(`<a class="result-link" href="${esc(title)}" download>Tải tiêu đề ↓</a>`);
    if (preview && preview !== video) links.push(`<a class="result-link" href="${esc(preview)}" target="_blank" rel="noopener">Mở bản dựng ↗</a>`);
    $('result-links').innerHTML = links.join('');
    $('detail-date').textContent = job.created_at ? `Tạo lúc ${date(job.created_at)}` : '';
    $('retry-button').classList.toggle('hidden', !['failed', 'blocked', 'interrupted'].includes(job.status));
  }
  function updateMedia(element, url) {
    element.classList.toggle('hidden', !url);
    if (url && element.getAttribute('src') !== url) { element.src = url; element.load(); }
    if (!url && element.hasAttribute('src')) { element.pause(); element.removeAttribute('src'); element.load(); }
  }
  async function selectJob(id) {
    state.selectedId = id;
    renderList();
    renderDetail(state.jobs.find(j => j.id === id));
    try { const job = await api(`/api/jobs/${encodeURIComponent(id)}`); if (state.selectedId === id) renderDetail(job.job || job); }
    catch (e) { if (state.selectedId === id) notice(`Không tải được chi tiết mới nhất: ${e.message}`); }
  }
  async function refresh({ checkStatus = false } = {}) {
    if (state.loading) return;
    state.loading = true;
    $('refresh-button').disabled = true;
    try {
      const [jobsData, service] = await Promise.all([api('/api/jobs'), checkStatus || !state.service ? api('/api/status') : Promise.resolve(null)]);
      state.jobs = Array.isArray(jobsData) ? jobsData : jobsData.jobs || [];
      if (service) updateService(service); else if (state.failures && state.service?.ready) { notice(''); $('connection-label').textContent = 'Studio sẵn sàng'; $('connection-toggle').className = 'connection'; }
      state.failures = 0;
      if (!state.selectedId || !state.jobs.some(j => j.id === state.selectedId)) state.selectedId = state.jobs[0]?.id || null;
      renderList();
      if (state.selectedId) {
        const selected = state.jobs.find(j => j.id === state.selectedId);
        renderDetail(selected);
        const data = await api(`/api/jobs/${encodeURIComponent(state.selectedId)}`);
        if ((data.job || data).id === state.selectedId) renderDetail(data.job || data);
      } else renderDetail(null);
    } catch (e) {
      state.failures += 1;
      $('connection-toggle').className = 'connection error';
      $('connection-label').textContent = 'Mất kết nối local';
      notice(`Chưa kết nối được máy chủ: ${e.message} Dữ liệu đang hiển thị có thể chưa cập nhật.`);
      if (!state.service) { $('create-button').disabled = true; $('jobs-list').innerHTML = '<p class="list-message">Chưa tải được danh sách dự án.<br>Kiểm tra máy chủ local rồi bấm Làm mới.</p>'; }
    } finally { state.loading = false; $('refresh-button').disabled = false; }
  }
  function validYouTube(value) {
    try { const u = new URL(value); return ['http:', 'https:'].includes(u.protocol) && (u.hostname === 'youtu.be' || u.hostname === 'youtube.com' || u.hostname.endsWith('.youtube.com')); } catch { return false; }
  }
  $('remake-form').addEventListener('submit', async event => {
    event.preventDefault(); formError('');
    const url = $('source-url').value.trim();
    if (!validYouTube(url)) { formError('Hãy nhập một đường dẫn video YouTube hợp lệ.'); $('source-url').focus(); return; }
    if (state.creating) return;
    state.creating = true; $('create-button').disabled = true; $('create-button').firstElementChild.textContent = 'Đang tạo dự án…';
    try {
      const data = await api('/api/jobs', { method: 'POST', body: JSON.stringify({ url, language: 'en', notes: $('notes').value.trim() }) });
      const job = data.job || data;
      state.selectedId = job.id;
      if (job.id) state.jobs = [job, ...state.jobs.filter(x => x.id !== job.id)];
      renderList(); renderDetail(job.id ? job : null);
      $('projects').scrollIntoView({ behavior: 'smooth', block: 'start' });
      await refresh();
    } catch (e) { formError(e.message || 'Chưa tạo được dự án.'); }
    finally { state.creating = false; $('create-button').disabled = !state.service?.ready; $('create-button').firstElementChild.textContent = 'Tạo bản remake'; }
  });
  $('jobs-list').addEventListener('click', event => { const button = event.target.closest('[data-job-id]'); if (button) selectJob(button.dataset.jobId); });
  $('refresh-button').addEventListener('click', () => refresh({ checkStatus: true }));
  $('use-reference').addEventListener('click', () => { $('source-url').value = 'https://www.youtube.com/watch?v=0NY2gAftzJE'; $('source-url').focus(); formError(''); });
  $('connection-toggle').addEventListener('click', () => { const open = $('capability-panel').classList.toggle('hidden') === false; $('connection-toggle').setAttribute('aria-expanded', String(open)); });
  $('retry-button').addEventListener('click', async () => {
    if (!state.selectedId) return;
    $('retry-button').disabled = true;
    try { const data = await api(`/api/jobs/${encodeURIComponent(state.selectedId)}/retry`, { method: 'POST' }); renderDetail(data.job || data); await refresh(); }
    catch (e) { $('job-error').textContent = e.message; $('job-error').classList.remove('hidden'); }
    finally { $('retry-button').disabled = false; }
  });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh({ checkStatus: true }); });
  refresh({ checkStatus: true });
  setInterval(() => { if (!document.hidden && !state.creating) refresh({ checkStatus: state.failures > 0 }); }, 3000);
})();
