var lastOverlay = null;
var map;
var overlays=[];

function init_map(){
rect_lower_lat = parseFloat(southwest.split(",")[0]);
rect_left_ln = parseFloat(southwest.split(",")[1]);
rect_upper_lat = parseFloat(northeast.split(",")[0]);
rect_right_ln = parseFloat(northeast.split(",")[1]);

center_lat = (rect_lower_lat + rect_upper_lat)/2;
center_ln = (rect_right_ln+ rect_left_ln)/2;

   map = new google.maps.Map(
    document.getElementById("map"),
    {
      center: { lat:center_lat, lng: center_ln },
      zoom: 12,
    }
  );


  const rectCoords = [
    { lat: rect_lower_lat, lng: rect_left_ln },
    { lat: rect_lower_lat, lng: rect_right_ln},
    { lat: rect_upper_lat, lng: rect_right_ln },
    { lat: rect_upper_lat, lng: rect_left_ln }
  ];
// Construct the rect.
  const rectangle = new google.maps.Polygon({
    paths: rectCoords,
    strokeColor: "blue",
    strokeOpacity: 0.9,
    strokeWeight: 2,
    fillColor: "blue",
    fillOpacity: .1,
  });


  rectangle.setMap(map);


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

$(".daterange input").datepicker();
query_range = {};
   $("#query")[0].addEventListener("click",function(){
        $.post("/query_domain",
        {
           domain_name : domain_name,
           start_date : document.getElementById("start_date").value,
           end_date : document.getElementById("end_date").value,
           southwest : document.getElementById("southwest").value.substr(1,document.getElementById("southwest").value.length-2),
           northeast : document.getElementById("northeast").value.substr(1,document.getElementById("northeast").value.length-2),
           query_range : JSON.stringify(query_range)
        },function(data,status){
           alert("query succeed!");
           console.info(data);
           data = JSON.parse(data);

           for(var i=0;i<overlays.length;i++){
              overlays[i].setMap(null);
           }
           overlays=[];

           for(var i=0;i<data.length;i++){
              data_item = data[i];
              north = parseFloat(data_item["bounding_box"][1].split(",")[0]);
              south = parseFloat(data_item["bounding_box"][0].split(",")[0]);
              east = parseFloat(data_item["bounding_box"][1].split(",")[1]);
              west = parseFloat(data_item["bounding_box"][0].split(",")[1]);

               const imageBounds = {
                north: north,
                south: south,
                east: east,
                west: west,
              };

              img_overlay = new google.maps.GroundOverlay(
                data_item["file_path"],
                imageBounds
              );
              img_overlay.setMap(map);
              overlays.append(img_overlay);
              map.setCenter({lat: (north+south)/2 ,lng: (east+west)/2});
              map.setZoom(13);
          }




        }



        )

     });