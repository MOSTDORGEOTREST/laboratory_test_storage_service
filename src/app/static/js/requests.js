/* ============================================================
   MDGT · LTS — API-клиент (все запросы к бэкенду)
   ============================================================ */

const API = (() => {
  const JSON_HEADERS = {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
  };

  // Токен истёк/невалиден: чистим куку и уходим на страницу входа.
  // Без signOut сервер снова отрендерит кабинет (он проверяет только наличие куки)
  // и страница зациклится на перезагрузках.
  let redirecting = false;
  function handleUnauthorized() {
    if (redirecting) return;
    redirecting = true;
    fetch("./auth/sign-out/", { method: "GET", credentials: "include" })
      .catch(() => {})
      .finally(() => { window.location.href = "./"; });
  }

  async function parseError(response) {
    let message = `Ошибка ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      }
    } catch (_) { /* тело не JSON */ }
    const err = new Error(message);
    err.status = response.status;
    return err;
  }

  async function request(path, { method = "GET", body, emptyOn404 = false } = {}) {
    const opts = {
      method,
      credentials: "include",
      headers: { Accept: "application/json", "X-Requested-With": "XMLHttpRequest" },
    };
    if (body !== undefined) {
      opts.headers = { ...JSON_HEADERS };
      opts.body = JSON.stringify(body);
    }
    const response = await fetch(path, opts);

    if (response.status === 401) {
      handleUnauthorized();
      throw Object.assign(new Error("Сессия истекла, выполняется выход…"), { status: 401 });
    }
    if (response.status === 404 && emptyOn404) return [];
    if (!response.ok) throw await parseError(response);
    if (response.status === 204) return null;
    try { return await response.json(); } catch (_) { return null; }
  }

  return {
    /* ---------- Авторизация ---------- */
    signIn(username, password) {
      return fetch("./auth/sign-in/", {
        method: "POST",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: `grant_type=password&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
      });
    },
    signOut() {
      return fetch("./auth/sign-out/", { method: "GET", credentials: "include" });
    },
    async getUser() {
      const response = await fetch("./auth/user/", {
        method: "GET",
        credentials: "include",
        headers: { Accept: "application/json", "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) return null;
      return response.json();
    },

    /* ---------- Объекты / скважины / образцы ----------
       POST-эндпоинты создания в бэке — это upsert (INSERT ... ON CONFLICT DO UPDATE
       по первичному ключу), поэтому они же используются для редактирования.
       PUT /objects/ в бэке неисправен (dict.get(default=...)) — не использовать. */
    getObjects: () => request("./objects/objects", { emptyOn404: true }),
    saveObject: (data) => request("./objects/objects", { method: "POST", body: data }),

    getBoreholes: (objectId) =>
      request(`./objects/boreholes?object_id=${encodeURIComponent(objectId)}`, { emptyOn404: true }),
    saveBoreholes: (list) => request("./objects/boreholes", { method: "POST", body: list }),
    deleteBorehole: (boreholeId) =>
      request(`./objects/boreholes?borehole_id=${encodeURIComponent(boreholeId)}`, { method: "DELETE" }),

    getSamples: (boreholeId) =>
      request(`./objects/samples?borehole_id=${encodeURIComponent(boreholeId)}`, { emptyOn404: true }),
    saveSamples: (list) => request("./objects/samples", { method: "POST", body: list }),
    deleteSample: (sampleId) =>
      request(`./objects/samples?sample_id=${encodeURIComponent(sampleId)}`, { method: "DELETE" }),

    /* ---------- Типы испытаний ---------- */
    getTestTypes: (limit = 500, offset = 0) =>
      request(`./test_types/?limit=${limit}&offset=${offset}`, { emptyOn404: true }),
    createTestType: (data) => request("./test_types/", { method: "POST", body: data }),
    updateTestType: (id, data) =>
      request(`./test_types/?test_type_id=${encodeURIComponent(id)}`, { method: "PUT", body: data }),
    deleteTestType: (id) =>
      request(`./test_types/?test_type_id=${encodeURIComponent(id)}`, { method: "DELETE" }),

    /* ---------- Опыты ---------- */
    getTests({ objectNumber, boreholeName, laboratoryNumber, testType, limit = 100, offset = 0 } = {}) {
      const params = new URLSearchParams();
      if (objectNumber) params.set("object_number", objectNumber);
      if (boreholeName) params.set("borehole_name", boreholeName);
      if (laboratoryNumber) params.set("laboratory_number", laboratoryNumber);
      if (testType) params.set("test_type", testType);
      params.set("limit", String(limit));
      params.set("offset", String(offset));
      return request(`./tests/?${params.toString()}`, { emptyOn404: true });
    },
    createTest: (data) => request("./tests/", { method: "POST", body: data }),
    /* PUT /tests/ в бэке МЕРЖИТ test_params/test_results со старыми значениями
       (и падает, если старое значение NULL). Поэтому обновление двухшаговое:
       сначала обнуляем словари пустыми {}, затем шлём новые данные —
       merge в пустой словарь эквивалентен полной замене. */
    async updateTest(id, data) {
      await request(`./tests/?test_id=${encodeURIComponent(id)}`, {
        method: "PUT",
        body: { test_params: {}, test_results: {} },
      });
      return request(`./tests/?test_id=${encodeURIComponent(id)}`, { method: "PUT", body: data });
    },
    deleteTest: (id) =>
      request(`./tests/?test_id=${encodeURIComponent(id)}`, { method: "DELETE" }),

    /* ---------- Файлы ---------- */
    getTestFiles: (testId) =>
      request(`./tests/files/?test_id=${encodeURIComponent(testId)}`, { emptyOn404: true }),
    deleteFile: (fileId) =>
      request(`./tests/files/${encodeURIComponent(fileId)}`, { method: "DELETE" }),
    deleteAllFiles: (testId) =>
      request(`./tests/files/?test_id=${encodeURIComponent(testId)}`, { method: "DELETE" }),
    fileUrl: (key) => `./s3/?key=${encodeURIComponent(key)}`,

    uploadFile(testId, file, description, onProgress) {
      return new Promise((resolve, reject) => {
        const params = new URLSearchParams({ test_id: String(testId) });
        if (description) params.set("description", description);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", `./tests/files/?${params.toString()}`);
        xhr.withCredentials = true;
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

        if (xhr.upload && typeof onProgress === "function") {
          xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) onProgress(event.loaded / event.total);
          });
        }
        xhr.addEventListener("load", () => {
          if (xhr.status === 401) {
            handleUnauthorized();
            reject(Object.assign(new Error("Сессия истекла, выполняется выход…"), { status: 401 }));
          } else if (xhr.status >= 200 && xhr.status < 300) {
            try { resolve(JSON.parse(xhr.responseText)); } catch (_) { resolve(null); }
          } else {
            let message = `Ошибка ${xhr.status}`;
            if (xhr.status === 413) message = "Файл слишком большой (лимит 50 МБ)";
            try {
              const data = JSON.parse(xhr.responseText);
              if (data && data.detail) message = String(data.detail);
            } catch (_) { /* not json */ }
            reject(Object.assign(new Error(message), { status: xhr.status }));
          }
        });
        xhr.addEventListener("error", () => reject(new Error("Сетевая ошибка при загрузке файла")));
        const formData = new FormData();
        formData.append("file", file, file.name);
        xhr.send(formData);
      });
    },
  };
})();

/* ============================================================
   Страница входа
   ============================================================ */
(function () {
  const form = document.getElementById("login-form");
  if (!form) return;

  const errorBox = document.getElementById("auth-error");
  const submitBtn = document.getElementById("login-submit");
  const inputs = form.querySelectorAll(".field__input");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    event.stopPropagation();

    inputs.forEach((input) => input.classList.remove("is-invalid"));
    if (errorBox) errorBox.hidden = true;

    const username = form.username.value.trim();
    const password = form.password.value;

    if (!username || !password) {
      inputs.forEach((input) => { if (!input.value) input.classList.add("is-invalid"); });
      return;
    }

    submitBtn.disabled = true;
    API.signIn(username, password)
      .then((response) => {
        if (!response.ok) {
          inputs.forEach((input) => input.classList.add("is-invalid"));
          if (errorBox) errorBox.hidden = false;
          submitBtn.disabled = false;
        } else {
          window.location.reload();
        }
      })
      .catch(() => {
        if (errorBox) {
          errorBox.hidden = false;
          errorBox.querySelector("span").textContent = "Сервер недоступен, попробуйте позже";
        }
        submitBtn.disabled = false;
      });
  });
})();
