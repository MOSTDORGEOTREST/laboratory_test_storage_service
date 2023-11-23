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
  cleanTests();
  cleanResults();
  cleanFiles();
}

function cleanTests() {
  const testsTable = document.getElementById("tests-table-body");

  if (!testsTable) return;

  testsTable.textContent = "";
}

function cleanResults() {
  const resultsTable = document.getElementById("results-table-body");

  if (!resultsTable) return;

  resultsTable.textContent = "";
}


function cleanFiles() {
  const filesTable = document.getElementById("files-table-body");

  if (!filesTable) return;

  filesTable.textContent = "";
}

function formTableLine(trId, className, items) {
  let html = `<tr class="${className}" data-id="${trId}" >`;

  const innerHtml = items.map((value) => {
    return `<td class="table__td">${value}</td>`;
  });
  return html + innerHtml.join(" ") + "</tr>";
}

function fillTables(data) {
  if (!data) return;

  const testsTable = document.getElementById("tests-table-body");
  const resultsTable = document.getElementById("results-table-body");

  if (!(testsTable && resultsTable)) return;

  data.forEach((item) => {
    const testsRow = formTableLine(item["test_id"], "tests-row", [
      item["test_id"],
      item["borehole_name"],
      item["laboratory_number"],
      item["test_type"],
      new Date(item["timestamp"]).toLocaleDateString(),
    ]);
    testsTable.insertAdjacentHTML("beforeend", testsRow);

    addTestsClicker(item, resultsTable);

    // fillResults(item, resultsTable);
  });
}

function addTestsClicker(item, resultsTable) {
  const tests = document.querySelectorAll(
    `.tests-row[data-id='${item["test_id"]}'`
  );

  if (tests.length === 1) {
    tests[0].addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();

      cleanResults();
      fillResults(item, resultsTable);
    });
  }
}

function fillResults(item, resultsTable) {
  const params = Object.keys(item["test_params"])
    .map((key) => {
      return `<div>${key}: ${item["test_params"][key]}</div>`;
    })
    .join("");

  const results = Object.keys(item["test_results"])
    .map((key) => {
      return `<div>${key}: ${item["test_results"][key]}</div>`;
    })
    .join("");

  const resultsRow = formTableLine(item["test_id"], "results-row", [
    item["laboratory_number"],
    params,
    results,
  ]);
  resultsTable.insertAdjacentHTML("beforeend", resultsRow);

  addReusltsClicker(item);
}


function addReusltsClicker(item, resultsTable) {
  const tests = document.querySelectorAll(
    `.results-row[data-id='${item["test_id"]}'`
  );

  console.log("item : ", item);
  console.log("tests : ", tests);


  if (tests.length === 1) {
    tests[0].addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();

      console.log(item["test_id"]);
      cleanFiles();
      fillFiles(item);
    });
  }
}

function fillFiles(item) {
  const filesTable = document.getElementById("files-table-body");
  if (!filesTable) return;

  fetch(`./tests/files/?test_id=${item["test_id"]}`, {
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
      cleanFiles();

      response.json().then((data) => {
        if (data && data.length > 0) {
          data.forEach((file)=>{
            const td1 = `<td><a target='_blank' href='./s3/?key=${file["key"]}'>${file["key"]}</a></td>`
            const td2 = `<td style='text-wrap: wrap;'>${file["description"]}</td>`
            const row = `<tr>${td1}${td2}</tr>`
            filesTable.insertAdjacentHTML('beforeend', row);
          })
        }
      });
      return;
    }
    if (response.status === 404) {
      cleanFiles();
      return;
    }
  });
}