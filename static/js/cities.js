    var cities = ["Bakar","Beli Manastir","Belišće","Benkovac","Biograd na Moru","Bjelovar","Buje","Buzet","Cres","Crikvenica","Čabar","Čakovec","Čazma","Daruvar","Delnice","Donja Stubica","Donji Miholjac","Drniš","Dubrovnik","Duga Resa","Dugo Selo","Đakovo","Đurđevac","Garešnica","Glina","Gospić","Grubišno Polje","Hrvatska Kostajnica","Hvar","Ilok","Imotski","Ivanec","Ivanić-Grad","Jastrebarsko","Karlovac","Kastav","Kaštela","Klanjec","Knin","Komiža","Koprivnica","Korčula","Kraljevica","Krapina","Križevci","Krk","Kutina","Kutjevo","Labin","Lepoglava","Lipik","Ludbreg","Makarska","Mali Lošinj","Metković","Mursko Središće","Našice","Nin","Nova Gradiška","Novalja","Novi Marof","Novi Vinodolski","Novigrad","Novska","Obrovac","Ogulin","Omiš","Opatija","Opuzen","Orahovica","Oroslavje","Osijek","Otočac","Otok","Ozalj","Pag","Pakrac","Pazin","Petrinja","Pleternica","Ploče","Popovača","Poreč","Požega","Pregrada","Prelog","Pula","Rab","Rijeka","Rovinj","Samobor","Senj","Sinj","Sisak","Skradin","Slatina","Slavonski Brod","Slunj","Solin","Split","Stari Grad","Supetar","Sveta Nedelja","Sveti Ivan Zelina","Šibenik","Trilj","Trogir","Umag","Valpovo","Varaždin","Varaždinske Toplice","Velika Gorica","Vinkovci","Virovitica","Vis","Vodice","Vodnjan","Vrbovec","Vrbovsko","Vrgorac","Vrlika","Vukovar","Zabok","Zadar","Zagreb","Zaprešić","Zlatar","Županja"];     
    var sel = document.getElementById('cityList');
    var fragment = document.createDocumentFragment();
    
    cities.forEach(function(cuisine, index) {
        var opt = document.createElement('option');
        opt.innerHTML = cuisine;
        opt.value = cuisine;
        if (cuisine == "Zagreb"){
            opt.selected = "selected";
        }
        fragment.appendChild(opt);
    });
    sel.appendChild(fragment);