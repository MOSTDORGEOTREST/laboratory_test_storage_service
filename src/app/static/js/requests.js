function checkForm(username, password) {
  if (username === "" || password === "") {
    return false;
  } else {
    return true;
  }
}

function login(username, password, gotoUrl = null) {
  fetch("./auth/sign-in/", {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    credentials: "include", // include, *same-origin, omit
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
      // 'Content-Type': 'application/x-www-form-urlencoded',
      "X-Requested-With": "XMLHttpRequest",
    },
    body: `grant_type=password&username=${username}&password=${password}`,
  }).then((response) => {
    if (!response.ok) {
      const inputs = document.querySelectorAll("#login-form input");
      inputs.forEach((input) => {
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");
      });
    } else {
      if (gotoUrl) window.location.href = gotoUrl;
      if (!gotoUrl) window.location.reload();
    }
  });
}

const form = document.getElementById("login-form");

if (form) {
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    event.stopPropagation();

    const inputs = document.querySelectorAll("#login-form input");
    inputs.forEach((input) => {
      input.classList.remove("is-valid");
      input.classList.remove("is-invalid");
    });

    let error = false;

    if (!checkForm(form.username.value, form.password.value)) {
      inputs.forEach((input) => {
        input.classList.add("is-invalid");
      });
      error = true;
    }

    if (!error) login(form.username.value, form.password.value);
  });
}

const btnOut = document.getElementById("log-out");
if (btnOut) {
  btnOut.addEventListener("click", (event) => {
    event.preventDefault();
    fetch("./auth/sign-out/", {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then(() => {
      window.location.reload();
    });
  });

  fetch("./auth/user/", {
    method: "GET", // *GET, POST, PUT, DELETE, etc.
    credentials: "include", // include, *same-origin, omit
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Requested-With": "XMLHttpRequest",
    },
  }).then((response) => {
    if (!response.ok) {
      btnOut.style.display = "none";
    } else {
      btnOut.style.display = "inline-flex";
    }
  });
}

function getTests(objNum) {
  fetch(`./tests/?object_number=${objNum}&limit=500&offset=0`, {
    method: "GET", // *GET, POST, PUT, DELETE, etc.
    credentials: "include", // include, *same-origin, omit
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
      // 'Content-Type': 'application/x-www-form-urlencoded',
      "X-Requested-With": "XMLHttpRequest",
    },
  }).then((response) => {
    if (response.ok && response.status === 200) {
      cleanTables();

      response.json().then((data) => {
		console.log(data);
        if (data && data.length > 0) {
			fillTables(data);
        }
      });
      return;
    }
    if (response.status === 404) {
      cleanTables();
      return;
    }
  });
}

function cleanTables() {
  const testsTable = document.getElementById("tests-table-body");
  const resultsTable = document.getElementById("results-table-body");

  if (!(testsTable && resultsTable)) return;

  testsTable.textContent = "";
  resultsTable.textContent = "";
}

function formTableLine(trId, className, items) {
  let html = `<tr class="${className}" data-id="${trId}" >`;

  const innerHtml = items.map((value) => {
    return `<td class="table__td">${value}</td>`;
  });
  return html + innerHtml.join(' ') + "</tr>";
}

function fillTables(data) {
  if (!data) return;

  const testsTable = document.getElementById("tests-table-body");
  const resultsTable = document.getElementById("results-table-body");

  console.log(testsTable, resultsTable);

  if (!(testsTable && resultsTable)) return;

  console.log('ready to fill');

  data.forEach((item) => {
    const testsRow = formTableLine(item["test_id"], 'tests-row', [
      item["test_id"],
      item["borehole_name"],
      item["laboratory_number"],
      item["test_type"],
      new Date(item["timestamp"]).toLocaleDateString(),
    ]);
    testsTable.insertAdjacentHTML("beforeend", testsRow);

	addTestsClicker();
  });
}


function addTestsClicker() {
	const tests = document.querySelectorAll(
		'.tests-row[data-id]'
	)
	
	if (tests.length > 0) {
		tests.forEach((item) => {
			item.addEventListener('click', onTestClick)
		})
	
		function onTestClick(event) {
			event.preventDefault();
	
			const testId = event.currentTarget.dataset.id
			if (!testId) return;
			console.log('test id : ', testId);
	
		}
	}
}