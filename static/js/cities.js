    var cities = ["Zagreb","Split","Rijeka","Osjek"];     
    var sel = document.getElementById('cityList');
    var fragment = document.createDocumentFragment();
    
    cities.forEach(function(cuisine, index) {
        var opt = document.createElement('option');
        opt.innerHTML = cuisine;
        opt.value = cuisine;
        fragment.appendChild(opt);
    });
    sel.appendChild(fragment);