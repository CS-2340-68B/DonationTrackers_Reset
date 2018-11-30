// Controller for detail list view
function viewDetail(event) {
    textOut = event.target.parentElement.innerText.split('\n')
    locationName = textOut[0].slice(12, textOut[0].length)
    window.location.href = '/locationdetail' + '/' + locationName
}