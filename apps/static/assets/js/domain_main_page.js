var lastOverlay = null;

function init_map(){
rect_lower_lat = parseFloat(southwest.split(",")[0]);
rect_left_ln = parseFloat(southwest.split(",")[1]);
rect_upper_lat = parseFloat(northeast.split(",")[0]);
rect_right_ln = parseFloat(northeast.split(",")[1]);

center_lat = (rect_lower_lat + rect_upper_lat)/2;
center_ln = (rect_right_ln+ rect_left_ln)/2;

  const map = new google.maps.Map(
    document.getElementById("map"),
    {
      center: { lat:center_lat, lng: center_ln },
      zoom: 8,
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
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "blue",
    fillOpacity: .3,
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

$("input").datepicker();
query_content = {};
   $("#query")[0].addEventListener("click",function(){
        $.post("/query_domain",
        {
           domain_name : document.getElementById("domain_name").value,
           start_date : document.getElementById("start_date").value,
           end_date : document.getElementById("end_date").value,
           southwest : document.getElementById("southwest").value.substr(1,document.getElementById("southwest").value.length-2),
           northeast : document.getElementById("northeast").value.substr(1,document.getElementById("northeast").value.length-2),
           query_content : JSON.stringify(query_content)
        },function(data,status){
           alert("query succeed!");




        }



        )

     });