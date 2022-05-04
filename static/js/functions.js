function goToPage(index) {
    if (location.href.search(/page=./g) == -1) {
        location.href += (location.search ? '':'?' ) +`&page=${index}`
    } else {
        location.href = location.href.replace(/page=.*/g, `page=${index}`);
    }
    
}


function unableField(elem) {
    address = document.querySelector('[name=address]');
    if (elem.value === 'custom')
        address.disabled = '';
    else 
        address.disabled = 'disabled';
        address.value = '';
}