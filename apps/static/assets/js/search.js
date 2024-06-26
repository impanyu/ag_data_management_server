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
        data_content = {};
        data_content[attr_id] =path+"/"+file_name;
        console.info(data_content);
        $.post("/add_to_domain",
        {


           domain_name : document.getElementById("domain_name_select").value,
           start_date : document.getElementById("start_date").value,
           end_date : document.getElementById("end_date").value,
           southwest : document.getElementById("southwest").value,
           northeast : document.getElementById("northeast").value,
           data_content : JSON.stringify(data_content)
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

    document.getElementById("attr").value = file_name.substr(0,file_name.length-file_name.split(".")[file_name.split(".").length-1].length-1);



     initMap();


}


  // Add event listener to the search box
  document.getElementById('search_box').addEventListener('keydown', function(event) {
    // Check if the Enter key (key code 13) is pressed
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default form submission (if inside a form)
        get_item_list(); // Call the function
    }
});


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
    rectangleOptions: {
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

google_map_circles = []

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

//get_file_list();

//$("option").click(function(){this.selected=true});

search_results_title = "Search Results:";
color_scale_map = {"Data":0, "Tool":1, "Collection":2, "Model":3};
modes = ["Data","Tool","Collection","Model"];

function get_item_list(){

  $("#file_list")[0].innerHTML="";
  category = [];
  category_options = document.querySelector("#category").options;
    for (var i =0; i<category_options.length; i++){
     if(category_options[i].selected)
        category.push(category_options[i].value);
  }


  mode = [];
  mode_options = document.querySelector("#mode").options;
  for (var i =0; i<mode_options.length; i++){
     if(mode_options[i].selected)
        mode.push(mode_options[i].value);
  }

  format = [];
  format_options = document.querySelector("#format").options;
  for (var i =0; i<format_options.length; i++){
     if(format_options[i].selected)
        format.push(format_options[i].value);
  }

  label = [];
  label_options = document.querySelector("#label").options;
  for (var i =0; i<label_options.length; i++){
     if(label_options[i].selected)
        label.push(label_options[i].value);
  }

  privilege = [];
  privilege_options = document.querySelector("#privilege").options;
  for (var i =0; i<privilege_options.length; i++){
     if(privilege_options[i].selected)
        privilege.push(privilege_options[i].value);
  }

 realtime = [];

 realtime_options = document.querySelector("#realtime").options;
  for (var i =0; i<realtime_options.length; i++){
     if(realtime_options[i].selected)
        realtime.push(realtime_options[i].value);
  }


 //console.info(mode);

  $.ajax({
         type: "POST",
         url:"/mode_search",
         data:JSON.stringify({
          current_path: current_path,

          search_box: document.querySelector("#search_box").value,
          category: category,
          mode:  mode,
          format:  format,
          label:  label,
          privilege: privilege,
          realtime: realtime,
          time_range:  [document.querySelector("#start_date").value,document.querySelector("#end_date").value],
          bounding_box:  [document.querySelector("#southwest").value, document.querySelector("#northeast").value]

        }),
        contentType: "application/json",
        success: function(data, status){
          //console.info(data);
          data=JSON.parse(data);
          subdomains=[];
          times=[];

          //draw all the data & files in current_path on google map based
          items = data["items"];
          points = data["2d_points"]


          console.info(items);
          console.info(search_results_title);
          document.querySelector("#result_number").innerHTML= "<b>"+search_results_title+" "+items.length+"</b>";
          for(i in items){
             items[i]["2d"] = points[i];
             //if(items[i]["format"].length > 0)
               items[i]["2d"].push(color_scale_map[items[i]["mode"][0]]);
             //else
               //items[i]["2d"].push(0);
          }

          draw_points(items);
          draw_2d_points(items);


          for(var i=0;i<items.length;i++){
          item = data["items"][i];
          item_path = item["abs_path"].substr(6)

            item_html =  '<tr class="file_and_dir_item"><td scope="row"><div class="media align-items-center"><div class="media-body"><span class="name mb-0 text-sm"> &nbsp;<a href="/files.html?current_path='+item_path+'"> ' +item["name"]+
                     '</a></span> </div></div></td>" + "<td class="budget">'+item["mode"]+'</td>"' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+item["format"]+'</span></span></td>' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+item["category"]+'</span></span></td>' +
                   '<td> <div class="avatar-group"> <a href="#" class=" " data-toggle="tooltip" data-original-title='+item["owner"]+'>'+item["owner"]+'</a></div></td>' +
                   '<td ><div class="dropdown"><a class="btn btn-sm btn-icon-only text-light" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></a>'+
                   '<div class="dropdown-menu dropdown-menu-right dropdown-menu-arrow">'+
                   '<a class="dropdown-item" href="#" id="'+i+'_file_delete">Delete</a>'+
                   '<a class="dropdown-item" href="#" id="'+i+'_add_domain">Add to Domain</a>'+
                   '</div> </div></td></tr>';
            item_node = htmlToElement(item_html);
            $("#file_list")[0].appendChild(item_node);


            $("#"+i+"_file_delete").click(function(){
               file_name= data["files"][parseInt(this.id.split("_")[0])]["file_name"];


               console.info(file_name);
               $.post("/delete_file",
                      {
                        current_path : current_path,
                        file_name: file_name
                      },
                      function(data, status){
                          $("#file_list")[0].innerHTML="";
                          get_item_list();
                          alert(data);
                      });
            });

            $("#"+i+"_add_domain").click(function(){
               file_name= data["files"][parseInt(this.id.split("_")[0])]["file_name"];
               console.info(file_name);
               add_to_domain(current_path,file_name);
            });

             $("#"+i+"_meta_data").click(function(){
               file_name= data["files"][parseInt(this.id.split("_")[0])]["file_name"];
               console.info(file_name);
               //get_meta_data(current_path,file_name);
            });
          }


          /*
          for(var i=0;i<data['files'].length;i++){
          file=data["files"][i];

            item_html =  '<tr><td scope="row"><div class="media align-items-center"><div class="media-body"><span class="name mb-0 text-sm"> &nbsp;<a href="/static/users/'+current_path+'/'+file["file_name"]+'"> ' +file["file_name"]+ '</a></span> </div></div></td>" + "<td class="budget">'+file["created_time"]+'</td>"' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+file["accessed_time"]+'</span></span></td>' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+file["size"]+'</span></span></td>' +
                   '<td> <div class="avatar-group"> <a href="#" class="avatar avatar-sm rounded-circle" data-toggle="tooltip" data-original-title='+user+'><img alt="Image placeholder" src="/static/assets/img/theme/react.jpg"></a></div></td>' +
                   '<td ><div class="dropdown"><a class="btn btn-sm btn-icon-only text-light" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></a>'+
                   '<div class="dropdown-menu dropdown-menu-right dropdown-menu-arrow">'+
                   '<a class="dropdown-item" href="#" id="'+i+'_file_delete">Delete</a>'+
                   '<a class="dropdown-item" href="#" id="'+i+'_add_domain">Add to Domain</a>'+
                   '<a class="dropdown-item" href="#" id="'+i+'_meta_data">Meta Data</a>'+
                   '<a class="dropdown-item" href="#" id="'+i+'_google_earth_engine">Earth Engine</a>'+
                   '</div> </div></td></tr>';
            item_node = htmlToElement(item_html);
            $("#file_list")[0].appendChild(item_node);


            $("#"+i+"_file_delete").click(function(){
               file_name= data["files"][parseInt(this.id.split("_")[0])]["file_name"];


               console.info(file_name);
               $.post("/delete_file",
                      {
                        current_path : current_path,
                        file_name: file_name
                      },
                      function(data, status){
                          $("#file_list")[0].innerHTML="";
                          get_file_list();
                          alert(data);
                      });


            });


            $("#"+i+"_add_domain").click(function(){
               file_name= data["files"][parseInt(this.id.split("_")[0])]["file_name"];
               console.info(file_name);
               add_to_domain(current_path,file_name);


            });

             $("#"+i+"_meta_data").click(function(){
               file_name= data["files"][parseInt(this.id.split("_")[0])]["file_name"];
               console.info(file_name);
               //get_meta_data(current_path,file_name);


            });
          }
       */


    }});
}

map_displayed = "map";

function change_file_plot(){
    if (map_displayed == "map"){
         document.querySelector("#map_main").style.display="none";
         document.querySelector("#files_plot").style.display="block";
         map_displayed="files_plot";
        }
    else{
     document.querySelector("#map_main").style.display="block";
         document.querySelector("#files_plot").style.display="none";
         map_displayed="map";
    }

}


$('body').on('focus',".datepicker input", function(){
            console.info()
            $(this).datepicker();
  });


function init_map_main(){
  map_main = new google.maps.Map(
    document.getElementById("map_main"),
    {
      center: { lat: 40.897, lng: -96.644 },
      zoom: 11,
    }
  );


     $.get("/get_domains_meta",
        {
        },function(data,status){
            //console.info(data)
           domains = JSON.parse(data);
            for(domain_name in domains){
                 //console.info(parseFloat(domains[domain_name]["bounding_box"][0].split(",")[0]) );
                 var marker = new google.maps.Marker({
                    position: {lat:parseFloat(domains[domain_name]["bounding_box"][0].split(",")[0]) , lng: parseFloat(domains[domain_name]["bounding_box"][0].split(",")[1])},
                    label: domain_name,
                  });
                  marker.setMap(map_main);
            }
        }
        )


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
    rectangleOptions: {
      fillColor: "#0000ff",
      fillOpacity: .6,
      strokeWeight: 3,
      clickable: false,
      editable: true,
      zIndex: 1,
    },
  });

  drawingManager.setMap(map_main);

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

var mode_color_map = {};
mode_color_map["Data"] = "pink";
mode_color_map["Tool"] = "blue";
mode_color_map["Model"] = "red";
mode_color_map["Collection"] = "green";

function draw_points(data_points){

  //clear circles
  google_map_circles.forEach(function(circle){circle.setMap(null)});
  google_map_circles=[];
  lat_center = 0;
  lng_center = 0;
   num =0;
   for (i in data_points) {
   data_point = data_points[i]
    data_mode = data_point["mode"];
    data_loc = {"lat": (data_point["spatial_range"]["southwest"]["lat"]+ data_point["spatial_range"]["northeast"]["lat"])/2, "lng":(data_point["spatial_range"]["southwest"]["lng"]+ data_point["spatial_range"]["northeast"]["lng"])/2}

    if (data_loc["lat"] == 0) continue;
    num++;
     lat_center += data_loc["lat"];
    lng_center += data_loc["lng"];
    //size = data_point["size"];
    const point = new google.maps.Circle({
      strokeColor: "black",
      strokeOpacity: 0.5,
      strokeWeight: 5,
      fillColor: mode_color_map[data_mode[0]],
      fillOpacity: 0.8,
      map:map_main,
      center: data_loc,
      radius:2000//Math.min(size,1000),
    });
    google_map_circles.push(point);
    if(num>0)
    map_main.setCenter({"lat":lat_center/num,"lng":lng_center/num});
  }
}


