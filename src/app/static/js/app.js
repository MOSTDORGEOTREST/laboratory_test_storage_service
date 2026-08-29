/* ============================================================
   MDGT · LTS — логика интерфейса
   ============================================================ */

(function () {
  "use strict";

  /* ================= Утилиты ================= */

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

  function fmtDateTime(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" }) +
      " " + date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
  }

  // 32-символьный hex-идентификатор (совместим с ID из EngGeo)
  function genId() {
    const bytes = new Uint8Array(16);
    (window.crypto || window.msCrypto).getRandomValues(bytes);
    return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function countUp(el, target, suffix = "") {
    if (!el) return;
    const value = Number(target) || 0;
    if (prefersReducedMotion || value === 0) { el.textContent = String(value) + suffix; return; }
    const duration = 900;
    const start = performance.now();
    const cubicOut = (t) => 1 - Math.pow(1 - t, 3);
    function tick(now) {
      const progress = Math.min(1, (now - start) / duration);
      el.textContent = String(Math.round(cubicOut(progress) * value)) + (progress >= 1 ? suffix : "");
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  /* ================= Тосты ================= */

  const ICONS = {
    success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
    info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
  };

  function toast(kind, title, text) {
    const host = $("#toasts");
    if (!host) return;
    const node = document.createElement("div");
    node.className = `toast toast--${kind}`;
    node.setAttribute("role", "status");
    node.innerHTML = `
      <span class="toast__icon">${ICONS[kind] || ICONS.info}</span>
      <span>
        <span class="toast__title">${esc(title)}</span>
        ${text ? `<br /><span class="toast__text">${esc(text)}</span>` : ""}
      </span>`;
    node.style.cursor = "pointer";
    node.title = "Скрыть";
    let dismissed = false;
    const dismiss = () => {
      if (dismissed) return;
      dismissed = true;
      node.style.transition = "opacity .4s, transform .4s";
      node.style.opacity = "0";
      node.style.transform = "translateY(-6px)";
      setTimeout(() => node.remove(), 420);
    };
    node.addEventListener("click", dismiss);
    host.appendChild(node);
    setTimeout(dismiss, 4200);
  }

  // Понятные русские сообщения для известных ответов бэкенда
  const ERROR_TRANSLATIONS = {
    "Not found": "Не найдено",
    "Not unique": "Такое значение уже существует",
    "Data structure exception": "Нельзя удалить: есть связанные опыты",
    "You should delete all tests in this sample before": "Сначала удалите все опыты этого образца",
    "You should delete all samples in this borehole before": "Сначала удалите все образцы этой скважины",
    "Authentication failed": "Сессия истекла — войдите заново",
    "Internal Server Error": "Внутренняя ошибка сервера",
  };

  function showError(err, fallback) {
    const raw = err && err.message ? err.message : "";
    const text = ERROR_TRANSLATIONS[raw] || raw;
    toast("error", fallback || "Ошибка", text);
  }

  /* ================= Навбар (обе страницы) ================= */

  const navbar = $("#navbar");
  if (navbar) {
    const onScroll = () => navbar.classList.toggle("is-scrolled", window.scrollY > 10);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  const appRoot = $("#app");

  // Элементы «только для кабинета» на странице входа не нужны
  if (!appRoot) $$(".app-only").forEach((el) => { el.hidden = true; el.style.display = "none"; });

  function doLogout() {
    API.signOut().then(() => { window.location.href = "./"; });
  }

  /* ================= Модалки ================= */

  const modalRoot = $("#modal-root");
  const modalBox = $("#modal-box");
  let modalCleanup = null;

  function openModal(html, { wide = false } = {}) {
    if (!modalRoot) return null;
    modalBox.className = "modal" + (wide ? " modal--wide" : "");
    modalBox.innerHTML = html;
    modalRoot.classList.add("is-open");
    modalRoot.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const firstInput = modalBox.querySelector("input, select, textarea");
    if (firstInput) setTimeout(() => firstInput.focus(), 60);
    return modalBox;
  }

  function closeModal() {
    if (!modalRoot) return;
    modalRoot.classList.remove("is-open");
    modalRoot.setAttribute("aria-hidden", "true");
    modalBox.innerHTML = "";
    document.body.style.overflow = "";
    if (typeof modalCleanup === "function") { modalCleanup(); modalCleanup = null; }
  }

  if (modalRoot) {
    modalRoot.addEventListener("click", (event) => {
      if (event.target.closest("[data-close-modal]")) closeModal();
    });
  }

  function confirmDialog({ title, text, confirmLabel = "Удалить", danger = true }) {
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
      if (!box) { resolve(false); return; }
      modalCleanup = () => resolve(false);
      box.querySelector('[data-act="cancel"]').addEventListener("click", () => closeModal());
      box.querySelector('[data-act="ok"]').addEventListener("click", () => {
        modalCleanup = null;
        closeModal();
        resolve(true);
      });
    });
  }

  /* ================= Панель деталей ================= */

  const detailRoot = $("#detail-root");
  const detailPanel = $("#detail-panel");

  function openDetail() {
    if (!detailRoot) return;
    detailRoot.classList.add("is-open");
    detailRoot.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeDetail() {
    if (!detailRoot) return;
    detailRoot.classList.remove("is-open");
    detailRoot.setAttribute("aria-hidden", "true");
    if (!modalRoot || !modalRoot.classList.contains("is-open")) document.body.style.overflow = "";
    detailPanel.innerHTML = "";
  }

  if (detailRoot) {
    detailRoot.addEventListener("click", (event) => {
      if (event.target.closest("[data-close-detail]")) closeDetail();
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (modalRoot && modalRoot.classList.contains("is-open")) closeModal();
    else if (detailRoot && detailRoot.classList.contains("is-open")) closeDetail();
    else {
      const drawer = $("#nav-drawer");
      if (drawer && drawer.classList.contains("is-open")) toggleDrawer(false);
    }
  });

  /* ================= Мобильное меню ================= */

  const drawer = $("#nav-drawer");
  const burger = $("#burger");

  function toggleDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    if (burger) burger.setAttribute("aria-expanded", String(open));
  }

  if (burger) burger.addEventListener("click", () => toggleDrawer(true));
  if (drawer) {
    drawer.addEventListener("click", (event) => {
      if (event.target.closest("[data-close-drawer]")) toggleDrawer(false);
    });
  }

  /* ============================================================
     Дальше — только рабочий кабинет
     ============================================================ */
  if (!appRoot) return;

  $$(".app-only").forEach((el) => { el.hidden = false; });
  if (burger) burger.hidden = false;

  /* ================= Состояние ================= */

  const LIMIT = 100;
  const state = {
    user: null,
    objects: [],
    testTypes: [],
    tests: [],
    testsOffset: 0,
    testsHasMore: false,
    filters: { objectNumber: "", boreholeName: "", testType: "", search: "" },
    boreholesByObject: new Map(), // object_id -> [boreholes]
    samplesByBorehole: new Map(), // borehole_id -> [samples]
    selectedObjectId: null,
    selectedBoreholeId: null,
    currentTest: null,
    currentFiles: [],
  };

  function initialObjects() {
    const node = $("#objects-data");
    if (!node) return [];
    try {
      const parsed = JSON.parse(node.textContent);
      return Array.isArray(parsed) ? parsed : [];
    } catch (_) { return []; }
  }

  /* ================= Авторизованный пользователь ================= */

  API.getUser().then((user) => {
    if (!user) return;
    state.user = user;
    const chip = $("#user-chip");
    if (chip) { chip.hidden = false; $("#user-name").textContent = user.username; }
    const mobileName = $("#user-name-mobile");
    if (mobileName) mobileName.textContent = user.username;
    const logoutBtn = $("#nav-logout");
    if (logoutBtn) logoutBtn.hidden = false;
  });

  const logoutBtn = $("#nav-logout");
  if (logoutBtn) logoutBtn.addEventListener("click", doLogout);
  const logoutMobile = $("#nav-logout-mobile");
  if (logoutMobile) logoutMobile.addEventListener("click", doLogout);

  /* ================= Переключение видов ================= */

  const views = { tests: $("#view-tests"), objects: $("#view-objects"), types: $("#view-types") };

  function setTabCount(key, text) {
    $$(`[data-tab-count="${key}"]`).forEach((em) => { em.textContent = text; });
  }

  function switchView(name) {
    Object.entries(views).forEach(([key, el]) => { if (el) el.hidden = key !== name; });
    $$(".nav-tab[data-view]").forEach((tab) =>
      tab.classList.toggle("is-active", tab.dataset.view === name));
    toggleDrawer(false);
    window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
  }

  $$(".nav-tab[data-view]").forEach((tab) =>
    tab.addEventListener("click", () => switchView(tab.dataset.view)));

  /* ================= KV-редактор ================= */

  function createKvEditor(host, initial, label) {
    let mode = "kv";
    // Защита от не-объектных значений из JSONB (строка/массив/число)
    const source = initial && typeof initial === "object" && !Array.isArray(initial) ? initial : {};
    const rows = Object.entries(source).map(([k, v]) => ({
      k, v: typeof v === "object" && v !== null ? JSON.stringify(v) : String(v),
    }));
    if (rows.length === 0) rows.push({ k: "", v: "" });

    host.classList.add("kv-editor");
    host.innerHTML = `
      <div class="kv-editor__head">
        <span class="field__label">${esc(label)}</span>
        <span class="seg" role="tablist">
          <button type="button" class="seg__btn is-active" data-mode="kv">Пары</button>
          <button type="button" class="seg__btn" data-mode="json">JSON</button>
        </span>
      </div>
      <div class="kv-editor__rows"></div>
      <div class="kv-json" hidden>
        <textarea class="field__textarea" spellcheck="false" placeholder="{ }"></textarea>
        <p class="field__hint">Валидный JSON-объект или пусто</p>
      </div>
      <div><button type="button" class="btn btn--ghost btn--sm" data-add>+ Параметр</button></div>`;

    const rowsHost = $(".kv-editor__rows", host);
    const jsonWrap = $(".kv-json", host);
    const textarea = $("textarea", jsonWrap);
    const addBtn = $("[data-add]", host);

    function renderRows() {
      rowsHost.innerHTML = "";
      rows.forEach((row, index) => {
        const div = document.createElement("div");
        div.className = "kv-row";
        div.innerHTML = `
          <input type="text" class="field__input field__input--mono" placeholder="ключ" value="${esc(row.k)}" data-k />
          <input type="text" class="field__input field__input--mono" placeholder="значение" value="${esc(row.v)}" data-v />
          <button type="button" class="icon-btn icon-btn--danger" data-del aria-label="Удалить строку">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>`;
        $("[data-k]", div).addEventListener("input", (e) => { row.k = e.target.value; });
        $("[data-v]", div).addEventListener("input", (e) => { row.v = e.target.value; });
        $("[data-del]", div).addEventListener("click", () => { rows.splice(index, 1); if (!rows.length) rows.push({ k: "", v: "" }); renderRows(); });
        rowsHost.appendChild(div);
      });
    }

    function rowsToObject() {
      const result = {};
      rows.forEach(({ k, v }) => {
        const key = k.trim();
        if (!key) return;
        const raw = v.trim();
        if (raw !== "" && !Number.isNaN(Number(raw.replace(",", "."))) && /^-?\d+([.,]\d+)?$/.test(raw)) {
          result[key] = Number(raw.replace(",", "."));
        } else {
          try { result[key] = JSON.parse(raw); }
          catch (_) { result[key] = raw; }
        }
      });
      return result;
    }

    function setMode(next) {
      if (next === mode) return;
      if (next === "json") {
        const obj = rowsToObject();
        textarea.value = Object.keys(obj).length ? JSON.stringify(obj, null, 2) : "";
      } else {
        const parsed = parseJsonArea();
        if (parsed === undefined) return; // невалидный JSON — остаёмся
        rows.length = 0;
        Object.entries(parsed || {}).forEach(([k, v]) =>
          rows.push({ k, v: typeof v === "object" && v !== null ? JSON.stringify(v) : String(v) }));
        if (!rows.length) rows.push({ k: "", v: "" });
        renderRows();
      }
      mode = next;
      rowsHost.hidden = mode !== "kv";
      addBtn.parentElement.hidden = mode !== "kv";
      jsonWrap.hidden = mode !== "json";
      $$(".seg__btn", host).forEach((b) => b.classList.toggle("is-active", b.dataset.mode === mode));
    }

    function parseJsonArea() {
      const raw = textarea.value.trim();
      if (!raw) return null;
      try {
        const parsed = JSON.parse(raw);
        if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error();
        textarea.classList.remove("is-invalid");
        return parsed;
      } catch (_) {
        textarea.classList.add("is-invalid");
        toast("error", "Невалидный JSON", `Проверьте поле «${label}»`);
        return undefined;
      }
    }

    $$(".seg__btn", host).forEach((btn) =>
      btn.addEventListener("click", () => setMode(btn.dataset.mode)));
    addBtn.addEventListener("click", () => { rows.push({ k: "", v: "" }); renderRows(); });
    renderRows();

    return {
      getValue() {
        if (mode === "json") {
          const parsed = parseJsonArea();
          if (parsed === undefined) return undefined;
          return parsed && Object.keys(parsed).length ? parsed : null;
        }
        const obj = rowsToObject();
        return Object.keys(obj).length ? obj : null;
      },
    };
  }

  /* ================= Справочники для селектов ================= */

  async function boreholesFor(objectId, force) {
    if (!force && state.boreholesByObject.has(objectId)) return state.boreholesByObject.get(objectId);
    const list = await API.getBoreholes(objectId);
    state.boreholesByObject.set(objectId, list);
    return list;
  }

  async function samplesFor(boreholeId, force) {
    if (!force && state.samplesByBorehole.has(boreholeId)) return state.samplesByBorehole.get(boreholeId);
    const list = await API.getSamples(boreholeId);
    state.samplesByBorehole.set(boreholeId, list);
    return list;
  }

  /* ================= Комбобокс объектов (ввод с подсказками) =================
     Объектов в базе много — выпадающий select неудобен. Ввод с фильтрацией
     по номеру и описанию, клавиатурной навигацией и точным применением. */
  function createObjectCombo({ input, listEl, clearBtn, onPick }) {
    let activeIndex = -1;
    let items = [];
    let applied = ""; // применённый номер объекта

    function matches(query) {
      const q = query.trim().toLowerCase();
      const all = state.objects.slice().sort((a, b) =>
        String(a.object_number).localeCompare(String(b.object_number), "ru", { numeric: true }));
      if (!q) return all.slice(0, 50);
      return all.filter((o) =>
        String(o.object_number).toLowerCase().includes(q) ||
        String(o.description ?? "").toLowerCase().includes(q)).slice(0, 50);
    }

    function close() {
      listEl.hidden = true;
      input.setAttribute("aria-expanded", "false");
      activeIndex = -1;
    }

    function open() {
      items = matches(input.value);
      listEl.innerHTML = "";
      if (!items.length) {
        listEl.innerHTML = '<div class="combo__empty">Объект не найден</div>';
      } else {
        const q = input.value.trim().toLowerCase();
        items.forEach((obj) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "combo__item";
          btn.setAttribute("role", "option");
          btn.innerHTML = `
            <span class="combo__item-num">${highlight(obj.object_number, q)}</span>
            <span class="combo__item-desc">${highlight(obj.description || "Без описания", q)}</span>`;
          // mousedown срабатывает раньше blur — клик по подсказке успевает выбрать
          btn.addEventListener("mousedown", (event) => { event.preventDefault(); pick(obj); });
          listEl.appendChild(btn);
        });
      }
      listEl.hidden = false;
      input.setAttribute("aria-expanded", "true");
      activeIndex = -1;
    }

    function highlightActive() {
      const els = $$(".combo__item", listEl);
      els.forEach((el, i) => el.classList.toggle("is-active", i === activeIndex));
      if (els[activeIndex]) els[activeIndex].scrollIntoView({ block: "nearest" });
    }

    function pick(obj) {
      applied = obj ? obj.object_number : "";
      input.value = applied;
      if (clearBtn) clearBtn.hidden = !applied;
      close();
      onPick(obj);
    }

    input.addEventListener("input", () => {
      if (clearBtn) clearBtn.hidden = input.value === "";
      if (input.value.trim() === "" && applied) { pick(null); open(); return; }
      open();
    });
    // открываем по клику, а не по focus: автофокус модалки не должен
    // разворачивать список сам по себе
    input.addEventListener("click", open);
    input.addEventListener("blur", () => {
      setTimeout(() => {
        // уход без выбора — возвращаем применённое значение
        input.value = applied;
        if (clearBtn) clearBtn.hidden = !applied;
        close();
      }, 120);
    });
    input.addEventListener("keydown", (event) => {
      if (listEl.hidden && (event.key === "ArrowDown" || event.key === "ArrowUp")) { open(); return; }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        highlightActive();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        highlightActive();
      } else if (event.key === "Enter") {
        event.preventDefault();
        if (activeIndex >= 0 && items[activeIndex]) { pick(items[activeIndex]); return; }
        const exact = state.objects.find((o) =>
          String(o.object_number).toLowerCase() === input.value.trim().toLowerCase());
        if (exact) pick(exact);
        else if (items.length === 1) pick(items[0]);
      } else if (event.key === "Escape" && !listEl.hidden) {
        input.value = applied;
        close();
        event.stopPropagation(); // не закрывать модалку/панель, пока открыт список
      }
    });
    if (clearBtn) clearBtn.addEventListener("click", () => { pick(null); input.focus(); });

    return {
      setValue(objectNumber) {
        applied = objectNumber || "";
        input.value = applied;
        if (clearBtn) clearBtn.hidden = !applied;
        close();
      },
    };
  }

  function fillSelect(select, items, { value, text, placeholder, keep }) {
    const current = keep ? select.value : "";
    select.innerHTML = "";
    if (placeholder !== undefined) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = placeholder;
      select.appendChild(opt);
    }
    items.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = String(value(item));
      opt.textContent = text(item);
      select.appendChild(opt);
    });
    if (keep && current) select.value = current;
  }

  /* ================= ВИД: ОПЫТЫ ================= */

  const testsEls = {
    tbody: $("#tests-tbody"),
    table: $("#tests-table"),
    count: $("#tests-count"),
    empty: $("#tests-empty"),
    emptyText: $("#tests-empty-text"),
    loading: $("#tests-loading"),
    moreRow: $("#tests-more-row"),
    fObject: $("#f-object"),
    fBorehole: $("#f-borehole"),
    fType: $("#f-type"),
    fSearch: $("#f-search"),
  };

  let testsFetchToken = 0;

  function visibleTests() {
    // Клиентская сортировка «новые сверху»; у старых записей timestamp может
    // отсутствовать — NaN приводим к 0, чтобы sort оставался корректным
    const ts = (t) => {
      const ms = new Date(t.timestamp).getTime();
      return Number.isNaN(ms) ? 0 : ms;
    };
    const sorted = state.tests.slice().sort((a, b) => {
      const diff = ts(b) - ts(a);
      return diff !== 0 ? diff : b.test_id - a.test_id;
    });
    const q = state.filters.search.trim().toLowerCase();
    if (!q) return sorted;
    return sorted.filter((t) => {
      const dateStr = fmtDate(t.timestamp);
      return [t.test_id, t.object_number, t.borehole_name, t.laboratory_number, t.soil_type, t.test_type, t.description, dateStr]
        .some((v) => String(v ?? "").toLowerCase().includes(q));
    });
  }

  function renderTests() {
    const list = visibleTests();
    testsEls.count.textContent = String(list.length);
    testsEls.tbody.innerHTML = "";

    if (!list.length) {
      testsEls.empty.hidden = false;
      testsEls.emptyText.textContent = state.tests.length
        ? "По вашему запросу ничего не найдено"
        : "Опытов не найдено — измените фильтры или создайте новый";
      testsEls.table.hidden = true;
    } else {
      testsEls.empty.hidden = true;
      testsEls.table.hidden = false;
      const fragment = document.createDocumentFragment();
      list.forEach((test) => {
        const tr = document.createElement("tr");
        tr.tabIndex = 0;
        tr.innerHTML = `
          <td class="mono" data-th="ID">${esc(test.test_id)}</td>
          <td class="mono" data-th="Дата">${esc(fmtDate(test.timestamp))}</td>
          <td data-th="Объект"><span class="chip chip--neutral">${esc(test.object_number ?? "—")}</span></td>
          <td class="mono" data-th="Скв">${esc(test.borehole_name ?? "—")}</td>
          <td class="mono" data-th="Л/н">${esc(test.laboratory_number ?? "—")}</td>
          <td data-th="Грунт">${esc(test.soil_type ?? "—")}</td>
          <td data-th="Тип"><span class="chip chip--amber">${esc(test.test_type ?? "—")}</span></td>
          <td class="num"><span class="row-actions">
            <button type="button" class="icon-btn" data-open aria-label="Открыть опыт">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </span></td>`;
        const open = () => openTestDetail(test);
        tr.addEventListener("click", open);
        tr.addEventListener("keydown", (e) => { if (e.key === "Enter") open(); });
        fragment.appendChild(tr);
      });
      testsEls.tbody.appendChild(fragment);
    }
    testsEls.moreRow.hidden = !state.testsHasMore;
  }

  /* Точное количество опытов в базе: у бэка нет count-эндпоинта, поэтому
     считаем бинарным поиском по offset дешёвыми запросами limit=1
     (~2·log2(N) запросов даже для сотен тысяч записей). */
  async function countTestsTotal(token) {
    try {
      const exists = async (offset) =>
        (await API.getTests({ limit: 1, offset })).length > 0;
      let lo = Math.max(state.tests.length - 1, 0); // здесь строка точно есть
      let hi = Math.max(256, (lo + 1) * 2);
      while (await exists(hi)) {
        if (token !== testsFetchToken) return null;
        lo = hi;
        hi *= 2;
        if (hi > 2000000) break;
      }
      while (lo + 1 < hi) {
        if (token !== testsFetchToken) return null;
        const mid = Math.floor((lo + hi) / 2);
        if (await exists(mid)) lo = mid; else hi = mid;
      }
      return hi;
    } catch (_) { return null; }
  }

  function setTestsTotal(total) {
    if (total < 1000) {
      countUp($("#stat-tests"), total);
      setTabCount("tests", String(total));
    } else {
      // больше тысячи — пишем в тысячах: «3+ тыс»
      const thousands = Math.floor(total / 1000);
      $("#stat-tests").textContent = `${thousands}+ тыс`;
      setTabCount("tests", `${thousands}+ тыс`);
    }
  }

  async function loadTests({ append = false } = {}) {
    const token = ++testsFetchToken;
    if (!append) { state.testsOffset = 0; state.tests = []; }
    testsEls.loading.hidden = false;
    testsEls.empty.hidden = true;
    try {
      const chunk = await API.getTests({
        objectNumber: state.filters.objectNumber || undefined,
        boreholeName: state.filters.boreholeName || undefined,
        testType: state.filters.testType || undefined,
        limit: LIMIT,
        offset: state.testsOffset,
      });
      if (token !== testsFetchToken) return;
      if (append) {
        // Пагинация без ORDER BY на сервере может отдать дубликаты — отфильтруем
        const seen = new Set(state.tests.map((t) => t.test_id));
        state.tests = state.tests.concat(chunk.filter((t) => !seen.has(t.test_id)));
      } else {
        state.tests = chunk;
      }
      state.testsHasMore = chunk.length === LIMIT;
      state.testsOffset += chunk.length;
      renderTests();
      // Счётчики в hero и в табе — только для нефильтрованной выборки
      const unfiltered = !state.filters.objectNumber && !state.filters.boreholeName && !state.filters.testType;
      if (unfiltered && !append) {
        if (!state.testsHasMore) {
          setTestsTotal(state.tests.length); // всё уже загружено — число точное
        } else {
          countTestsTotal(token).then((total) => {
            if (token === testsFetchToken && total != null) setTestsTotal(total);
          });
        }
      }
    } catch (err) {
      if (token !== testsFetchToken) return;
      showError(err, "Не удалось загрузить опыты");
    } finally {
      if (token === testsFetchToken) testsEls.loading.hidden = true;
    }
  }

  function refreshFilterSelects() {
    fillSelect(testsEls.fType, state.testTypes, {
      value: (t) => t.test_type,
      text: (t) => t.test_type,
      placeholder: "Все типы",
      keep: true,
    });
  }

  const objectCombo = createObjectCombo({
    input: testsEls.fObject,
    listEl: $("#f-object-combo .combo__list"),
    clearBtn: $("#f-object-clear"),
    onPick: async (obj) => {
      state.filters.objectNumber = obj ? obj.object_number : "";
      state.filters.boreholeName = "";
      testsEls.fBorehole.innerHTML = '<option value="">Все скважины</option>';
      testsEls.fBorehole.disabled = !obj;
      if (obj) {
        try {
          const boreholes = await boreholesFor(obj.object_id);
          fillSelect(testsEls.fBorehole, boreholes, {
            value: (b) => b.borehole_name,
            text: (b) => b.borehole_name,
            placeholder: "Все скважины",
          });
        } catch (_) { /* нет скважин */ }
      }
      loadTests();
    },
  });

  testsEls.fBorehole.addEventListener("change", () => {
    state.filters.boreholeName = testsEls.fBorehole.value;
    loadTests();
  });

  testsEls.fType.addEventListener("change", () => {
    state.filters.testType = testsEls.fType.value;
    loadTests();
  });

  testsEls.fSearch.addEventListener("input", debounce(() => {
    state.filters.search = testsEls.fSearch.value;
    renderTests();
  }, 150));

  $("#btn-reset-filters").addEventListener("click", () => {
    state.filters = { objectNumber: "", boreholeName: "", testType: "", search: "" };
    objectCombo.setValue("");
    testsEls.fBorehole.innerHTML = '<option value="">Все скважины</option>';
    testsEls.fBorehole.disabled = true;
    testsEls.fType.value = "";
    testsEls.fSearch.value = "";
    loadTests();
  });

  $("#btn-tests-more").addEventListener("click", () => loadTests({ append: true }));

  /* ================= Детали опыта ================= */

  function kvListHtml(data) {
    // В JSONB реальной базы может лежать не только объект — массив, строка, число.
    // Такое показываем как есть, не разбирая на пары.
    if (data !== null && data !== undefined && (typeof data !== "object" || Array.isArray(data))) {
      return `<dl class="kv-list"><dt>JSON</dt><dd>${esc(JSON.stringify(data))}</dd></dl>`;
    }
    if (!data || !Object.keys(data).length) {
      return '<p class="empty-state empty-state--compact">Нет данных</p>';
    }
    const rows = Object.entries(data)
      .map(([key, value]) => `<dt>${esc(key)}</dt><dd>${esc(
        typeof value === "object" && value !== null ? JSON.stringify(value) : value
      )}</dd>`)
      .join("");
    return `<dl class="kv-list">${rows}</dl>`;
  }

  function fileNameFromKey(key) {
    const parts = String(key || "").split("/");
    return parts[parts.length - 1] || key;
  }

  function renderDetailFiles(files) {
    const host = $("#detail-files", detailPanel);
    if (!host) return;
    state.currentFiles = files;
    if (!files.length) {
      host.innerHTML = '<p class="empty-state empty-state--compact">Файлов пока нет — добавьте первый отчёт</p>';
      return;
    }
    host.innerHTML = `<ul class="file-list">${files.map((file) => `
      <li class="file-item">
        <span class="file-item__icon">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
        </span>
        <span class="file-item__main">
          <a class="file-item__name" href="${API.fileUrl(file.key)}" target="_blank" rel="noopener">${esc(fileNameFromKey(file.key))}</a>
          ${file.description ? `<div class="file-item__desc">${esc(file.description)}</div>` : ""}
          <div class="file-item__date">загружен ${esc(fmtDateTime(file.upload))}</div>
        </span>
        <span class="file-item__actions">
          <a class="icon-btn" href="${API.fileUrl(file.key)}" target="_blank" rel="noopener" aria-label="Скачать файл" title="Скачать">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          </a>
          <button type="button" class="icon-btn icon-btn--danger" data-del-file="${esc(file.file_id)}" aria-label="Удалить файл" title="Удалить">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
          </button>
        </span>
      </li>`).join("")}</ul>`;

    $$("[data-del-file]", host).forEach((btn) =>
      btn.addEventListener("click", async () => {
        const fileId = btn.dataset.delFile;
        const file = files.find((f) => String(f.file_id) === fileId);
        const ok = await confirmDialog({
          title: "Удалить файл?",
          text: `Файл <b>${esc(fileNameFromKey(file ? file.key : ""))}</b> будет удалён из базы и из хранилища S3. Действие необратимо.`,
        });
        if (!ok) return;
        try {
          await API.deleteFile(fileId);
          toast("success", "Файл удалён");
          reloadDetailFiles();
        } catch (err) { showError(err, "Не удалось удалить файл"); }
      }));
  }

  function reloadDetailFiles() {
    if (!state.currentTest) return;
    API.getTestFiles(state.currentTest.test_id)
      .then((files) => renderDetailFiles(files))
      .catch(() => renderDetailFiles([]));
  }

  function openTestDetail(test) {
    state.currentTest = test;
    detailPanel.innerHTML = `
      <div class="detail-panel__head">
        <button type="button" class="icon-btn detail-panel__close" data-close-detail aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
        <p class="eyebrow"><span class="live-dot" aria-hidden="true"></span>Опыт · ID ${esc(test.test_id)}</p>
        <h3 class="detail-panel__title">${esc(test.test_type ?? "Без типа")}</h3>
        <div class="detail-panel__meta">
          <span class="chip">объект ${esc(test.object_number ?? "—")}</span>
          <span class="chip">скв. ${esc(test.borehole_name ?? "—")}</span>
          <span class="chip">л/н ${esc(test.laboratory_number ?? "—")}</span>
          <span class="chip">${esc(fmtDateTime(test.timestamp))}</span>
        </div>
      </div>
      <div class="detail-panel__body">
        <div class="card detail-block">
          <div class="detail-block__title">Образец <i>01</i></div>
          <dl class="kv-list">
            <dt>Грунт</dt><dd>${esc(test.soil_type ?? "—")}</dd>
            ${test.description ? `<dt>Описание</dt><dd>${esc(test.description)}</dd>` : ""}
          </dl>
        </div>
        <div class="card detail-block">
          <div class="detail-block__title">Параметры опыта <i>02</i></div>
          ${kvListHtml(test.test_params)}
        </div>
        <div class="card detail-block">
          <div class="detail-block__title">Результаты <i>03</i></div>
          ${kvListHtml(test.test_results)}
        </div>
        <div class="card detail-block">
          <div class="detail-block__title">
            Файлы отчётов
            <span style="display:inline-flex; align-items:center; gap:.8rem;">
              <button type="button" class="btn btn--ghost btn--sm" id="btn-del-all-files">Удалить все</button>
              <i>04</i>
            </span>
          </div>
          <div id="detail-files">
            <div class="loading-state"><span class="spinner"></span><span>Загрузка файлов…</span></div>
          </div>
          <div style="margin-top:.9rem; display:grid; gap:.6rem;">
            <div class="dropzone" id="dropzone" tabindex="0" role="button" aria-label="Загрузить файл">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
              <span>Перетащите файл сюда или <b>выберите</b></span>
              <span class="dropzone__file" id="dropzone-file" hidden></span>
              <input type="file" id="file-input" hidden />
            </div>
            <input type="text" class="field__input" id="file-desc" placeholder="Описание файла (необязательно)" />
            <div class="progress" id="upload-progress" hidden><div class="progress__bar" id="upload-bar"></div></div>
            <button type="button" class="btn btn--primary" id="btn-upload" disabled>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
              Загрузить файл
            </button>
          </div>
        </div>
      </div>
      <div class="detail-panel__actions">
        <button type="button" class="btn btn--ghost" id="btn-edit-test">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
          Редактировать
        </button>
        <button type="button" class="btn btn--danger" id="btn-del-test">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
          Удалить опыт
        </button>
      </div>`;
    openDetail();
    reloadDetailFiles();

    /* --- загрузка файла --- */
    const dropzone = $("#dropzone", detailPanel);
    const fileInput = $("#file-input", detailPanel);
    const fileLabel = $("#dropzone-file", detailPanel);
    const uploadBtn = $("#btn-upload", detailPanel);
    let pickedFile = null;

    function setPicked(file) {
      if (file && file.size > 50 * 1024 * 1024) {
        toast("error", "Файл слишком большой", "Максимальный размер — 50 МБ");
        return;
      }
      pickedFile = file || null;
      fileLabel.hidden = !pickedFile;
      if (pickedFile) fileLabel.textContent = `${pickedFile.name} · ${(pickedFile.size / 1024 / 1024).toFixed(2)} МБ`;
      uploadBtn.disabled = !pickedFile;
    }

    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); } });
    fileInput.addEventListener("change", () => setPicked(fileInput.files[0]));
    ["dragenter", "dragover"].forEach((type) =>
      dropzone.addEventListener(type, (e) => { e.preventDefault(); dropzone.classList.add("is-drag"); }));
    ["dragleave", "drop"].forEach((type) =>
      dropzone.addEventListener(type, (e) => { e.preventDefault(); dropzone.classList.remove("is-drag"); }));
    dropzone.addEventListener("drop", (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) setPicked(e.dataTransfer.files[0]);
    });

    uploadBtn.addEventListener("click", async () => {
      if (!pickedFile) return;
      const progressWrap = $("#upload-progress", detailPanel);
      const bar = $("#upload-bar", detailPanel);
      uploadBtn.disabled = true;
      progressWrap.hidden = false;
      bar.style.width = "0%";
      try {
        await API.uploadFile(test.test_id, pickedFile, $("#file-desc", detailPanel).value.trim(),
          (ratio) => { bar.style.width = `${Math.round(ratio * 100)}%`; });
        bar.style.width = "100%";
        toast("success", "Файл загружен", pickedFile.name);
        setPicked(null);
        fileInput.value = "";
        $("#file-desc", detailPanel).value = "";
        reloadDetailFiles();
      } catch (err) {
        showError(err, "Не удалось загрузить файл");
      } finally {
        uploadBtn.disabled = !pickedFile;
        setTimeout(() => { progressWrap.hidden = true; }, 600);
      }
    });

    /* --- удалить все файлы --- */
    $("#btn-del-all-files", detailPanel).addEventListener("click", async () => {
      if (!state.currentFiles.length) { toast("info", "Файлов нет"); return; }
      const ok = await confirmDialog({
        title: "Удалить все файлы?",
        text: `Будут удалены <b>все файлы (${state.currentFiles.length})</b> этого опыта из базы и из S3.`,
      });
      if (!ok) return;
      try {
        await API.deleteAllFiles(test.test_id);
        toast("success", "Файлы удалены");
        reloadDetailFiles();
      } catch (err) { showError(err, "Не удалось удалить файлы"); }
    });

    /* --- удалить опыт --- */
    $("#btn-del-test", detailPanel).addEventListener("click", async () => {
      const ok = await confirmDialog({
        title: "Удалить опыт?",
        text: `Опыт <b>№${esc(test.test_id)} · ${esc(test.test_type)}</b> (л/н ${esc(test.laboratory_number)}) и все его файлы будут удалены безвозвратно.`,
      });
      if (!ok) return;
      try {
        await API.deleteTest(test.test_id);
        toast("success", "Опыт удалён", `ID ${test.test_id}`);
        closeDetail();
        loadTests();
      } catch (err) { showError(err, "Не удалось удалить опыт"); }
    });

    /* --- редактировать --- */
    $("#btn-edit-test", detailPanel).addEventListener("click", () => openTestModal(test));
  }

  /* ================= Модалка опыта (создание/редактирование) ================= */

  async function openTestModal(existing) {
    const isEdit = Boolean(existing);
    if (!state.objects.length) {
      toast("error", "Нет объектов", "Сначала создайте объект в разделе «Объекты»");
      switchView("objects");
      return;
    }
    if (!state.testTypes.length) {
      toast("error", "Нет типов испытаний", "Сначала создайте тип в разделе «Типы испытаний»");
      switchView("types");
      return;
    }
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">${isEdit ? "Редактирование опыта" : "Новый опыт"}</h3>
          <p class="modal__sub">${isEdit ? `ID ${esc(existing.test_id)}` : "протокол испытания"}</p>
        </div>
        <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal__body">
        <div class="form-row">
          <label class="field">
            <span class="field__label">Объект</span>
            <span class="combo" id="m-object-combo">
              <input type="text" class="field__input" id="m-object" placeholder="Начните вводить номер…"
                     autocomplete="off" spellcheck="false" role="combobox"
                     aria-expanded="false" aria-autocomplete="list" />
              <div class="combo__list" role="listbox" hidden></div>
            </span>
          </label>
          <label class="field">
            <span class="field__label">Скважина</span>
            <select class="field__select" id="m-borehole" disabled><option value="">— сначала объект —</option></select>
          </label>
        </div>
        <div class="form-row">
          <label class="field">
            <span class="field__label">Образец (лаб. номер)</span>
            <select class="field__select" id="m-sample" disabled><option value="">— сначала скважина —</option></select>
          </label>
          <label class="field">
            <span class="field__label">Тип испытания</span>
            <select class="field__select" id="m-type"><option value="">— выберите —</option></select>
          </label>
        </div>
        <div class="form-row">
          <label class="field">
            <span class="field__label">Дата и время опыта</span>
            <input type="datetime-local" class="field__input" id="m-timestamp" />
          </label>
          <label class="field">
            <span class="field__label">Описание</span>
            <input type="text" class="field__input" id="m-desc" placeholder="Необязательно" maxlength="500" />
          </label>
        </div>
        <div id="m-params"></div>
        <div id="m-results"></div>
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Отмена</button>
        <button type="button" class="btn btn--primary" id="m-save">${isEdit ? "Сохранить" : "Создать опыт"}</button>
      </div>`, { wide: true });
    if (!box) return;

    const mObject = $("#m-object", box);
    const mBorehole = $("#m-borehole", box);
    const mSample = $("#m-sample", box);
    const mType = $("#m-type", box);
    const mTimestamp = $("#m-timestamp", box);
    const mDesc = $("#m-desc", box);

    fillSelect(mType, state.testTypes, {
      value: (t) => t.test_type_id,
      text: (t) => t.test_type,
      placeholder: "— выберите —",
    });

    const paramsEditor = createKvEditor($("#m-params", box), existing ? existing.test_params : null, "Параметры опыта");
    const resultsEditor = createKvEditor($("#m-results", box), existing ? existing.test_results : null, "Результаты");

    const now = existing && existing.timestamp ? new Date(existing.timestamp) : new Date();
    const pad = (n) => String(n).padStart(2, "0");
    mTimestamp.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
    if (existing && existing.description) mDesc.value = existing.description;

    async function loadModalBoreholes(objectId, preselectName) {
      mBorehole.disabled = true;
      mSample.disabled = true;
      mSample.innerHTML = '<option value="">— сначала скважина —</option>';
      if (!objectId) { mBorehole.innerHTML = '<option value="">— сначала объект —</option>'; return; }
      try {
        const boreholes = await boreholesFor(objectId);
        fillSelect(mBorehole, boreholes, {
          value: (b) => b.borehole_id,
          text: (b) => b.borehole_name,
          placeholder: "— выберите —",
        });
        mBorehole.disabled = false;
        if (preselectName) {
          const found = boreholes.find((b) => b.borehole_name === preselectName);
          if (found) { mBorehole.value = found.borehole_id; await loadModalSamples(found.borehole_id, existing && existing.laboratory_number); }
        }
      } catch (_) {
        mBorehole.innerHTML = '<option value="">Скважин нет</option>';
      }
    }

    async function loadModalSamples(boreholeId, preselectLab) {
      mSample.disabled = true;
      if (!boreholeId) { mSample.innerHTML = '<option value="">— сначала скважина —</option>'; return; }
      try {
        const samples = await samplesFor(boreholeId);
        fillSelect(mSample, samples, {
          value: (s) => s.sample_id,
          text: (s) => `${s.laboratory_number} — ${s.soil_type}`,
          placeholder: "— выберите —",
        });
        mSample.disabled = false;
        if (preselectLab) {
          const found = samples.find((s) => s.laboratory_number === preselectLab);
          if (found) mSample.value = found.sample_id;
        }
      } catch (_) {
        mSample.innerHTML = '<option value="">Образцов нет</option>';
      }
    }

    const mObjectCombo = createObjectCombo({
      input: mObject,
      listEl: $("#m-object-combo .combo__list", box),
      clearBtn: null,
      onPick: (obj) => loadModalBoreholes(obj ? obj.object_id : ""),
    });
    mBorehole.addEventListener("change", () => loadModalSamples(mBorehole.value));

    if (isEdit) {
      const obj = state.objects.find((o) => o.object_number === existing.object_number);
      if (obj) {
        mObjectCombo.setValue(obj.object_number);
        await loadModalBoreholes(obj.object_id, existing.borehole_name);
      }
      const typeObj = state.testTypes.find((t) => t.test_type === existing.test_type);
      if (typeObj) mType.value = String(typeObj.test_type_id);
    }

    $("#m-save", box).addEventListener("click", async () => {
      const sampleId = mSample.value;
      const typeId = mType.value;
      [mSample, mType].forEach((el) => el.classList.remove("is-invalid"));
      if (!sampleId || !typeId) {
        if (!sampleId) mSample.classList.add("is-invalid");
        if (!typeId) mType.classList.add("is-invalid");
        toast("error", "Заполните поля", "Нужны образец и тип испытания");
        return;
      }
      const testParams = paramsEditor.getValue();
      const testResults = resultsEditor.getValue();
      if (testParams === undefined || testResults === undefined) return;

      // Наивное локальное время (без Z): бэкенд хранит DateTime без таймзоны,
      // а отображение парсит его как локальное — так время не «уплывает» на смещение пояса.
      const naiveTimestamp = mTimestamp.value
        ? `${mTimestamp.value}:00`
        : (() => {
            const d = new Date();
            return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:00`;
          })();

      const payload = {
        sample_id: sampleId,
        test_type_id: Number(typeId),
        timestamp: naiveTimestamp,
        // При редактировании шлём {} вместо null: PUT в бэке игнорирует None,
        // а {} после предварительной очистки означает «оставить пустым»
        test_params: isEdit ? (testParams || {}) : testParams,
        test_results: isEdit ? (testResults || {}) : testResults,
        // Пустая строка (а не null) — иначе PUT не сможет очистить описание
        description: isEdit ? mDesc.value.trim() : (mDesc.value.trim() || null),
      };

      const saveBtn = $("#m-save", box);
      saveBtn.disabled = true;
      try {
        if (isEdit) {
          await API.updateTest(existing.test_id, payload);
          toast("success", "Опыт обновлён", `ID ${existing.test_id}`);
        } else {
          await API.createTest(payload);
          toast("success", "Опыт создан");
        }
        closeModal();
        closeDetail();
        loadTests();
      } catch (err) {
        showError(err, "Не удалось сохранить опыт");
        saveBtn.disabled = false;
      }
    });
  }

  $("#btn-new-test").addEventListener("click", () => openTestModal(null));

  /* ================= ВИД: ОБЪЕКТЫ ================= */

  const objEls = {
    list: $("#objects-list"),
    count: $("#objects-count"),
    empty: $("#objects-empty"),
    search: $("#objects-search"),
    bhList: $("#boreholes-list"),
    bhCount: $("#boreholes-count"),
    bhEmpty: $("#boreholes-empty"),
    bhLoading: $("#boreholes-loading"),
    bhAdd: $("#btn-new-borehole"),
    smList: $("#samples-list"),
    smCount: $("#samples-count"),
    smEmpty: $("#samples-empty"),
    smLoading: $("#samples-loading"),
    smAdd: $("#btn-new-sample"),
  };

  function highlight(text, q) {
    const safe = esc(text);
    if (!q) return safe;
    const idx = String(text ?? "").toLowerCase().indexOf(q);
    if (idx === -1) return safe;
    const source = String(text ?? "");
    return esc(source.slice(0, idx)) + '<mark class="hl">' + esc(source.slice(idx, idx + q.length)) + "</mark>" + esc(source.slice(idx + q.length));
  }

  function renderObjectsList() {
    const q = (objEls.search.value || "").trim().toLowerCase();
    const filtered = state.objects
      .filter((o) => !q || [o.object_number, o.description, o.object_id]
        .some((v) => String(v ?? "").toLowerCase().includes(q)))
      .sort((a, b) => String(a.object_number).localeCompare(String(b.object_number), "ru", { numeric: true }));

    objEls.count.textContent = String(filtered.length);
    objEls.list.innerHTML = "";
    objEls.empty.hidden = filtered.length > 0;
    objEls.empty.textContent = state.objects.length ? "Ничего не найдено" : "Объектов пока нет";

    const fragment = document.createDocumentFragment();
    filtered.forEach((obj) => {
      const li = document.createElement("li");
      const active = obj.object_id === state.selectedObjectId;
      li.innerHTML = `
        <button type="button" class="entity-item ${active ? "is-active" : ""}">
          <span class="entity-item__row">
            <span class="entity-item__primary">${highlight(obj.object_number, q)}</span>
            <span class="icon-btn" data-edit title="Редактировать объект" aria-label="Редактировать объект">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
            </span>
          </span>
          <span class="entity-item__secondary">${highlight(obj.description || "Без описания", q)}</span>
          <span class="entity-item__meta"><span>ID ${highlight(obj.object_id, q)}</span></span>
        </button>`;
      const btn = $("button", li);
      btn.addEventListener("click", (event) => {
        if (event.target.closest("[data-edit]")) { openObjectModal(obj); return; }
        selectObject(obj);
      });
      fragment.appendChild(li);
    });
    objEls.list.appendChild(fragment);
  }

  async function selectObject(obj, { force = false } = {}) {
    state.selectedObjectId = obj.object_id;
    state.selectedBoreholeId = null;
    renderObjectsList();
    objEls.bhAdd.disabled = false;
    objEls.smAdd.disabled = true;
    objEls.smList.innerHTML = "";
    objEls.smCount.textContent = "0";
    objEls.smEmpty.hidden = false;
    objEls.smEmpty.textContent = "Выберите скважину";

    objEls.bhLoading.hidden = false;
    objEls.bhEmpty.hidden = true;
    objEls.bhList.innerHTML = "";
    try {
      const boreholes = await boreholesFor(obj.object_id, force);
      renderBoreholesList(boreholes);
    } catch (err) {
      showError(err, "Не удалось загрузить скважины");
    } finally {
      objEls.bhLoading.hidden = true;
    }
  }

  function renderBoreholesList(boreholes) {
    objEls.bhCount.textContent = String(boreholes.length);
    objEls.bhList.innerHTML = "";
    objEls.bhEmpty.hidden = boreholes.length > 0;
    objEls.bhEmpty.textContent = "Скважин нет — добавьте первую";

    const fragment = document.createDocumentFragment();
    boreholes
      .slice()
      .sort((a, b) => String(a.borehole_name).localeCompare(String(b.borehole_name), "ru", { numeric: true }))
      .forEach((bh) => {
        const li = document.createElement("li");
        const active = bh.borehole_id === state.selectedBoreholeId;
        li.innerHTML = `
          <button type="button" class="entity-item ${active ? "is-active" : ""}">
            <span class="entity-item__row">
              <span class="entity-item__primary">${esc(bh.borehole_name)}</span>
              <span style="display:inline-flex; gap:.3rem;">
                <span class="icon-btn" data-edit title="Редактировать скважину" aria-label="Редактировать скважину">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
                </span>
                <span class="icon-btn icon-btn--danger" data-del title="Удалить скважину" aria-label="Удалить скважину">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
                </span>
              </span>
            </span>
            ${bh.description ? `<span class="entity-item__secondary">${esc(bh.description)}</span>` : ""}
          </button>`;
        const btn = $("button", li);
        btn.addEventListener("click", async (event) => {
          if (event.target.closest("[data-edit]")) { openBoreholeModal(bh); return; }
          if (event.target.closest("[data-del]")) {
            const ok = await confirmDialog({
              title: "Удалить скважину?",
              text: `Скважина <b>${esc(bh.borehole_name)}</b> будет удалена. Удаление возможно только если в ней нет образцов.`,
            });
            if (!ok) return;
            try {
              await API.deleteBorehole(bh.borehole_id);
              toast("success", "Скважина удалена", bh.borehole_name);
              const list = (state.boreholesByObject.get(bh.object_id) || []).filter((b) => b.borehole_id !== bh.borehole_id);
              state.boreholesByObject.set(bh.object_id, list);
              state.samplesByBorehole.delete(bh.borehole_id);
              if (state.selectedBoreholeId === bh.borehole_id) {
                state.selectedBoreholeId = null;
                objEls.smAdd.disabled = true;
                objEls.smList.innerHTML = "";
                objEls.smCount.textContent = "0";
                objEls.smEmpty.hidden = false;
                objEls.smEmpty.textContent = "Выберите скважину";
              }
              renderBoreholesList(list);
            } catch (err) { showError(err, "Нельзя удалить скважину"); }
            return;
          }
          selectBorehole(bh);
        });
        fragment.appendChild(li);
      });
    objEls.bhList.appendChild(fragment);
  }

  async function selectBorehole(bh, { force = false } = {}) {
    state.selectedBoreholeId = bh.borehole_id;
    const cached = state.boreholesByObject.get(state.selectedObjectId) || [];
    renderBoreholesList(cached);
    objEls.smAdd.disabled = false;

    objEls.smLoading.hidden = false;
    objEls.smEmpty.hidden = true;
    objEls.smList.innerHTML = "";
    try {
      const samples = await samplesFor(bh.borehole_id, force);
      renderSamplesList(samples);
    } catch (err) {
      showError(err, "Не удалось загрузить образцы");
    } finally {
      objEls.smLoading.hidden = true;
    }
  }

  function renderSamplesList(samples) {
    objEls.smCount.textContent = String(samples.length);
    objEls.smList.innerHTML = "";
    objEls.smEmpty.hidden = samples.length > 0;
    objEls.smEmpty.textContent = "Образцов нет — добавьте первый";

    const fragment = document.createDocumentFragment();
    samples
      .slice()
      .sort((a, b) => String(a.laboratory_number).localeCompare(String(b.laboratory_number), "ru", { numeric: true }))
      .forEach((sample) => {
        const propsCount = sample.properties && typeof sample.properties === "object" && !Array.isArray(sample.properties)
          ? Object.keys(sample.properties).length
          : 0;
        const li = document.createElement("li");
        li.innerHTML = `
          <button type="button" class="entity-item">
            <span class="entity-item__row">
              <span class="entity-item__primary">л/н ${esc(sample.laboratory_number)}</span>
              <span style="display:inline-flex; gap:.3rem;">
                <span class="icon-btn" data-edit title="Редактировать образец" aria-label="Редактировать образец">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
                </span>
                <span class="icon-btn icon-btn--danger" data-del title="Удалить образец" aria-label="Удалить образец">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
                </span>
              </span>
            </span>
            <span class="entity-item__secondary">${esc(sample.soil_type ?? "—")}</span>
            <span class="entity-item__meta">
              ${propsCount ? `<span>${propsCount} свойств</span>` : ""}
              ${sample.description ? `<span>${esc(sample.description)}</span>` : ""}
            </span>
          </button>`;
        const btn = $("button", li);
        btn.addEventListener("click", async (event) => {
          if (event.target.closest("[data-edit]")) { openSampleModal(sample); return; }
          if (event.target.closest("[data-del]")) {
            const ok = await confirmDialog({
              title: "Удалить образец?",
              text: `Образец <b>л/н ${esc(sample.laboratory_number)}</b> будет удалён. Удаление возможно только если по нему нет опытов.`,
            });
            if (!ok) return;
            try {
              await API.deleteSample(sample.sample_id);
              toast("success", "Образец удалён", `л/н ${sample.laboratory_number}`);
              const list = (state.samplesByBorehole.get(sample.borehole_id) || []).filter((s) => s.sample_id !== sample.sample_id);
              state.samplesByBorehole.set(sample.borehole_id, list);
              renderSamplesList(list);
            } catch (err) { showError(err, "Нельзя удалить образец"); }
            return;
          }
          openSampleView(sample);
        });
        fragment.appendChild(li);
      });
    objEls.smList.appendChild(fragment);
  }

  function openSampleView(sample) {
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">Образец · л/н ${esc(sample.laboratory_number)}</h3>
          <p class="modal__sub">ID ${esc(sample.sample_id)}</p>
        </div>
        <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal__body">
        <dl class="kv-list">
          <dt>Грунт</dt><dd>${esc(sample.soil_type ?? "—")}</dd>
          ${sample.description ? `<dt>Описание</dt><dd>${esc(sample.description)}</dd>` : ""}
        </dl>
        <div>
          <p class="field__label" style="margin-bottom:.5rem;">Свойства образца</p>
          ${kvListHtml(sample.properties)}
        </div>
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Закрыть</button>
        <button type="button" class="btn btn--primary" id="sv-edit">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
          Редактировать
        </button>
      </div>`);
    if (!box) return;
    $("#sv-edit", box).addEventListener("click", () => {
      closeModal();
      openSampleModal(sample);
    });
  }

  objEls.search.addEventListener("input", debounce(renderObjectsList, 150));

  /* --- модалка объекта --- */

  function openObjectModal(existing) {
    const isEdit = Boolean(existing);
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">${isEdit ? "Редактирование объекта" : "Новый объект"}</h3>
          <p class="modal__sub">${isEdit ? `ID ${esc(existing.object_id)}` : "строительный объект"}</p>
        </div>
        <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal__body">
        <label class="field">
          <span class="field__label">Номер объекта</span>
          <input type="text" class="field__input" id="o-number" maxlength="10" placeholder="Например: 705-32" value="${isEdit ? esc(existing.object_number) : ""}" />
          <span class="field__hint">До 10 символов, уникальный</span>
        </label>
        <label class="field">
          <span class="field__label">Описание</span>
          <textarea class="field__textarea" id="o-desc" maxlength="500" placeholder="Адрес, название, примечания…">${isEdit ? esc(existing.description || "") : ""}</textarea>
        </label>
        ${isEdit ? "" : `
        <label class="field">
          <span class="field__label">ID (EngGeo)</span>
          <input type="text" class="field__input field__input--mono" id="o-id" maxlength="32" value="${genId()}" />
          <span class="field__hint">32 символа; сгенерирован автоматически — замените на ID из EngGeo при необходимости</span>
        </label>`}
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Отмена</button>
        <button type="button" class="btn btn--primary" id="o-save">${isEdit ? "Сохранить" : "Создать объект"}</button>
      </div>`);
    if (!box) return;

    $("#o-save", box).addEventListener("click", async () => {
      const numberInput = $("#o-number", box);
      const objectNumber = numberInput.value.trim();
      numberInput.classList.remove("is-invalid");
      if (!objectNumber) { numberInput.classList.add("is-invalid"); return; }
      const description = $("#o-desc", box).value.trim() || null;
      const saveBtn = $("#o-save", box);
      saveBtn.disabled = true;
      try {
        const objectId = isEdit
          ? existing.object_id
          : ($("#o-id", box).value.trim() || genId()).slice(0, 32);
        const saved = { object_id: objectId, object_number: objectNumber, description };
        await API.saveObject(saved);
        toast("success", isEdit ? "Объект обновлён" : "Объект создан", objectNumber);
        closeModal();
        // Обновляем локальное состояние сразу — серверный кеш (60 c) может отдать старый список
        const idx = state.objects.findIndex((o) => o.object_id === objectId);
        if (idx === -1) state.objects.push(saved);
        else state.objects[idx] = saved;
        renderObjectsList();
        refreshFilterSelects();
        countUp($("#stat-objects"), state.objects.length);
        setTabCount("objects", state.objects.length);
      } catch (err) {
        showError(err, "Не удалось сохранить объект");
        saveBtn.disabled = false;
      }
    });
  }

  $("#btn-new-object").addEventListener("click", () => openObjectModal(null));

  /* --- модалка скважины --- */

  function openBoreholeModal(existing) {
    const isEdit = Boolean(existing);
    const obj = state.objects.find((o) => o.object_id === state.selectedObjectId);
    if (!obj) return;
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">${isEdit ? "Редактирование скважины" : "Новая скважина"}</h3>
          <p class="modal__sub">объект ${esc(obj.object_number)}</p>
        </div>
        <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal__body">
        <label class="field">
          <span class="field__label">Наименование скважины</span>
          <input type="text" class="field__input" id="b-name" maxlength="50" placeholder="Например: С-14" value="${isEdit ? esc(existing.borehole_name) : ""}" />
        </label>
        <label class="field">
          <span class="field__label">Описание</span>
          <textarea class="field__textarea" id="b-desc" maxlength="500" placeholder="Необязательно">${isEdit ? esc(existing.description || "") : ""}</textarea>
        </label>
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Отмена</button>
        <button type="button" class="btn btn--primary" id="b-save">${isEdit ? "Сохранить" : "Создать скважину"}</button>
      </div>`);
    if (!box) return;

    $("#b-save", box).addEventListener("click", async () => {
      const nameInput = $("#b-name", box);
      const boreholeName = nameInput.value.trim();
      nameInput.classList.remove("is-invalid");
      if (!boreholeName) { nameInput.classList.add("is-invalid"); return; }
      const saveBtn = $("#b-save", box);
      saveBtn.disabled = true;
      try {
        const saved = {
          borehole_id: isEdit ? existing.borehole_id : genId(),
          borehole_name: boreholeName,
          object_id: obj.object_id,
          description: $("#b-desc", box).value.trim() || null,
        };
        await API.saveBoreholes([saved]);
        toast("success", isEdit ? "Скважина обновлена" : "Скважина создана", boreholeName);
        closeModal();
        // Локальное обновление кеша — не зависим от серверного кеша списков
        const list = state.boreholesByObject.get(obj.object_id) || [];
        const idx = list.findIndex((b) => b.borehole_id === saved.borehole_id);
        if (idx === -1) list.push(saved);
        else list[idx] = saved;
        state.boreholesByObject.set(obj.object_id, list);
        renderBoreholesList(list);
      } catch (err) {
        showError(err, "Не удалось сохранить скважину");
        saveBtn.disabled = false;
      }
    });
  }

  objEls.bhAdd.addEventListener("click", () => openBoreholeModal(null));

  /* --- модалка образца --- */

  function openSampleModal(existing) {
    const isEdit = Boolean(existing);
    const boreholeId = isEdit ? existing.borehole_id : state.selectedBoreholeId;
    const bh = (state.boreholesByObject.get(state.selectedObjectId) || [])
      .find((b) => b.borehole_id === boreholeId);
    if (!bh) return;
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">${isEdit ? "Редактирование образца" : "Новый образец"}</h3>
          <p class="modal__sub">скважина ${esc(bh.borehole_name)}</p>
        </div>
        <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal__body">
        <div class="form-row">
          <label class="field">
            <span class="field__label">Лабораторный номер</span>
            <input type="text" class="field__input" id="s-lab" maxlength="50" placeholder="Например: 1234-21" value="${isEdit ? esc(existing.laboratory_number) : ""}" />
          </label>
          <label class="field">
            <span class="field__label">Тип грунта</span>
            <input type="text" class="field__input" id="s-soil" maxlength="500" placeholder="Например: суглинок тугопластичный" value="${isEdit ? esc(existing.soil_type) : ""}" />
          </label>
        </div>
        <label class="field">
          <span class="field__label">Описание</span>
          <input type="text" class="field__input" id="s-desc" maxlength="500" placeholder="Необязательно" value="${isEdit ? esc(existing.description || "") : ""}" />
        </label>
        <div id="s-props"></div>
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Отмена</button>
        <button type="button" class="btn btn--primary" id="s-save">${isEdit ? "Сохранить" : "Создать образец"}</button>
      </div>`, { wide: true });
    if (!box) return;

    const propsEditor = createKvEditor($("#s-props", box), isEdit ? existing.properties : null, "Свойства (глубина, влажность…)");

    $("#s-save", box).addEventListener("click", async () => {
      const labInput = $("#s-lab", box);
      const soilInput = $("#s-soil", box);
      [labInput, soilInput].forEach((el) => el.classList.remove("is-invalid"));
      const laboratoryNumber = labInput.value.trim();
      const soilType = soilInput.value.trim();
      if (!laboratoryNumber || !soilType) {
        if (!laboratoryNumber) labInput.classList.add("is-invalid");
        if (!soilType) soilInput.classList.add("is-invalid");
        return;
      }
      const properties = propsEditor.getValue();
      if (properties === undefined) return;
      const saveBtn = $("#s-save", box);
      saveBtn.disabled = true;
      try {
        const saved = {
          sample_id: isEdit ? existing.sample_id : genId(),
          borehole_id: bh.borehole_id,
          laboratory_number: laboratoryNumber,
          soil_type: soilType,
          properties,
          description: $("#s-desc", box).value.trim() || null,
        };
        await API.saveSamples([saved]);
        toast("success", isEdit ? "Образец обновлён" : "Образец создан", `л/н ${laboratoryNumber}`);
        closeModal();
        // Локальное обновление кеша — не зависим от серверного кеша списков
        const list = state.samplesByBorehole.get(bh.borehole_id) || [];
        const idx = list.findIndex((s) => s.sample_id === saved.sample_id);
        if (idx === -1) list.push(saved);
        else list[idx] = saved;
        state.samplesByBorehole.set(bh.borehole_id, list);
        if (state.selectedBoreholeId === bh.borehole_id) renderSamplesList(list);
      } catch (err) {
        showError(err, "Не удалось сохранить образец");
        saveBtn.disabled = false;
      }
    });
  }

  objEls.smAdd.addEventListener("click", () => openSampleModal(null));

  /* ================= ВИД: ТИПЫ ИСПЫТАНИЙ ================= */

  const typesEls = {
    tbody: $("#types-tbody"),
    table: $("#types-table"),
    count: $("#types-count"),
    empty: $("#types-empty"),
    loading: $("#types-loading"),
  };

  function renderTypes() {
    typesEls.count.textContent = String(state.testTypes.length);
    typesEls.tbody.innerHTML = "";
    typesEls.empty.hidden = state.testTypes.length > 0;
    typesEls.table.hidden = state.testTypes.length === 0;

    const fragment = document.createDocumentFragment();
    state.testTypes
      .slice()
      .sort((a, b) => String(a.test_type).localeCompare(String(b.test_type), "ru"))
      .forEach((type) => {
        const tr = document.createElement("tr");
        tr.style.cursor = "default";
        tr.innerHTML = `
          <td class="mono" data-th="ID">${esc(type.test_type_id)}</td>
          <td data-th="Тип"><b>${esc(type.test_type)}</b></td>
          <td data-th="Описание">${esc(type.description || "—")}</td>
          <td class="num"><span class="row-actions">
            <button type="button" class="icon-btn" data-edit aria-label="Редактировать тип" title="Редактировать">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
            </button>
            <button type="button" class="icon-btn icon-btn--danger" data-del aria-label="Удалить тип" title="Удалить">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
            </button>
          </span></td>`;
        $("[data-edit]", tr).addEventListener("click", () => openTypeModal(type));
        $("[data-del]", tr).addEventListener("click", async () => {
          const ok = await confirmDialog({
            title: "Удалить тип испытания?",
            text: `Тип <b>${esc(type.test_type)}</b> будет удалён. Если по нему есть опыты, база не позволит удаление.`,
          });
          if (!ok) return;
          try {
            await API.deleteTestType(type.test_type_id);
            toast("success", "Тип удалён", type.test_type);
            await reloadTypes();
          } catch (err) { showError(err, "Нельзя удалить тип"); }
        });
        fragment.appendChild(tr);
      });
    typesEls.tbody.appendChild(fragment);
  }

  function openTypeModal(existing) {
    const isEdit = Boolean(existing);
    const box = openModal(`
      <div class="modal__head">
        <div>
          <h3 class="modal__title">${isEdit ? "Редактирование типа" : "Новый тип испытания"}</h3>
          <p class="modal__sub">${isEdit ? `ID ${esc(existing.test_type_id)}` : "справочник"}</p>
        </div>
        <button type="button" class="icon-btn" data-close-modal aria-label="Закрыть">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal__body">
        <label class="field">
          <span class="field__label">Тип испытания</span>
          <input type="text" class="field__input" id="t-name" maxlength="500" placeholder="Например: Трёхосное сжатие КД" value="${isEdit ? esc(existing.test_type) : ""}" />
        </label>
        <label class="field">
          <span class="field__label">Описание</span>
          <textarea class="field__textarea" id="t-desc" maxlength="500" placeholder="ГОСТ, методика, примечания…">${isEdit ? esc(existing.description || "") : ""}</textarea>
        </label>
      </div>
      <div class="modal__foot">
        <button type="button" class="btn btn--ghost" data-close-modal>Отмена</button>
        <button type="button" class="btn btn--primary" id="t-save">${isEdit ? "Сохранить" : "Создать тип"}</button>
      </div>`);
    if (!box) return;

    $("#t-save", box).addEventListener("click", async () => {
      const nameInput = $("#t-name", box);
      const testType = nameInput.value.trim();
      nameInput.classList.remove("is-invalid");
      if (!testType) { nameInput.classList.add("is-invalid"); return; }
      const payload = { test_type: testType, description: $("#t-desc", box).value.trim() || null };
      const saveBtn = $("#t-save", box);
      saveBtn.disabled = true;
      try {
        if (isEdit) {
          await API.updateTestType(existing.test_type_id, payload);
          toast("success", "Тип обновлён", testType);
        } else {
          await API.createTestType(payload);
          toast("success", "Тип создан", testType);
        }
        closeModal();
        await reloadTypes();
      } catch (err) {
        showError(err, "Не удалось сохранить тип");
        saveBtn.disabled = false;
      }
    });
  }

  $("#btn-new-type").addEventListener("click", () => openTypeModal(null));

  /* ================= Загрузка справочников ================= */

  async function reloadObjects() {
    try {
      state.objects = await API.getObjects();
    } catch (_) { /* оставим как есть */ }
    renderObjectsList();
    refreshFilterSelects();
    countUp($("#stat-objects"), state.objects.length);
    setTabCount("objects", state.objects.length);
  }

  async function reloadTypes() {
    typesEls.loading.hidden = false;
    try {
      state.testTypes = await API.getTestTypes();
    } catch (err) {
      showError(err, "Не удалось загрузить типы испытаний");
    } finally {
      typesEls.loading.hidden = true;
    }
    renderTypes();
    refreshFilterSelects();
    countUp($("#stat-types"), state.testTypes.length);
    setTabCount("types", state.testTypes.length);
  }

  /* ================= Старт ================= */

  state.objects = initialObjects();
  renderObjectsList();
  refreshFilterSelects();
  countUp($("#stat-objects"), state.objects.length);

  reloadObjects();
  reloadTypes();
  loadTests();
})();
