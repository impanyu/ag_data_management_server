var domain_names=[];
  $.get("/get_domains",
        {
        },function(data,status){
           domain_names = JSON.parse(data);
        }

        );



function add_to_domain(path,file_name){
     box_height = 800;
     box_width = 1200;
     body = document.getElementsByTagName("body")[0];

     add_to_domain_box = document.createElement("div");
     add_to_domain_box.setAttribute("id","add_to_domain_box");
     add_to_domain_box.style.position = "fixed";
     add_to_domain_box.style.width = box_width+"px";
     add_to_domain_box.style.height = box_height+"px";
     add_to_domain_box.style.background = "white";
     add_to_domain_box.style.left =(body.offsetWidth - box_width)/2 + "px";
     add_to_domain_box.style.top = (body.offsetHeight - box_height)/2 + "px";

     title = document.createElement("div");
     title.style.margin = "50px";
     title.style.display = "inline-block";
     title.innerHTML = "<span>Add File to Domain</span>"
     add_to_domain_box.appendChild(title);

     submit_button = htmlToElement('<button class="btn btn-primary" type="button" id="add_to_domain_submit">Submit</button>');
     add_to_domain_box.appendChild(submit_button);

     submit_button.addEventListener("click",function(){
        $.post("/add_to_new_domain",
        {
           domain_name : document.getElementById("domain_name_select").value,
           start_date : document.getElementById("start_date").value,
           end_date : document.getElementById("end_date").value,
           southwest : document.getElementById("southwest").value,
           northeast : document.getElementById("northeast").value,
           file_path : path+"/"+file_name
        },function(data,status){

           if(data == "file added to domain"){
              add_to_domain_box.remove();
              background_cover.remove();
           }



        }

        )

     });



  domain_name_select_string = '<select class="form-control form-select-lg mb-3" data-toggle="select" title="Simple select" data-placeholder="Select a domain" id="domain_name_select">';
   //domain_name_select_string = '<select class="form-select form-select-lg mb-3" aria-label="domain select" id="domain_name_select">';

   for(domain_name in domain_names)
      domain_name_select_string +=  '<option value="'+domain_name+'">'+domain_name+'</option>'



   domain_name_select_string += '</select>'



    domain_name_select = htmlToElement(domain_name_select_string
     );



    domain_name_select.setAttribute("id","domain_name_select");
    domain_name_select.style.width =  box_width-100+"px";
    domain_name_select.style.marginLeft = "50px";

    add_to_domain_box.appendChild(domain_name_select);



    date_picker = htmlToElement('<div class="input-daterange datepicker row align-items-center">'+
    '<div class="col col-lg-6 ">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">'+
                '<div class="input-group-prepend">'+
                    '<span class="input-group-text"><i class="ni ni-calendar-grid-58"></i></span>'+
                '</div>'+
                '<input class="form-control"  placeholder="Start date" type="text" value="05/18/2022" id="start_date">'+
            '</div>'+
        '</div>'+
    '</div>'+
    '<div class="col col-lg-6">'+
        '<div class="form-group">'+
            '<div class="input-group input-group-alternative">'+
               '<div class="input-group-prepend">'+
                    '<span class="input-group-text"><i class="ni ni-calendar-grid-58"></i></span>'+
                '</div>'+
                '<input class="form-control" placeholder="End date" type="text" value="05/22/2022" id="end_date">'+
            '</div>'+
        '</div>'+
    '</div>'+
'</div>');



    //date_picker.setAttribute("id","date_picker");


    add_to_domain_box.appendChild(date_picker);
    date_picker.style.width =  box_width-100+"px";
    date_picker.style.marginLeft = "50px";


    $('body').on('focus',".datepicker input", function(){
            $(this).datepicker();
    });


    bounding_box =  htmlToElement('<div class="i row align-items-center">'+
    '<div class="col col-lg-6 ">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">'+

                '<input type="text" placeholder="Southwest Corner" class="form-control" id = "southwest"/>'+
            '</div>'+
        '</div>'+
    '</div>'+
    '<div class="col col-lg-6">'+
        '<div class="form-group">'+
            '<div class="input-group input-group-alternative">'+
                '<input type="text" placeholder="Northeast Corner" class="form-control" id="northeast"/>'+
            '</div>'+
        '</div>'+
    '</div>'+
'</div>');

    bounding_box.setAttribute("id","lower_left");
    bounding_box.style.width =  box_width-100+"px";
    bounding_box.style.marginLeft = "50px";

    add_to_domain_box.appendChild(bounding_box);


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
         add_to_domain_box.remove();

     });


     //$("body>*").css("opacity","0.5");
     body.appendChild(background_cover);
     body.appendChild(add_to_domain_box);





     map_container = document.createElement("div");
     map_container.setAttribute("id","map");



     map_container.style.width = box_width-100+"px";
     map_container.style.height = box_height-420+"px";
     map_container.style.marginLeft = "50px";
     add_to_domain_box.appendChild(map_container);


     initMap();


}
lastOverlay = null;

function initMap(){
  const map = new google.maps.Map(
    document.getElementById("map"),
    {
      center: { lat: 39.397, lng: -97.644 },
      zoom: 6,
    }
  );

  const drawingManager = new google.maps.drawing.DrawingManager({
    drawingMode: google.maps.drawing.OverlayType.RECTANGLE,
    drawingControl: true,
    drawingControlOptions: {
      position: google.maps.ControlPosition.TOP_CENTER,
      drawingModes: [
        google.maps.drawing.OverlayType.RECTANGLE,
      ],
    },
    markerOptions: {
      icon: "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png",
    },
    circleOptions: {
      fillColor: "#ffff00",
      fillOpacity: 1,
      strokeWeight: 5,
      clickable: false,
      editable: true,
      zIndex: 1,
    },
  });

  drawingManager.setMap(map);

  google.maps.event.addListener(drawingManager, "overlaycomplete", function(event){
       if(lastOverlay)
           lastOverlay.setMap(null);

        event.overlay.overlayType = event.type;
        lastOverlay = event.overlay; // Save it

        var bounds = lastOverlay.getBounds();
        var start = bounds.getNorthEast();
        var end = bounds.getSouthWest();

        document.getElementById("southwest").setAttribute("value",end) ;
        document.getElementById("northeast").setAttribute("value",start);


        //map.drawingManager.setDrawingMode(null); // Return to 'hand' mode
});


}
