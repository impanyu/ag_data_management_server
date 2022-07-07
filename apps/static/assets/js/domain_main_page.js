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