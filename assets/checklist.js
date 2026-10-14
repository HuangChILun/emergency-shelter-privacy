(function () {
  'use strict';
  const VERSION = 1;
  function readState(storage, key, ids) {
    try {
      const data = JSON.parse(storage.getItem(key));
      if (!data || data.version !== VERSION || !Array.isArray(data.checked)) return [];
      return data.checked.filter(id => typeof id === 'string' && ids.includes(id));
    } catch (_) { return []; }
  }
  function saveState(storage, key, checked) {
    try { storage.setItem(key, JSON.stringify({ version: VERSION, checked })); return true; }
    catch (_) { return false; }
  }
  // The pure storage helpers are also used by the local regression checks.
  if (typeof module !== 'undefined' && module.exports) module.exports = { readState, saveState };
  if (typeof document === 'undefined') return;
  document.querySelectorAll('[data-checklist]').forEach(root => {
    const boxes = Array.from(root.querySelectorAll('input[type="checkbox"][id]'));
    const ids = boxes.map(box => box.id);
    const key = 'safetw:website:checklist:' + root.dataset.checklist;
    let storage;
    try { storage = window.localStorage; } catch (_) { storage = null; }
    const saved = readState(storage, key, ids);
    boxes.forEach(box => { box.checked = saved.includes(box.id); });
    const progress = root.querySelector('progress');
    const count = root.querySelector('[data-count]');
    const status = root.querySelector('[data-status]');
    const storageNote = root.querySelector('[data-storage-note]');
    function update(persist) {
      const checked = boxes.filter(box => box.checked).map(box => box.id);
      progress.max = boxes.length;
      progress.value = checked.length;
      count.textContent = checked.length + ' / ' + boxes.length + ' 項已確認';
      if (persist && !saveState(storage, key, checked)) {
        storageNote.textContent = '此瀏覽器無法儲存勾選，重新整理後可能清除。你仍可列印保存。';
      }
    }
    update(false);
    if (!storage) storageNote.textContent = '此瀏覽器無法儲存勾選，重新整理後可能清除。你仍可列印保存。';
    boxes.forEach(box => box.addEventListener('change', () => { status.textContent = ''; update(true); }));
    root.querySelector('[data-reset]').addEventListener('click', () => {
      boxes.forEach(box => { box.checked = false; });
      update(true);
      status.textContent = '已清除這份清單的勾選，其他頁面的清單不受影響。';
    });
    root.querySelector('[data-print]').addEventListener('click', () => window.print());
    root.querySelector('[data-copy]').addEventListener('click', async () => {
      const heading = document.querySelector('h1').textContent.trim();
      const lines = boxes.map(box => (box.checked ? '[✓] ' : '[ ] ') + box.closest('label').querySelector('[data-item-title]').textContent.trim());
      const value = heading + '\n\n' + lines.join('\n') + '\n\n來源：https://safetw.app/' + window.location.pathname.split('/').pop();
      try {
        await navigator.clipboard.writeText(value);
        status.textContent = '已複製清單文字，可貼到你自己的筆記或訊息。';
      } catch (_) {
        status.textContent = '此瀏覽器不允許複製。請使用列印，或手動選取清單文字。';
      }
    });
  });
}());
