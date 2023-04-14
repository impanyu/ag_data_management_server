function create_collection(new_collection_name){
       $.ajax({
            type: "POST",

            url: "/create_collection",
            data: {
               new_collection_name: new_collection_name
            },
            success: function (data) {
                console.info(data);
                //$("#box_container")[0].innerHTML="";
                create_collection_overlay.style.display  = "none";
                document.querySelector("#new_collection_name").value = "New collection";
                get_collection_list();
            }
        });



}


function set_create_collection_overlay(){
        const create_collection_overlay = document.querySelector('#create_collection_overlay');

        create_collection_overlay.addEventListener('click', function(event) {
            this.style.display  = "none";
        });

        const create_collection_tab = document.querySelector('#create_collection_tab');

        create_collection_tab.addEventListener('click', function(event) {
           event.stopPropagation();
        });


        const create_collection_button = document.querySelector('#create_collection_button');

        create_collection_button.addEventListener('click', function(event) {

           new_collection_name = document.querySelector("#new_collection_name").value;
           create_collection(new_collection_name);
        });


        const cancel_create_collection_button = document.querySelector('#cancel_create_collection_button');

        cancel_create_collection_button.addEventListener('click', function(event) {
           create_collection_overlay.style.display  = "none";
        });

        const create_collection_li = document.querySelector('#create_collection');

        create_collection_li.addEventListener('click', function(event) {
           create_collection_overlay.style.display  = "flex";
        });
}


function get_collection_list(){
       $.ajax({
            type: "POST",

            url: "/file_system_virtual",
            data: {
               current_path: current_path
            },
            success: function (data) {
                console.info(data);
                collections = JSON.parse(data);
                for(collection of collections){
                    document.querySelector("#box_container").innerHTML += '<div class="col-lg-3 col-md-6">'+
                      '<button type="button" class="btn-block" data-clipboard-text="active-40" onclick="window.open(\'/collection.html?current_path='+user+'/ag_data/collections/'+collection["name"]+'\',\'_self\').focus()">'+
                        '<div>'+
                          '<i class="ni ni-map-big "></i>'+
                          '<span>'+collection["name"]+'</span>'+
                       '</div>'+
                      '</button>'+
                    '</div>';
                }

            }
        });
}

set_create_collection_overlay();
get_collection_list();