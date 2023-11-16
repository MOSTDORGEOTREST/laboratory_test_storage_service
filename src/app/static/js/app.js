const objects = document.querySelectorAll(
	'.object-row[data-id]'
)

if (objects.length > 0) {
    objects.forEach((item) => {
        item.addEventListener('click', onObjectClick)
    })

    function onObjectClick(event) {
        event.preventDefault();

        const objNum = event.currentTarget.dataset.id
        if (!objNum) return;
        console.log('object num : ', objNum);
        getTests(objNum);

    }
}