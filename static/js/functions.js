function goToPage(index) {
    if (location.href.search(/page=./g) == -1) {
        location.href += (location.search ? '':'?' ) +`&page=${index}`
    } else {
        location.href = location.href.replace(/page=.*/g, `page=${index}`);
    }
    
}