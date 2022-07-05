function htmlToElement(html) {
          var template = document.createElement('template');
          html = html.trim(); // Never return a text node of whitespace as the result
          template.innerHTML = html;
          return template.content.firstChild;
}

function create_domain(){
     box_height = 800;
     box_width = 1200;
     body = document.getElementsByTagName("body")[0];
     new_domain_box = document.createElement("div");
     new_domain_box.setAttribute("id","create_domain_box");
     //new_domain_box.style.position = "fixed";
     new_domain_box.style.width = box_width+"px";
     new_domain_box.style.height = box_height+"px";
     new_domain_box.style.background = "white";
     new_domain_box.style.left =(body.offsetWidth - box_width)/2 + "px";
     new_domain_box.style.top = (body.offsetHeight - box_height)/2 + "px";

     title = document.createElement("div");
     title.style.margin = "40px";
     title.innerHTML = "<span>Create New Domain</span>"
     new_domain_box.appendChild(title);


    name_input = htmlToElement('<div class="col">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">'+
                '<input type="text" placeholder="Domain Name" class="form-control" />'+
            '</div>'+
        '</div>'+
    '</div>');

    name_input.setAttribute("id","name_input");

    new_domain_box.appendChild(name_input);



    date_picker = htmlToElement('<div class="input-daterange datepicker row align-items-center">'+
    '<div class="col">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">'+
                '<div class="input-group-prepend">'+
                    '<span class="input-group-text"><i class="ni ni-calendar-grid-58"></i></span>'+
                '</div>'+
                '<input class="form-control"  placeholder="Start date" type="text" value="06/18/2020">'+
            '</div>'+
        '</div>'+
    '</div>'+
    '<div class="col">'+
        '<div class="form-group">'+
            '<div class="input-group input-group-alternative">'+
               '<div class="input-group-prepend">'+
                    '<span class="input-group-text"><i class="ni ni-calendar-grid-58"></i></span>'+
                '</div>'+
                '<input class="form-control" placeholder="End date" type="text" value="06/22/2020">'+
            '</div>'+
        '</div>'+
    '</div>'+
'</div>');



    //date_picker.setAttribute("id","date_picker");


    new_domain_box.appendChild(date_picker);








     background_cover = document.createElement("div");
     background_cover.setAttribute("id","background_cover");
     background_cover.style.position = "fixed";
     background_cover.style.width = body.offsetWidth+"px";
     background_cover.style.height = body.offsetHeight+"px";
     background_cover.style.background = "black";
     background_cover.style.left =0 + "px";
     background_cover.style.top = 0 + "px";
     background_cover.style.opacity = "0.5";
     background_cover.addEventListener("click",function(){

         this.remove();
         new_domain_box.remove();

     });


     //$("body>*").css("opacity","0.5");
     body.appendChild(background_cover);
     body.appendChild(new_domain_box);



}