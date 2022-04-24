var stars = document.querySelectorAll('.rating_star');
var counter = document.querySelector('.rating_counter');
var field = document.querySelector('input.rating');


for (star of stars) {
    star.onclick = function (event) {
        var main_elem = event.srcElement;
        var parent = Array.from(main_elem.parentElement.childNodes);
        parent = parent.filter(i => i.className == 'rating_star');
        main_index = parent.indexOf(main_elem);
        counter.innerHTML = main_index + 1
        field.value = main_index + 1
        for (index in parent) {
            parent[index].innerHTML = '&#9734;';
            if (index <= main_index) {
                parent[index].innerHTML = '&#9733;';
            }
        }
        
    };
}