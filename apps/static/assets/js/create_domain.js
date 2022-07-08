function htmlToElement(html) {
          var template = document.createElement('template');
          html = html.trim(); // Never return a text node of whitespace as the result
          template.innerHTML = html;
          return template.content.firstChild;
}

function create_domain(){
     box_height = Math.min(800,window.innerHeight-200);
     box_width = Math.min(1200,window.innerWidth-200);
     body = document.getElementsByTagName("body")[0];
     new_domain_box = document.createElement("div");
     new_domain_box.setAttribute("id","create_domain_box");
     new_domain_box.style.position = "fixed";
     new_domain_box.style.width = box_width+"px";
     new_domain_box.style.height = box_height+"px";
     new_domain_box.style.background = "white";
     new_domain_box.style.left =(window.innerWidth - box_width)/2 + "px";
     new_domain_box.style.top = (window.innerHeight - box_height)/2 + "px";

     title = document.createElement("div");
     title.style.margin = "50px";
     title.style.display = "inline-block";
     title.innerHTML = "<span>Create New Domain</span>"
     new_domain_box.appendChild(title);


     submit_button = htmlToElement('<button class="btn btn-primary" type="button" id="new_domain_submit">Submit</button>');
     new_domain_box.appendChild(submit_button);

     submit_button.addEventListener("click",function(){
        $.post("/create_new_domain",
        {
           new_domain_name : document.getElementById("new_domain_name").value,
           start_date : document.getElementById("start_date").value,
           end_date : document.getElementById("end_date").value,
           southwest : document.getElementById("southwest").value.substr(1,document.getElementById("southwest").value.length-2),
           northeast : document.getElementById("northeast").value.substr(1,document.getElementById("northeast").value.length-2),
        },function(data,status){

           if(data == "domain created")
            location.href = '/domains.html';


        }



        )

     });



    name_input = htmlToElement('<div class="col">'+
        '<div class="form-group">'+
           '<div class="input-group input-group-alternative">'+
                '<input type="text" placeholder="Domain Name" class="form-control" id="new_domain_name" value=""/>'+
            '</div>'+
        '</div>'+
    '</div>');

    name_input.setAttribute("id","name_input");
    name_input.style.width =  box_width-100+"px";
    name_input.style.marginLeft = "50px";

    new_domain_box.appendChild(name_input);



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


    new_domain_box.appendChild(date_picker);
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

    new_domain_box.appendChild(bounding_box);


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





     map_container = document.createElement("div");
     map_container.setAttribute("id","map");



     map_container.style.width = box_width-100+"px";
     map_container.style.height = box_height-420+"px";
     map_container.style.marginLeft = "50px";
     new_domain_box.appendChild(map_container);


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


function init_map_main(){
  map_main = new google.maps.Map(
    document.getElementById("map_main"),
    {
      center: { lat: 39.397, lng: -97.644 },
      zoom: 6,
    }
  );

     $.get("/get_domains_meta",
        {
        },function(data,status){
            console.info(data)
           domains = JSON.parse(data);
            for(domain_name in domains){
                 console.info(parseFloat(domains[domain_name]["bounding_box"][0].split(",")[0]) );
                 var marker = new google.maps.Marker({
                    position: {lat:parseFloat(domains[domain_name]["bounding_box"][0].split(",")[0]) , lng: parseFloat(domains[domain_name]["bounding_box"][0].split(",")[1])},

                    label: domain_name,
                  });
                  marker.setMap(map_main);
            }



        }



        )






}