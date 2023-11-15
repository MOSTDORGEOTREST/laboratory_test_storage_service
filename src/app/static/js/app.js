const objects = document.querySelectorAll(
	'.object-row[data-id]'
)

if (objects.length > 0) {
    objects.forEach((item) => {
        item.addEventListener('click', onObjectClick)
    })

    function onObjectClick(event) {
        event.preventDefault();

        console.log('objID:', event.currentTarget.dataset.id);
    }
}