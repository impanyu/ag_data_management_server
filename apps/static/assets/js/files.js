var domain_names=[];
  $.get("/get_domains",
        {
        },function(data,status){
           domain_names = JSON.parse(data);
        }

        );
var start;
var end;
var map;
var lastOverlay;
var drawingManager;



function add_to_domain(path,file_name){
      if(file_name.split(".")[file_name.split(".").length-1] !="tif" && file_name.split(".")[file_name.split(".").length-1] !="tiff" && file_name.split(".")[file_name.split(".").length-1] !="png" && file_name.split(".")[file_name.split(".").length-1] !="jpg")
         return;

      if(file_name.split(".")[file_name.split(".").length-1] == "tif" || file_name.split(".")[file_name.split(".").length-1] =="tiff"){
              $.get("/get_tif_range",
                {
                   file_path : path+"/"+file_name
                },function(data,status){
                   console.info(data);

                   data = JSON.parse(data);
                   start = data[0];
                   end = data[1];


                   rectangle = new google.maps.Rectangle({
                        strokeColor: "#FF0000",
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        fillColor: "#FF0000",
                        fillOpacity: 0.35,
                        map,
                        bounds: {
                          north: end[0],
                          south: start[0],
                          east: end[1],
                          west: start[1],
                        },
                      });

                      rectangle.setMap(map);
                      lastOverlay = rectangle;

                      map.setCenter({lat:(start[0]+end[0])/2,lng:(start[1]+end[1])/2});
                      document.getElementById("southwest").setAttribute("value",start) ;
                      document.getElementById("northeast").setAttribute("value",end);


                }

                );
        }

     body = document.getElementsByTagName("body")[0];

     box_height = Math.min(800,window.innerHeight-200);
     box_width = Math.min(1200,window.innerWidth-200);


     add_to_domain_box = document.createElement("div");
     add_to_domain_box.setAttribute("id","add_to_domain_box");
     add_to_domain_box.style.position = "fixed";
     add_to_domain_box.style.width = box_width+"px";
     add_to_domain_box.style.height = box_height+"px";
     add_to_domain_box.style.background = "white";
     add_to_domain_box.style.left =(window.innerWidth - box_width)/2 + "px";
     add_to_domain_box.style.top = (window.innerHeight - box_height)/2 + "px";

     title = document.createElement("div");
     title.style.margin = "50px";
     title.style.display = "inline-block";
     title.innerHTML = "<span>Add File to Domain</span>"
     add_to_domain_box.appendChild(title);

     submit_button = htmlToElement('<button class="btn btn-primary" type="button" id="add_to_domain_submit">Submit</button>');
     add_to_domain_box.appendChild(submit_button);



     submit_button.addEventListener("click",function(){
        attr_id=document.getElementById("attr").value;
        $.post("/add_to_domain",
        {


           domain_name : document.getElementById("domain_name_select").value,
           start_date : document.getElementById("start_date").value,
           end_date : document.getElementById("end_date").value,
           southwest : document.getElementById("southwest").value,
           northeast : document.getElementById("northeast").value,
           data_content : JSON.stringify({attr_id: path+"/"+file_name})
        },function(data,status){
           console.info(data);

           if(data == "item added to domain"){
              alert("item added to domain: "+document.getElementById("domain_name_select").value);
              add_to_domain_box.remove();
              background_cover.remove();

           }



        }

        )

     });



   //domain_name_select_string = '<select class="form-select form-select-lg mb-3" aria-label="domain select" id="domain_name_select">';

  domain_name_select_string = '<div class="col col-lg-6 align-items-center">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">';
   domain_name_select_string += '<select class="form-control form-select-lg" data-toggle="select" title="Simple select" data-placeholder="Select a domain" id="domain_name_select">';


   for(var i in domain_names)
      domain_name_select_string +=  '<option value="'+domain_names[i]+'">'+domain_names[i]+'</option>'



   domain_name_select_string += '</select></div></div></div>'



    domain_name_select = htmlToElement(domain_name_select_string
     );




    domain_name_select.setAttribute("id","domain_name_select");
    //domain_name_select.style.width =  box_width-100+"px";
    //domain_name_select.style.marginLeft = "50px";



    //add_to_domain_box.appendChild(domain_name_select);



   attr_input = htmlToElement('<div class="col col-lg-6 align-items-center">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">'+
                '<input type="text" placeholder="Attribute Name" class="form-control" id="attr" value=""/>'+
            '</div>'+
        '</div>'+
    '</div>');

    attr_input.getElementById("attr").value = file_name.substr(0,file_name.length-file_name.split(".")[file_name.split(".").length-1].length);
    domain_and_attr_container = htmlToElement('<div class="row align-items-center" style="width: 1100px; margin-left: 50px;"></div>')
    domain_and_attr_container.appendChild(domain_name_select);
    domain_and_attr_container.appendChild(attr_input);
    add_to_domain_box.appendChild(domain_and_attr_container);


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


function initMap(){
  map = new google.maps.Map(
    document.getElementById("map"),
    {
      center: { lat: 39.397, lng: -97.644 },
      zoom: 14,
    }
  );

  drawingManager = new google.maps.drawing.DrawingManager({
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
      fillOpacity: .8,
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
        end = bounds.getNorthEast();
        start = bounds.getSouthWest();

        document.getElementById("southwest").setAttribute("value",start) ;
        document.getElementById("northeast").setAttribute("value",end);


        //map.drawingManager.setDrawingMode(null); // Return to 'hand' mode
});


}
