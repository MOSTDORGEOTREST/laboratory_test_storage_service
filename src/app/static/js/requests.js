function checkForm(username, password) {
	if (username === '' || password === '') {
		return false
	} else {
		return true
	}
}

function login(username, password, gotoUrl = null) {
	fetch('./auth/sign-in/', {
		method: 'POST', // *GET, POST, PUT, DELETE, etc.
		credentials: 'include', // include, *same-origin, omit
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/x-www-form-urlencoded',
			// 'Content-Type': 'application/x-www-form-urlencoded',
			'X-Requested-With': 'XMLHttpRequest',
		},
		body: `grant_type=password&username=${username}&password=${password}`,
	}).then((response) => {
		if (!response.ok) {
			const inputs = document.querySelectorAll('#login-form input')
			inputs.forEach((input) => {
				input.classList.remove('is-valid')
				input.classList.add('is-invalid')
			})
		} else {
			if (gotoUrl) window.location.href = gotoUrl
			if (!gotoUrl) window.location.reload()
		}
	})
}

const form = document.getElementById('login-form')

if (form) {
	form.addEventListener('submit', function (event) {
		event.preventDefault()
		event.stopPropagation()

		const inputs = document.querySelectorAll('#login-form input')
		inputs.forEach((input) => {
			input.classList.remove('is-valid')
			input.classList.remove('is-invalid')
		})

		let error = false

		if (!checkForm(form.username.value, form.password.value)) {
			inputs.forEach((input) => {
				input.classList.add('is-invalid')
			})
			error = true
		}

		if (!error) login(form.username.value, form.password.value)
	})
}

const btnOut = document.getElementById('log-out')
if (btnOut) {
	btnOut.addEventListener('click', (event) => {
		event.preventDefault()
		fetch('./auth/sign-out/', {
			method: 'GET', // *GET, POST, PUT, DELETE, etc.
			credentials: 'include', // include, *same-origin, omit
		}).then(() => {
			window.location.reload()
		})
	})

	fetch('./auth/user/', {
		method: 'GET', // *GET, POST, PUT, DELETE, etc.
		credentials: 'include', // include, *same-origin, omit
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/x-www-form-urlencoded',
			'X-Requested-With': 'XMLHttpRequest',
		}
	}).then((response) => {
		if (!response.ok) {
			btnOut.style.display = 'none'
		} else {
			btnOut.style.display = 'inline-flex'
		}
	})
}
