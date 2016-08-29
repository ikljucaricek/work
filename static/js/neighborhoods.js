var neighborhoods = ["Blato","Borongaj","Borovje","Botinec","Brestje","Brezovica","Bukovac","Buzin","Centar","Črnomerec","Čulinec","Cvjetno naselje","Dubec","Dubrava","Dugave","Ferenščica","Folnegovićevo","Gajnice","Gračani","Ivanja Reka","Jakuševec","Jankomir","Jarun","Kajzerica","Kanal","Klara","Knežija","Kruge","Ksaver","Kustošija","Kvatrić","Lanište","Lučko","Ljubljanica","Maksimir","Malešnica","Markuševec","Medveščak","Mikulići","Mlinovi","Peščenica","Podsused","Poljanice","Prečko","Ravnice","Remete","Remetinec","Retkovec","Rudeš","Savica","Savski gaj","Šestine","Sesvete","Sigečica","Siget","Sloboština","Sopot","Špansko","Središće","Srednjaci","Stenjevec","Stupnik","Sveta Nedelja","Svetice","Travno","Trešnjevka","Trnava","Trnovčica","Trnsko","Trnje","Trokut","Utrina","Veliko Polje","Volovčica","Voltino","Vrapče","Vrbani","Vrbik","Vukomerec","Zapruđe","Zavrtnica","Žitnjak"];     
    var sel = document.getElementById('neighborhoodList');
    var fragment = document.createDocumentFragment();
    
    neighborhoods.forEach(function(cuisine, index) {
        var opt = document.createElement('option');
        opt.innerHTML = cuisine;
        opt.value = cuisine;
        fragment.appendChild(opt);
    });
sel.appendChild(fragment);