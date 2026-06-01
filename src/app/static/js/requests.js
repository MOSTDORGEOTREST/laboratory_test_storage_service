function checkForm(username, password) {
  return username !== "" && password !== "";
}

function login(username, password, gotoUrl = null) {
  fetch("./auth/sign-in/", {
    method: "POST",
    credentials: "include",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: `grant_type=password&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
  }).then((response) => {
    if (!response.ok) {
      document.querySelectorAll("#login-form .field__input, #login-form input").forEach((input) => {
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");
      });
    } else {
      if (gotoUrl) window.location.href = gotoUrl;
      else window.location.reload();
    }
  });
}

const form = document.getElementById("login-form");

if (form) {
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    event.stopPropagation();

    const inputs = form.querySelectorAll(".field__input, input");
    inputs.forEach((input) => {
      input.classList.remove("is-valid", "is-invalid");
    });

    if (!checkForm(form.username.value, form.password.value)) {
      inputs.forEach((input) => input.classList.add("is-invalid"));
      return;
    }

    login(form.username.value, form.password.value);
  });
}

const btnOut = document.getElementById("log-out");
if (btnOut) {
  btnOut.addEventListener("click", (event) => {
    event.preventDefault();
    fetch("./auth/sign-out/", {
      method: "GET",
      credentials: "include",
    }).then(() => window.location.reload());
  });

  fetch("./auth/user/", {
    method: "GET",
    credentials: "include",
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
  }).then((response) => {
    btnOut.style.display = response.ok ? "inline-flex" : "none";
  });
}

function fetchTests(objectNumber) {
  return fetch(
    `./tests/?object_number=${encodeURIComponent(objectNumber)}&limit=500&offset=0`,
    {
      method: "GET",
      credentials: "include",
      headers: {
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
    }
  ).then((response) => {
    if (response.ok && response.status === 200) {
      return response.json();
    }
    if (response.status === 404) {
      return [];
    }
    throw new Error(`Tests request failed: ${response.status}`);
  });
}

function fetchTestFiles(testId) {
  return fetch(`./tests/files/?test_id=${testId}`, {
    method: "GET",
    credentials: "include",
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
  }).then((response) => {
    if (response.ok && response.status === 200) {
      return response.json();
    }
    if (response.status === 404) {
      return [];
    }
    throw new Error(`Files request failed: ${response.status}`);
  });
}
