/* ============================================================
   MDGT · LTS Admin — логика панели управления лабораториями
   ============================================================ */

(function () {
  "use strict";

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function esc(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function debounce(fn, ms) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  function fmtDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
  }

  /* ---------- Тосты ---------- */

  const ICONS = {
    success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
    info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
  };

  function toast(kind, title, text) {
    const host = $("#toasts");
    const node = document.createElement("div");
    node.className = `toast toast--${kind}`;
    node.setAttribute("role", "status");
    node.style.cursor = "pointer";
    node.innerHTML = `
      <span class="toast__icon">${ICONS[kind] || ICONS.info}</span>
      <span>
        <span class="toast__title">${esc(title)}</span>
        ${text ? `<br /><span class="toast__text">${esc(text)}</span>` : ""}
      </span>`;
    let done = false;
    const dismiss = () => {
      if (done) return;
      done = true;
      node.style.transition = "opacity .4s, transform .4s";
      node.style.opacity = "0";
      setTimeout(() => node.remove(), 420);
    };
    node.addEventListener("click", dismiss);
    host.appendChild(node);
    setTimeout(dismiss, 5000);
  }

  /* ---------- API ---------- */

  async function api(path, { method = "GET", body } = {}) {
    const opts = { method, credentials: "include", headers: { Accept: "application/json" } };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const response = await fetch(path, opts);
    if (response.status === 401) {
      showLogin();
      throw Object.assign(new Error("Не авторизован"), { status: 401 });
    }
    if (!response.ok) {
      let message = `Ошибка ${response.status}`;
      try {
        const data = await response.json();
        if (data && data.detail) message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      } catch (_) { /* not json */ }
      throw Object.assign(new Error(message), { status: response.status });
    }
    try { return await response.json(); } catch (_) { return null; }
  }

  const showError = (err, fallback) =>
    toast("error", fallback || "Ошибка", err && err.message ? err.message : "");

  /* ---------- Переключение вида ---------- */

  const viewLogin = $("#view-login");
  const viewDash = $("#view-dash");

  function showLogin() {
    viewLogin.hidden = false;
    viewDash.hidden = true;
    $("#user-chip").hidden = true;
    $("#btn-logout").hidden = true;
  }

  function showDash(me) {
    viewLogin.hidden = true;
    viewDash.hidden = false;
    $("#user-chip").hidden = false;
    $("#user-name").textContent = me.username + (me.mock ? " · MOCK" : "");
    $("#btn-logout").hidden = false;
    $("#hero-sub").textContent =
      `Домен *.${me.domain} · образ ${me.image}. Своя база и поддомен у каждой лабы.`;
    loadLabs();
  }

  /* ---------- Модалки ---------- */

  const modalRoot = $("#modal-root");
  const modalBox = $("#modal-box");
  let modalCleanup = null;

  function openModal(html) {
    modalBox.className = "modal";
    modalBox.innerHTML = html;
    modalRoot.classList.add("is-open");
    modalRoot.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const firstInput = modalBox.querySelector("input");
    if (firstInput) setTimeout(() => firstInput.focus(), 60);
    return modalBox;
  }

  function closeModal() {
    modalRoot.classList.remove("is-open");
    modalRoot.setAttribute("aria-hidden", "true");
    modalBox.innerHTML = "";
    document.body.style.overflow = "";
    if (typeof modalCleanup === "function") { modalCleanup(); modalCleanup = null; }
  }

  modalRoot.addEventListener("click", (event) => {
    if (event.target.closest("[data-close-modal]")) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modalRoot.classList.contains("is-open")) closeModal();
  });

  const CLOSE_BTN = `
    <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>`;

  function confirmDialog({ title, text, confirmLabel = "Подтвердить", danger = false }) {
    return new Promise((resolve) => {
      const box = openModal(`
        <div class="modal__head">
          <div>
            <h3 class="modal__title">${esc(title)}</h3>
            <p class="modal__sub">требуется подтверждение</p>
          </div>
        </div>
        <div class="modal__body"><p class="confirm-text">${text}</p></div>
        <div class="modal__foot">
          <button type="button" class="btn btn--ghost" data-act="cancel">Отмена</button>
          <button type="button" class="btn ${danger ? "btn--danger" : "btn--primary"}" data-act="ok">${esc(confirmLabel)}</button>
        </div>`);
      modalCleanup = () => resolve(false);
      box.querySelector('[data-act="cancel"]').addEventListener("click", () => closeModal());
      box.querySelector('[data-act="ok"]').addEventListener("click", () => {
        modalCleanup = null;
        closeModal();
        resolve(true);
      });
    });
  }

  /* ---------- Вход/выход ---------- */

  $("#login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const errorBox = $("#login-error");
    errorBox.hidden = true;
    const submit = $("#login-submit");
    submit.disabled = true;
    try {
      await api("/api/login", {
        method: "POST",
        body: { username: $("#login-username").value.trim(), password: $("#login-password").value },
      });
      const me = await api("/api/me");
      showDash(me);
    } catch (_) {
      errorBox.hidden = false;
    } finally {
      submit.disabled = false;
    }
  });

  $("#btn-logout").addEventListener("click", async () => {
    await api("/api/logout").catch(() => {});
    showLogin();
  });

  /* ---------- Список лаб ---------- */

  let labs = [];

  const STATUS_LABELS = {
    running: "работает",
    stopped: "остановлена",
    deleted: "удалена",
    error: "нет контейнера",
    restarting: "перезапуск",
    created: "создана",
  };

  async function loadLabs() {
    $("#labs-loading").hidden = false;
    try {
      labs = await api("/api/labs");
      renderLabs();
    } catch (err) {
      if (err.status !== 401) showError(err, "Не удалось загрузить список");
    } finally {
      $("#labs-loading").hidden = true;
    }
  }

  function renderLabs() {
    const tbody = $("#labs-tbody");
    tbody.innerHTML = "";
    const visible = labs.filter((lab) => lab.status !== "deleted");
    $("#labs-count").textContent = String(visible.length);
    $("#stat-total").textContent = String(visible.length);
    $("#stat-running").textContent = String(visible.filter((l) => l.status === "running").length);
    $("#labs-empty").hidden = visible.length > 0;
    $("#labs-table").hidden = visible.length === 0;

    visible.forEach((lab) => {
      const stopped = lab.status !== "running";
      const tr = document.createElement("tr");
      tr.style.cursor = "default";
      tr.innerHTML = `
        <td data-th="Статус">
          <span class="status-dot status-dot--${esc(lab.status)}" aria-hidden="true"></span>
          <span class="mono">${esc(STATUS_LABELS[lab.status] || lab.status)}</span>
        </td>
        <td data-th="Лаба">
          <div class="lab-cell__name">${esc(lab.display_name)}</div>
          <div class="lab-cell__sub">${esc(lab.name)}</div>
        </td>
        <td data-th="Адрес"><a class="mono" href="${esc(lab.url)}" target="_blank" rel="noopener">${esc(lab.url.replace(/^https?:\/\//, ""))}</a></td>
        <td class="mono" data-th="БД">${esc(lab.db_name)}</td>
        <td class="mono" data-th="Суперюзер">${esc(lab.superuser_name)}</td>
        <td class="mono" data-th="Создана">${esc(fmtDate(lab.created_at))}</td>
        <td class="num"><span class="row-actions">
          <button type="button" class="icon-btn" data-act="toggle" title="${stopped ? "Запустить" : "Остановить"}" aria-label="${stopped ? "Запустить" : "Остановить"}">
            ${stopped
              ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 4l14 8-14 8z"/></svg>'
              : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="4" width="4" height="16" rx="1"/><rect x="15" y="4" width="4" height="16" rx="1"/></svg>'}
          </button>
          <button type="button" class="icon-btn" data-act="reset" title="Сбросить пароль суперюзера" aria-label="Сбросить пароль">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
          </button>
          <button type="button" class="icon-btn icon-btn--danger" data-act="delete" title="Удалить лабораторию" aria-label="Удалить">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
          </button>
        </span></td>`;

      $('[data-act="toggle"]', tr).addEventListener("click", () => toggleLab(lab, stopped));
      $('[data-act="reset"]', tr).addEventListener("click", () => resetPassword(lab));
      $('[data-act="delete"]', tr).addEventListener("click", () => deleteLab(lab));
      tbody.appendChild(tr);
    });
  }

  async function toggleLab(lab, start) {
    if (!start) {
      const ok = await confirmDialog({
        title: "Остановить лабораторию?",
        text: `<b>${esc(lab.display_name)}</b> станет недоступна пользователям, пока вы не запустите её снова. Данные сохраняются.`,
        confirmLabel: "Остановить",
      });
      if (!ok) return;
    }
    try {
      await api(`/api/labs/${encodeURIComponent(lab.name)}/${start ? "start" : "stop"}`, { method: "POST" });
      toast("success", start ? "Лаборатория запущена" : "Лаборатория остановлена", lab.display_name);
      loadLabs();
    } catch (err) { showError(err); }
  }

  async function resetPassword(lab) {
    const ok = await confirmDialog({
      title: "Сбросить пароль суперюзера?",
      text: `Пароль лаборатории <b>${esc(lab.display_name)}</b> будет заменён новым, контейнер перезапустится (несколько секунд недоступности). Старый пароль перестанет работать.`,
      confirmLabel: "Сбросить",
    });
    if (!ok) return;
    try {
      const creds = await api(`/api/labs/${encodeURIComponent(lab.name)}/reset-password`, { method: "POST" });
      showCredentials(lab.display_name, lab.url, creds, "Новый пароль суперюзера");
    } catch (err) { showError(err); }
  }

  async function deleteLab(lab) {
    const ok = await confirmDialog({
      title: "Удалить лабораторию?",
      text: `Контейнер <b>${esc(lab.display_name)}</b> будет остановлен и снят. База данных <b>сохранится</b> в кластере до ручной очистки (см. README) — данные не теряются.`,
      confirmLabel: "Удалить",
      danger: true,
    });
    if (!ok) return;
    try {
      await api(`/api/labs/${encodeURIComponent(lab.name)}`, { method: "DELETE" });
      toast("success", "Лаборатория удалена", `${lab.display_name} · база осталась в кластере`);
      loadLabs();
    } catch (err) { showError(err); }
  }

  /* ---------- Создание лаборатории ---------- */

  $("#btn-new-lab").addEventListener("click", () => {
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">Новая лаборатория</h3>
          <p class="modal__sub">база + контейнер + поддомен</p>
        </div>
        ${CLOSE_BTN}
      </div>
      <div class="modal__body">
        <label class="field">
          <span class="field__label">Имя (поддомен, латиницей)</span>
          <input type="text" class="field__input field__input--mono" id="lab-name" maxlength="20"
                 placeholder="geo" autocomplete="off" spellcheck="false" />
          <span class="field__hint name-hint" id="name-hint">2–20 символов: a–z, цифры, дефис</span>
        </label>
        <label class="field">
          <span class="field__label">Название</span>
          <input type="text" class="field__input" id="lab-display" maxlength="100"
                 placeholder="Геотехническая лаборатория" />
        </label>
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Отмена</button>
        <button type="button" class="btn btn--primary" id="lab-save" disabled>Создать лабораторию</button>
      </div>`);

    const nameInput = $("#lab-name", box);
    const hint = $("#name-hint", box);
    const saveBtn = $("#lab-save", box);
    let nameOk = false;
    let checkToken = 0;

    const checkName = debounce(async () => {
      const name = nameInput.value.trim().toLowerCase();
      nameInput.value = name;
      nameOk = false;
      saveBtn.disabled = true;
      hint.className = "field__hint name-hint";
      if (!name) { hint.textContent = "2–20 символов: a–z, цифры, дефис"; return; }
      const token = ++checkToken;
      try {
        const result = await api(`/api/labs/check?name=${encodeURIComponent(name)}`);
        if (token !== checkToken) return;
        if (result.ok) {
          nameOk = true;
          saveBtn.disabled = false;
          hint.textContent = `Свободно → ${result.url}`;
          hint.classList.add("is-ok");
        } else {
          hint.textContent = result.reason;
          hint.classList.add("is-bad");
        }
      } catch (_) { /* сеть — молча */ }
    }, 250);

    nameInput.addEventListener("input", checkName);

    saveBtn.addEventListener("click", async () => {
      if (!nameOk) return;
      const name = nameInput.value.trim();
      const displayName = $("#lab-display", box).value.trim() || name;
      saveBtn.disabled = true;
      saveBtn.textContent = "Создаётся…";
      try {
        const result = await api("/api/labs", { method: "POST", body: { name, display_name: displayName } });
        toast("success", "Лаборатория создана", result.lab.url);
        showCredentials(result.lab.display_name, result.lab.url, result.credentials, "Доступ суперюзера");
        loadLabs();
      } catch (err) {
        showError(err, "Не удалось создать лабораторию");
        saveBtn.disabled = false;
        saveBtn.textContent = "Создать лабораторию";
      }
    });
  });

  /* ---------- Показ кредов (один раз) ---------- */

  function credRow(label, value) {
    return `
      <div>
        <div class="cred-label" style="margin-bottom:.3rem;">${esc(label)}</div>
        <div class="cred-row">
          <code>${esc(value)}</code>
          <button type="button" class="icon-btn" data-copy="${esc(value)}" title="Скопировать" aria-label="Скопировать">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
        </div>
      </div>`;
  }

  function showCredentials(labTitle, url, creds, subtitle) {
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">${esc(labTitle)}</h3>
          <p class="modal__sub">${esc(subtitle)}</p>
        </div>
        ${CLOSE_BTN}
      </div>
      <div class="modal__body">
        <div class="cred-warn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="flex:none; margin-top:.15rem;"><path d="M10.3 3.9L1.8 18a2 2 0 001.7 3h17a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
          <span>Пароль показывается <b>только сейчас</b> — сохраните его. Потом можно будет лишь сбросить на новый.</span>
        </div>
        ${credRow("Адрес", url)}
        ${credRow("Логин", creds.login)}
        ${credRow("Пароль", creds.password)}
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--primary" data-close-modal>Готово, сохранил</button>
      </div>`);

    $$("[data-copy]", box).forEach((btn) =>
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(btn.dataset.copy);
          toast("success", "Скопировано");
        } catch (_) {
          toast("error", "Не удалось скопировать", "Скопируйте вручную");
        }
      }));
  }

  /* ---------- Обновить все ---------- */

  $("#btn-update-all").addEventListener("click", async () => {
    const ok = await confirmDialog({
      title: "Обновить все лаборатории?",
      text: "Будет скачан свежий образ и поочерёдно пересозданы контейнеры всех работающих лаб. Каждая лаба будет недоступна несколько секунд.",
      confirmLabel: "Обновить",
    });
    if (!ok) return;
    const btn = $("#btn-update-all");
    btn.disabled = true;
    try {
      const result = await api("/api/update-all", { method: "POST" });
      toast("success", "Обновление завершено",
        result.updated.length ? `Обновлены: ${result.updated.join(", ")}` : "Работающих лаб нет");
      loadLabs();
    } catch (err) {
      showError(err, "Не удалось обновить");
    } finally {
      btn.disabled = false;
    }
  });

  /* ---------- Старт ---------- */

  api("/api/me")
    .then((me) => showDash(me))
    .catch(() => showLogin());
})();
