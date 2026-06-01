(function () {
  const dashboard = document.getElementById("dashboard");
  if (!dashboard) return;

  const els = {
    objectsList: document.getElementById("objects-list"),
    objectsCount: document.getElementById("objects-count"),
    objectsEmpty: document.getElementById("objects-empty"),
    objectsSearch: document.getElementById("objects-search"),
    objectsSort: document.getElementById("objects-sort"),

    testsList: document.getElementById("tests-list"),
    testsCount: document.getElementById("tests-count"),
    testsEmpty: document.getElementById("tests-empty"),
    testsHint: document.getElementById("tests-hint"),
    testsLoading: document.getElementById("tests-loading"),
    testsSubtitle: document.getElementById("tests-subtitle"),
    testsSearch: document.getElementById("tests-search"),
    testsSort: document.getElementById("tests-sort"),

    detailContent: document.getElementById("detail-content"),
    detailHint: document.getElementById("detail-hint"),
    detailSubtitle: document.getElementById("detail-subtitle"),
    paramsList: document.getElementById("params-list"),
    resultsList: document.getElementById("results-list"),
    filesList: document.getElementById("files-list"),
    filesEmpty: document.getElementById("files-empty"),
    filesLoading: document.getElementById("files-loading"),
  };

  let objectsData = [];
  let testsData = [];
  let selectedObjectNumber = null;
  let selectedTestId = null;
  let testsFetchToken = 0;

  function loadObjectsData() {
    const node = document.getElementById("objects-data");
    if (!node) return [];
    try {
      const parsed = JSON.parse(node.textContent);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function debounce(fn, ms) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  function normalizeQuery(q) {
    return q.trim().toLowerCase();
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function highlightText(text, query) {
    const safe = escapeHtml(text);
    if (!query) return safe;
    const idx = String(text).toLowerCase().indexOf(query);
    if (idx === -1) return safe;
    const before = escapeHtml(String(text).slice(0, idx));
    const match = escapeHtml(String(text).slice(idx, idx + query.length));
    const after = escapeHtml(String(text).slice(idx + query.length));
    return `${before}<mark class="highlight">${match}</mark>${after}`;
  }

  function filterObjects(items, query) {
    const q = normalizeQuery(query);
    if (!q) return items;
    return items.filter((o) =>
      [o.object_number, o.description, o.object_id].some((v) =>
        String(v ?? "")
          .toLowerCase()
          .includes(q)
      )
    );
  }

  function sortObjects(items, mode) {
    const copy = [...items];
    const cmpStr = (a, b) => String(a).localeCompare(String(b), "ru", { numeric: true });
    switch (mode) {
      case "number-desc":
        return copy.sort((a, b) => cmpStr(b.object_number, a.object_number));
      case "desc-asc":
        return copy.sort((a, b) => cmpStr(a.description || "", b.description || ""));
      case "desc-desc":
        return copy.sort((a, b) => cmpStr(b.description || "", a.description || ""));
      case "number-asc":
      default:
        return copy.sort((a, b) => cmpStr(a.object_number, b.object_number));
    }
  }

  function filterTests(items, query) {
    const q = normalizeQuery(query);
    if (!q) return items;
    return items.filter((t) => {
      const dateStr = t.timestamp ? new Date(t.timestamp).toLocaleDateString("ru-RU") : "";
      return [
        t.test_id,
        t.borehole_name,
        t.laboratory_number,
        t.test_type,
        t.soil_type,
        dateStr,
      ].some((v) =>
        String(v ?? "")
          .toLowerCase()
          .includes(q)
      );
    });
  }

  function sortTests(items, mode) {
    const copy = [...items];
    const cmpStr = (a, b) => String(a).localeCompare(String(b), "ru", { numeric: true });
    switch (mode) {
      case "date-asc":
        return copy.sort(
          (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
      case "type-asc":
        return copy.sort((a, b) => cmpStr(a.test_type, b.test_type));
      case "lab-asc":
        return copy.sort((a, b) => cmpStr(a.laboratory_number, b.laboratory_number));
      case "date-desc":
      default:
        return copy.sort(
          (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
    }
  }

  function renderObjects() {
    const query = els.objectsSearch?.value || "";
    const sortMode = els.objectsSort?.value || "number-asc";
    const filtered = sortObjects(filterObjects(objectsData, query), sortMode);
    const q = normalizeQuery(query);

    els.objectsCount.textContent = filtered.length;
    els.objectsList.innerHTML = "";

    if (filtered.length === 0) {
      els.objectsEmpty.hidden = objectsData.length > 0 ? false : true;
      if (objectsData.length === 0) {
        els.objectsEmpty.textContent = "Объектов нет";
      } else {
        els.objectsEmpty.textContent = "Ничего не найдено";
      }
      return;
    }

    els.objectsEmpty.hidden = true;

    const fragment = document.createDocumentFragment();
    filtered.forEach((obj) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "entity-item";
      btn.dataset.id = obj.object_number;
      btn.setAttribute("role", "option");
      if (obj.object_number === selectedObjectNumber) {
        btn.classList.add("is-active");
      }

      btn.innerHTML = `
        <div class="entity-item__primary">${highlightText(obj.object_number, q)}</div>
        <div class="entity-item__secondary">${highlightText(obj.description || "—", q)}</div>
        <div class="entity-item__meta">
          <span class="entity-item__tag">ID: ${highlightText(obj.object_id, q)}</span>
        </div>
      `;

      btn.addEventListener("click", () => selectObject(obj.object_number));
      li.appendChild(btn);
      fragment.appendChild(li);
    });

    els.objectsList.appendChild(fragment);
  }

  function setLoading(el, isLoading) {
    if (!el) return;
    el.hidden = !isLoading;
  }

  function renderTests() {
    const query = els.testsSearch?.value || "";
    const sortMode = els.testsSort?.value || "date-desc";
    const filtered = sortTests(filterTests(testsData, query), sortMode);
    const q = normalizeQuery(query);

    els.testsCount.textContent = filtered.length;
    els.testsList.innerHTML = "";

    if (!selectedObjectNumber) {
      els.testsHint.hidden = false;
      els.testsEmpty.hidden = true;
      return;
    }

    els.testsHint.hidden = true;

    if (filtered.length === 0) {
      els.testsEmpty.hidden = testsData.length > 0 ? false : true;
      els.testsEmpty.textContent =
        testsData.length > 0 ? "Ничего не найдено" : "Нет опытов по выбранному объекту";
      return;
    }

    els.testsEmpty.hidden = true;

    const fragment = document.createDocumentFragment();
    filtered.forEach((test) => {
      const dateStr = test.timestamp
        ? new Date(test.timestamp).toLocaleDateString("ru-RU", {
            day: "2-digit",
            month: "short",
            year: "numeric",
          })
        : "—";

      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "entity-item";
      btn.dataset.id = String(test.test_id);
      btn.setAttribute("role", "option");
      if (test.test_id === selectedTestId) {
        btn.classList.add("is-active");
      }

      btn.innerHTML = `
        <div class="entity-item__primary">${highlightText(test.test_type, q)} · ${highlightText(test.laboratory_number, q)}</div>
        <div class="entity-item__secondary">Скважина: ${highlightText(test.borehole_name, q)}</div>
        <div class="entity-item__meta">
          <span class="entity-item__tag">ID ${highlightText(String(test.test_id), q)}</span>
          <span class="entity-item__tag">${escapeHtml(dateStr)}</span>
        </div>
      `;

      btn.addEventListener("click", () => selectTest(test));
      li.appendChild(btn);
      fragment.appendChild(li);
    });

    els.testsList.appendChild(fragment);
  }

  function clearDetail() {
    selectedTestId = null;
    els.detailContent.hidden = true;
    els.detailHint.hidden = false;
    els.detailSubtitle.textContent = "Выберите опыт";
    els.paramsList.innerHTML = "";
    els.resultsList.innerHTML = "";
    els.filesList.innerHTML = "";
    els.filesEmpty.hidden = true;
    setLoading(els.filesLoading, false);
  }

  function fillKvList(container, data) {
    container.innerHTML = "";
    if (!data || typeof data !== "object" || Object.keys(data).length === 0) {
      const dt = document.createElement("dt");
      dt.textContent = "—";
      const dd = document.createElement("dd");
      dd.textContent = "Нет данных";
      container.append(dt, dd);
      return;
    }
    Object.entries(data).forEach(([key, value]) => {
      const dt = document.createElement("dt");
      dt.textContent = key;
      const dd = document.createElement("dd");
      dd.textContent = value == null ? "—" : String(value);
      container.append(dt, dd);
    });
  }

  function renderFiles(files) {
    setLoading(els.filesLoading, false);
    els.filesList.innerHTML = "";
    els.filesEmpty.textContent = "Файлов нет";

    if (!files || files.length === 0) {
      els.filesEmpty.hidden = false;
      return;
    }

    els.filesEmpty.hidden = true;
    const fragment = document.createDocumentFragment();

    files.forEach((file) => {
      const li = document.createElement("li");
      li.className = "file-list__item";
      const key = escapeHtml(file.key);
      const desc = escapeHtml(file.description || "");
      li.innerHTML = `
        <span class="file-list__icon" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
        </span>
        <div>
          <a class="file-list__link" target="_blank" rel="noopener" href="./s3/?key=${encodeURIComponent(file.key)}">${key}</a>
          ${desc ? `<div class="file-list__desc">${desc}</div>` : ""}
        </div>
      `;
      fragment.appendChild(li);
    });

    els.filesList.appendChild(fragment);
  }

  function selectTest(test) {
    selectedTestId = test.test_id;
    renderTests();

    els.detailHint.hidden = true;
    els.detailContent.hidden = false;
    els.detailSubtitle.textContent = `${test.test_type} · л/н ${test.laboratory_number} · ID ${test.test_id}`;

    fillKvList(els.paramsList, test.test_params);
    fillKvList(els.resultsList, test.test_results);

    els.filesList.innerHTML = "";
    els.filesEmpty.hidden = true;
    setLoading(els.filesLoading, true);

    const filesToken = test.test_id;
    fetchTestFiles(test.test_id)
      .then((files) => {
        if (selectedTestId !== filesToken) return;
        renderFiles(files);
      })
      .catch(() => {
        if (selectedTestId !== filesToken) return;
        setLoading(els.filesLoading, false);
        els.filesEmpty.hidden = false;
        els.filesEmpty.textContent = "Не удалось загрузить файлы";
      });
  }

  function setTestsToolbarEnabled(enabled) {
    els.testsSearch.disabled = !enabled;
    els.testsSort.disabled = !enabled;
  }

  function selectObject(objectNumber) {
    selectedObjectNumber = objectNumber;
    selectedTestId = null;
    testsData = [];
    els.testsSearch.value = "";
    clearDetail();
    renderObjects();

    const obj = objectsData.find((o) => o.object_number === objectNumber);
    els.testsSubtitle.textContent = obj
      ? `Объект ${obj.object_number}${obj.description ? ` — ${obj.description}` : ""}`
      : `Объект ${objectNumber}`;

    setTestsToolbarEnabled(true);
    setLoading(els.testsLoading, true);
    els.testsHint.hidden = true;
    els.testsEmpty.hidden = true;
    els.testsList.innerHTML = "";

    const token = ++testsFetchToken;

    fetchTests(objectNumber)
      .then((data) => {
        if (token !== testsFetchToken) return;
        testsData = Array.isArray(data) ? data : [];
        renderTests();
      })
      .catch(() => {
        if (token !== testsFetchToken) return;
        testsData = [];
        els.testsEmpty.hidden = false;
        els.testsEmpty.textContent = "Ошибка загрузки опытов";
      })
      .finally(() => {
        if (token !== testsFetchToken) return;
        setLoading(els.testsLoading, false);
      });
  }

  objectsData = loadObjectsData();
  renderObjects();

  els.objectsSearch?.addEventListener(
    "input",
    debounce(() => renderObjects(), 150)
  );
  els.objectsSort?.addEventListener("change", () => renderObjects());

  els.testsSearch?.addEventListener(
    "input",
    debounce(() => renderTests(), 150)
  );
  els.testsSort?.addEventListener("change", () => renderTests());

  setTestsToolbarEnabled(false);
})();
