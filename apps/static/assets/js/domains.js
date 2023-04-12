function create_domain(new_domain_name){
       $.ajax({
            type: "POST",

            url: "/create_domain",
            data: {
               new_domain_name: new_domain_name
            },
            success: function (data) {
                console.info(data);
                //$("#box_container")[0].innerHTML="";
                create_domain_overlay.style.display  = "none";
                document.querySelector("#new_domain_name").value = "New Domain";
                get_domain_list();
            }
        });



}


function set_create_domain_overlay(){
        const create_domain_overlay = document.querySelector('#create_domain_overlay');

        create_domain_overlay.addEventListener('click', function(event) {
            this.style.display  = "none";
        });

        const create_domain_tab = document.querySelector('#create_domain_tab');

        create_domain_tab.addEventListener('click', function(event) {
           event.stopPropagation();
        });


        const create_domain_button = document.querySelector('#create_domain_button');

        create_domain_button.addEventListener('click', function(event) {

           new_domain_name = document.querySelector("#new_domain_name").value;
           create_domain(new_domain_name);
        });


        const cancel_create_domain_button = document.querySelector('#cancel_create_domain_button');

        cancel_create_domain_button.addEventListener('click', function(event) {
           create_domain_overlay.style.display  = "none";
        });

        const create_domain_li = document.querySelector('#create_domain');

        create_domain_li.addEventListener('click', function(event) {
           create_domain_overlay.style.display  = "flex";
        });
}


function get_domain_list(){
       $.ajax({
            type: "POST",

            url: "/file_system_virtual",
            data: {

            },
            success: function (data) {
                console.info(data);
                domains = JSON.parse(data);
                for(domain of domains){
                    document.querySelector("#box_container").innerHTML += '<div class="col-lg-3 col-md-6">'+
                      '<button type="button" class="btn-block" data-clipboard-text="active-40"  onclick="/domain.html?current_path={{user}}/ag_data/domain/'+domain["name"]+'">'+
                        '<div>'+
                          '<i class="ni ni-map-big "></i>'+
                          '<span>'+domain["name"]+'</span>'+
                       '</div>'+
                      '</button>'+
                    '</div>';
                }

            }
        });
}

set_create_domain_overlay();
get_domain_list();