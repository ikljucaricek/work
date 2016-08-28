var neighborhoods = ["Lucko","Gornji Grad","Remiza","Tresnjevka","Vrbani"];     
    var sel = document.getElementById('neighborhoodList');
    var fragment = document.createDocumentFragment();
    
    neighborhoods.forEach(function(cuisine, index) {
        var opt = document.createElement('option');
        opt.innerHTML = cuisine;
        opt.value = cuisine;
        fragment.appendChild(opt);
    });
sel.appendChild(fragment);