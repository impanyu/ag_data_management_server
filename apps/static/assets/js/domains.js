function create_domain(new_domain_name){




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