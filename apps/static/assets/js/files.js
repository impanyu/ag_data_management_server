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





for(var i = 0; i < current_path_components.length; i++){
  path += current_path_components[i];
  item_html='<li class="breadcrumb-item"><a href="/files.html?current_path='+path+'">'+current_path_components[i]+'</a></li>'
  path += "/";
  item_node = htmlToElement(item_html);
  $("#pwd")[0].appendChild(item_node);
}


document.querySelector("#upload_dir").onchange=function(){
//form[0].requestSubmit();
//form[0].submit();
files = this.files;
upload();
this.value="";


};

document.querySelector("#upload_file").onchange=function(){

files = this.files;
upload();
this.value="";

};


function upload(){
var form_data = new FormData();
form_data.append("current_path",current_path);

for(var i=0;i<files.length;i++){
  form_data.append("files",files[i]);
  form_data.append("paths",files[i]["webkitRelativePath"]);
  console.info(files[i]["webkitRelativePath"]);

}


 $.ajax({
            method: "post",
            processData: false,
            contentType: false,
            cache: false,
            url: "/upload_file",
            data: form_data,
            enctype: "multipart/form-data",
            success: function (data) {
                alert(data);
                $("#file_list")[0].innerHTML="";
                get_file_list();
            }
        });

}



function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

get_file_list();
get_meta_data();


function get_file_list(){
 /*
  $("#file_list")[0].innerHTML="";
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
  */


  $.post("/file_system",
        {
          current_path: current_path,
          /*
          search_box: document.querySelector("#search_box").value,
          category: document.querySelector("#category").value,
          mode: mode,
          format: format,
          label: label,
          time_range: [document.querySelector("#start_date").value,document.querySelector("#end_date").value],
          bounding_box: [document.querySelector("#southwest").value, document.querySelector("#northeast").value]
          */


        },
        function(data, status){
          //console.info(data);
          data=JSON.parse(data);
          subdomains=[];
          times=[];

          //draw all the data & files in current_path on google map based
          data_points = data["data_points"];
          console.info(data_points)
          draw_points(data_points);


          for(var i=0;i<data['dirs'].length;i++){
            dir=data["dirs"][i];

            item_html =  '<tr><td scope="row"><div class="media align-items-center"><div class="media-body"><i class="ni ni-folder-17 text-primary"></i><span class="name mb-0 text-sm"> <a href="/files.html?current_path='+current_path+'/'+dir["dir_name"] +'">&nbsp; ' +dir["dir_name"]+
            '</a></span> </div></div></td>" + "<td class="budget">'+dir["created_time"]+'</td>"' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+dir["accessed_time"]+'</span></span></td>' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+dir["size"]+'</span></span></td>' +
                   '<td> <div class="avatar-group"> <a href="#" class="avatar avatar-sm rounded-circle" data-toggle="tooltip" data-original-title='+user+'><img alt="Image placeholder" src="/static/assets/img/theme/react.jpg"></a></div></td>' +
                   '<td ><div class="dropdown"><a class="btn btn-sm btn-icon-only text-light" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></a>'+
                   '<div class="dropdown-menu dropdown-menu-right dropdown-menu-arrow">'+
                   '<a class="dropdown-item" href="#" id="'+i+'_delete">Delete</a>'+
                   '</div> </div></td></tr>';
            item_node = htmlToElement(item_html);
            $("#file_list")[0].appendChild(item_node);

            $("#"+i+"_delete").click(function(){
               file_name = data["dirs"][parseInt(this.id.split("_")[0])]["dir_name"];

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


            $("#"+data["dirs"][i]["dir_name"]+"_add_domain").click(function(){
              subdomain=this.id.split("_")[3];
              time=this.id.split("_")[5];
              console.info(this.id.split("_")[3]);

               $.post("/domain",
                    {
                      subdomain: subdomain,
                      time: time//data["dirs"][i]["dir_name"].split("_")[5]
                    },
                    function(data, status){

                    });

            });


            function callbackClosure(i, callback) {
              return function() {
                return callback(i);
              }
            }

            $("#"+data["dirs"][i]["dir_name"]+"_canopy_height").click(function(){
              dir_name= this.id.substr(0,this.id.length-"_canopy_height".length);

               $.post("/canopy_height",
                    {
                       dir_name :dir_name,
                       subdomain: "spidercam_"+this.id.split("_")[3],
                       time: this.id.split("_")[5]

                    },
                    function(data, status){

                    });

            });

            $("#"+data["dirs"][i]["dir_name"]+"_canopy_coverage_and_temperature").click(function(){
              dir_name= this.id.substr(0,this.id.length-"_canopy_coverage_and_temperature".length);


               $.post("/canopy_coverage_and_temperature",
                    {
                       dir_name :dir_name,
                       subdomain: "spidercam_"+this.id.split("_")[3],
                       time: this.id.split("_")[5]

                    },
                    function(data, status){

                    });

            });

          }


          //for(file of data.files){
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




    });
}

meta_data_options = {"category":["Genotype","Phenotype","Soil","Atmosphere"],
                   "mode":["Folder","File","Tool","Model"],
                   "format":["Image","Shape","CSV","Spreadsheet","Python","R","Matlab"],
                   "label":["Spidercam","ENREC","Wheat"]};


meta_data={};
function remove_meta_data_option(self){
   removed_label = self.previousSibling.innerHTML;
   current_labels.delete(removed_label);
   parent = self.parentNode;
   grand_parent = parent.parentNode;
   grand_parent.removeChild(parent);
}

function update_meta(){
  meta_data = {};
  category = [];
  category_options = document.querySelector("#category").options;
    for (var i =0; i<category_options.length; i++){
     if(category_options[i].selected)
        category.push(category_options[i].value);

  }
  meta_data["category"] = category;


   mode = [];
  mode_options = document.querySelector("#mode").options;
  for (var i =0; i<mode_options.length; i++){
     if(mode_options[i].selected)
        mode.push(mode_options[i].value);
  }
   meta_data["mode"] = mode;

  format = [];
  format_options = document.querySelector("#format").options;
  for (var i =0; i<format_options.length; i++){
     if(format_options[i].selected)
        format.push(format_options[i].value);
  }
  meta_data["format"] = format;

  label = [];
  label_options = document.querySelector("#label").querySelectorAll("div");
  for (var i =0; i<label_options.length; i++){
        label.push(label_options[i].querySelector("span").innerHTML);
  }
  meta_data["label"] = label;


  if(document.querySelector("#toggle-switch").checked)
    meta_data["public"] = "False";
   else
     meta_data["public"] = "True";

    meta_data["time_range"] = {"start":document.querySelector("#start_date").value, "end":document.querySelector("#end_date").value};
    meta_data["spatial_range"] = {"southwest":document.querySelector("#southwest").value, "northeast":document.querySelector("#northeast").value};
    meta_data["other_meta"] = document.querySelector("#other_meta").value;

    $.ajax({
         type: "POST",
         url:"/update_meta",
         data:JSON.stringify({
          current_path: current_path,
          meta_data: meta_data

        }),
        contentType: "application/json",
        success: function(data, status){
          //alert("meta data updated");

  }});


}

labels= ["Spidercam","ENREC","Wheat"];
current_labels = new Set();
function get_meta_data(){
    $.post("/meta_data",
        {
          current_path: current_path
         },
         function(data, status){
          //console.info(data);
          meta_data=JSON.parse(data);
          console.info(meta_data);

          for(meta_key in meta_data){
             meta_value = meta_data[meta_key];
             if (meta_key == "subdirs" || meta_key =="abs_path" )
              continue;

              else if (meta_key == "mode" || meta_key == "category" || meta_key == "format"){
                 if(meta_value.length == 0)
                   continue;
                document.querySelector("#"+meta_key).querySelector("option[value="+meta_value[0]+"]").selected=true;
              }

              else if (meta_key == "time_range"){
                //if(meta_value["start"] == "01/01/2030 00:00:00" and meta_value["end"] == "01/01/2030 00:00:00")
                  //continue;
                document.querySelector("#start_date").value = meta_value["start"].substr(0,10);
                document.querySelector("#end_date").value = meta_value["end"].substr(0,10);

              }

              else if (meta_key == "spatial_range"){
                //if(meta_value["northeast"]["lat"] == "0" and meta_value["northeast"]["lng"] == "-180")
                 // continue;
                document.querySelector("#northeast").value = "("+meta_value["northeast"]["lat"]+","+meta_value["northeast"]["lng"]+")";

                document.querySelector("#southwest").value = "("+meta_value["southwest"]["lat"]+","+meta_value["southwest"]["lng"]+")";

              }

             else if  (meta_key == "label"){
                         label_html = "";
                         label_option_html = "";
                         current_labels = new Set(meta_value);


                              for (i in meta_value){
                                 label_html += '<div class ="meta_option">'+'<span>'+meta_value[i]+'</span>'+
                                 '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16" onclick="remove_meta_data_option(this)">'+
                                 '<path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>'+
                                 '</svg>' + ',' +'</div>';
                              }
                             document.querySelector("#label").innerHTML = label_html;


                             for(j in labels){

                               label_option_html += '<li ><span onclick="add_meta_data_option(this)" style="display:block;padding:3px 20px;">'+ labels[j] +'</span></li>';
                               }
                              document.querySelector("#label_option").innerHTML = label_option_html;

                 }
             else if (meta_key == "public"){
                 console.info(meta_value);
                  if(meta_value == "False"){
                     document.querySelector("#toggle-switch").checked = true;
                     document.getElementById("privilege").innerHTML = "Private Data";
                     }
                  else{
                     document.querySelector("#toggle-switch").checked = false;
                     document.getElementById("privilege").innerHTML = "Public Data";
                     }
             }

             else{
                document.querySelector("#other_meta").value += meta_key + ": "+ JSON.stringfy(meta_value) + "\n";
             }

          }





         });

}

// Get the toggle switch element
var toggleSwitch = document.getElementById("toggle-switch");

// Get the content element
var content = document.getElementById("privilege");

// Add an event listener to the toggle switch
toggleSwitch.addEventListener("change", function() {
  if (toggleSwitch.checked) {
    // Show the content
    content.innerHTML = "Private Data";
  } else {
    // Hide the content
   content.innerHTML = "Public Data"
  }
});

document.querySelector("#navbar-search-main").style.display="none";

map_displayed = "map";

function  add_meta_data_option(self){
  new_label=self.innerHTML;

  //new_label=this.querySelector("a").innerHTML;
   if (current_labels.has(new_label))
      return;

   label_html = '<div class ="meta_option">'+'<span>'+new_label+'</span>'+
                                 '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16" onclick="remove_meta_data_option(this)">'+
                                 '<path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>'+
                                 '</svg>' + ',' +'</div>';
   console.info(label_html);
   document.querySelector("#label").innerHTML =  document.querySelector("#label").innerHTML+label_html;
   current_labels.add(new_label);
}


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
            $(this).datepicker();
  });



