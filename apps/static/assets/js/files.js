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


meta_data={};
suffix = current_path.split(".")[current_path.split(".").length-1];
labels= ["Spidercam", "ENREC", "Wheat", "Crop", "Weather", "GIS", "Application", "UAV", "IoT", "Farm", "Machinery", "Disease", "Pest", "Fertilizer", "Water", "Nitrogen", "Cattle"];
current_labels = new Set();
document.querySelector("#other_meta").value ="";

document.querySelector("#file_content").style.display="none";
if(current_path.indexOf(".")!=-1){
  document.querySelector("#preloader2").style.display="flex";
  document.querySelector("#preloader5").style.display="flex";
} 
get_meta_and_content();
current_col = "";
current_band = "";
file_content ="";
file_changed = false;

entry_point = "";
args = {};


selected_collection = "";
selected_file_path = "";
set_collections_overlay();


set_create_file_overlay();
set_create_folder_overlay();
set_warning_overlay();
set_file_system_overlay();
set_delete_file_overlay()
previous_selected_file = null;
deleted_file_path = "";

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

    document.ElementById("attr").value = file_name.substr(0,file_name.length-file_name.split(".")[file_name.split(".").length-1].length-1);



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


document.querySelector("#upload_dir").onchange=async function(){
//form[0].requestSubmit();
//form[0].submit();
files = this.files;
webkitEntires = this.webkitEntries;
console.info(files.length);
await upload();
this.value="";


};

document.querySelector("#upload_file").onchange=async function(){

files = this.files;
webkitEntires = this.webkitEntries;
console.info(webkitEntires);
await upload();
this.value="";

};





function upload(){
return new Promise(function(resolve,reject){

var form_data = new FormData();
form_data.append("current_path",current_path);

if(files.length == 0) {//should create a new folder, but currently do not allow
     //actually if folder is empty, onchange will never be called, so the control flow will not reach here
     //still need to find ways to upload empty folders
      alert("Empty Folder!!!");
      resolve();
       return;
}
if(files[0]["webkitRelativePath"]== ""){//upload a file
    if(current_files_names.indexOf(files[0]["name"])!=-1){
       alert("File Exists!!!");
       resolve();
       return;
    }
}

else{//upload a folder
    if(current_folders_names.indexOf(files[0]["webkitRelativePath"].split("/")[0])!=-1){
      alert("Folder Exists!!!");
      resolve();
      return;

  }
}


for(var i=0;i<files.length;i++){


  form_data.append("files",files[i]);
  form_data.append("paths",files[i]["webkitRelativePath"]);
  console.info(files[i]["webkitRelativePath"]);


}

$('#preloader3')[0].style.display = "block";
 $.ajax({

                 xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(evt) {
                            if (evt.lengthComputable) {
                                var percentComplete = evt.loaded / evt.total;
                                //console.info(percentComplete);
                                //$('#preloader3').text('Uploading: ' + Math.round(percentComplete * 100) + '%');
                                if (percentComplete < 0.7)
                                    $('#preloader3')[0].style.width = Math.round(percentComplete * 100) + '%';
                                else
                                     $('#preloader3')[0].style.width = Math.round(((percentComplete-0.7)*0.8+0.7) * 100) + '%';
                            }
                        }, false);
                        return xhr;
                    },
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
                $('#preloader3')[0].style.width =  '100%';


                get_file_list();
                $('#preloader3')[0].style.display = "none";
            }
        });

      resolve();

    });
}



function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}



function set_create_folder_overlay(){
        const create_folder_overlay = document.querySelector('#create_folder_overlay');

        create_folder_overlay.addEventListener('click', function(event) {
            this.style.display  = "none";
        });

        const create_folder_tab = document.querySelector('#create_folder_tab');

        create_folder_tab.addEventListener('click', function(event) {
           event.stopPropagation();
        });


        const create_folder_button = document.querySelector('#create_folder_button');

        create_folder_button.addEventListener('click', function(event) {

           new_folder_name = document.querySelector("#new_folder_name").value;
           create_folder(new_folder_name);
        });


        const cancel_create_folder_button = document.querySelector('#cancel_create_folder_button');

        cancel_create_folder_button.addEventListener('click', function(event) {
           create_folder_overlay.style.display  = "none";
        });

        const create_folder_li = document.querySelector('#create_folder_li');

        create_folder_li.addEventListener('click', function(event) {
           create_folder_overlay.style.display  = "flex";
        });
}


function set_create_file_overlay(){

    const create_file_overlay = document.querySelector('#create_file_overlay');

    create_file_overlay.addEventListener('click', function(event) {
        this.style.display  = "none";
    });

    const create_file_tab = document.querySelector('#create_file_tab');

    create_file_tab.addEventListener('click', function(event) {
       event.stopPropagation();
    });


    const create_file_button = document.querySelector('#create_file_button');

    create_file_button.addEventListener('click', function(event) {

       new_file_name = document.querySelector("#new_file_name").value;
       create_file(new_file_name);
    });


    const cancel_create_file_button = document.querySelector('#cancel_create_file_button');

    cancel_create_file_button.addEventListener('click', function(event) {
       create_file_overlay.style.display  = "none";
    });

    const create_file_li = document.querySelector('#create_file_li');

    create_file_li.addEventListener('click', function(event) {
       create_file_overlay.style.display  = "flex";
    });

}

function set_delete_file_overlay(){

    const delete_file_overlay = document.querySelector('#delete_file_overlay');

    delete_file_overlay.addEventListener('click', function(event) {
        this.style.display  = "none";
    });

    const delete_file_tab = document.querySelector('#delete_file_tab');

    delete_file_tab.addEventListener('click', function(event) {
       event.stopPropagation();
    });


    const delete_file_button = document.querySelector('#delete_file_button');

    delete_file_button.addEventListener('click', function(event) {

        $.post("/delete_file",
                      {
                        file_path : deleted_file_path
                        //file_name: file_name
                      },
                      function(data, status){
                          $("#file_list")[0].innerHTML="";
                          get_item_list();
                          alert(data);
                      });
         delete_file_overlay.style.display  = "none";


    });


    const cancel_delete_file_button = document.querySelector('#cancel_delete_file_button');

    cancel_delete_file_button.addEventListener('click', function(event) {
       delete_file_overlay.style.display  = "none";
    });



}


function set_warning_overlay(){

    const warning_overlay = document.querySelector('#warning_overlay');

    warning_overlay.addEventListener('click', function(event) {
        this.style.display  = "none";
    });

    const warning_tab = document.querySelector('#warning_tab');

    warning_tab.addEventListener('click', function(event) {
       event.stopPropagation();
    });


    const warning_button = document.querySelector('#warning_button');

    warning_button.addEventListener('click', function(event) {
           warning_overlay.style.display = "none";
    });

}

function display_warning_overlay(warning_message){
    document.querySelector("#warning_message").innerHTML = warning_message;
    warning_overlay.style.display = "flex";


}

function set_file_system_overlay(){

    const file_system_overlay = document.querySelector('#file_system_overlay');

    file_system_overlay.addEventListener('click', function(event) {
        this.style.display  = "none";
        document.body.style.overflow = "auto";
    });

    const file_system_tab = document.querySelector('#file_system_tab');

    file_system_tab.addEventListener('click', function(event) {
       event.stopPropagation();
    });


    const file_system_button = document.querySelector('#file_system_button');

    file_system_button.addEventListener('click', function(event) {
           file_system_overlay.style.display = "none";
           document.body.style.overflow = "auto";
    });

    document.querySelector("#file_system_tab").addEventListener('scroll',function(event){
       // event.stopPropagation();
         //event.preventDefault();

    });

}





function create_folder(new_folder_name){
    $.ajax({
            type: "POST",

            url: "/create_folder",
            data: {
               current_path: current_path,
               new_folder_name: new_folder_name
            },
            success: function (data) {
                console.info(data);
                $("#file_list")[0].innerHTML="";
                create_folder_overlay.style.display  = "none";
                document.querySelector("#new_folder_name").value = "New Folder";

                get_file_list();
            }
        });

}


function create_file(new_file_name){
    $.ajax({
            type: "POST",

            url: "/create_file",
            data: {
               current_path: current_path,
               new_file_name: new_file_name
            },
            success: function (data) {
                console.info(data);
                $("#file_list")[0].innerHTML="";
                create_file_overlay.style.display  = "none";
                document.querySelector("#new_file_name").value = "New File";

                get_file_list();
            }
        });

}




function toggle_tool_panel(){
   if(document.querySelector("#tool_panel").style.height == "0px"){
     document.querySelector("#tool_panel").style.height = (document.querySelector("#tool_panel_container").offsetHeight + 450)+"px";
     document.querySelector("#tool_panel").style.paddingTop = "1.25rem";
     document.querySelector("#tool_panel").style.paddingBottom = "1.25rem";

     }
    else{
     document.querySelector("#tool_panel").style.height = "0px";
     document.querySelector("#tool_panel").style.paddingTop = "0rem";
     document.querySelector("#tool_panel").style.paddingBottom = "0rem";
     }
}



function set_tool_panel(){
  document.querySelector("#tool_panel_tab").style.display = "block";
  document.querySelector("#tool_panel_container").innerHTML = "";
  if(current_path.indexOf(".")==-1){ //folder
           document.querySelector("#tool_panel_container").innerHTML +='<div class="row align-items-center py-4" >'+

                            '<div class="col-lg-3 col-12">'+
                             '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>Program Entry Point</b></label>'+
                        '</div>'+
                         '<div class="col-lg-7 col-12">'+
                             '<input class="form-control"   type="text" value="Program Entry Point" id="arg_entry_point" onclick="display_file_selection(\'entry_point\',\''+ current_path + '\')"  >'+
                        '</div></div>'
           if(meta_data["entry_point"])
               document.querySelector("#entry_point").value = meta_data["entry_point"];

  }

  else{
    document.querySelector("#tool_panel_container").innerHTML +='<div class="row align-items-center py-4" >'+
                         '<div class="col-lg-3 col-12">'+
                             '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>Program Entry Point</b></label>'+
                        '</div>'+
                         '<div class="col-lg-7 col-12">'+
                             '<input class="form-control" id="arg_entry_point"  type="text" value="/'+ current_path+'" disabled >'+
                        '</div></div>'

  }
  document.querySelector("#tool_panel_container").innerHTML +='<div class="row align-items-center py-4" >'+
  '<div class="col-lg-3 col-12">'+
      '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>Execution Environment</b></label>'+
 '</div>'+
  '<div class="col-lg-7 col-12">'+


 '<select class="form-control" aria-label="Default select example" id="exe_env">'+
 '<option selected value="default">Default</option>'+
 '<option value="python_regular">Python Regular</option>'+
 '<option value="python_ag">Python Agriculture</option>'+
 '<option value="matlab">Matlab</option>'+
  '</select>'+
 '</div></div>'






  if(meta_data["args"]){
      for(arg in meta_data["args"]){
         arg_type =meta_data["args"][arg];
         args[arg] = arg_type;
          if(arg_type == "File" || arg_type == "Directory"){
          document.querySelector("#tool_panel_container").innerHTML +='<div class="row align-items-center py-4" id="arg_container_'+arg+'">'+

                            '<div class="col-lg-3 col-12">'+
                             '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>'+arg+'</b></label>'+
                        '</div>'+
                         '<div class="col-lg-7 col-6">'+
                             '<input class="form-control"  onclick="display_file_selection(\''+ arg  +'\',\''+user+'/ag_data\')"  type="text" value="Specify arguments: '+arg +'" id="arg_'+arg+'" >'+
                        '</div>'+
                          '<div class="col-lg-2 col-6">'+
                                    '<div href="#" class="btn btn-lg btn-danger"   id="remove_arg_'+arg+'"  onclick="remove_tool_arg(this)">'  +
                                      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="20" height="20">' +

                                      ' <path d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z" fill="#FFFFFF"/>' +
                                   ' </svg>'+

                             '</div>'  +
                         '</div>' +

                        '</div>';

            }
             else{
             document.querySelector("#tool_panel_container").innerHTML +='<div class="row align-items-center py-4" id="arg_container_'+arg+'">'+

                            '<div class="col-lg-3 col-12">'+
                             '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>'+arg+'</b></label>'+
                        '</div>'+
                         '<div class="col-lg-7 col-6">'+
                             '<input class="form-control"  type="text" value="Specify arguments: '+arg +'" id="arg_'+arg+'" >'+
                        '</div>'+
                          '<div class="col-lg-2 col-6">'+
                                    '<div href="#" class="btn btn-lg btn-danger"   id="remove_arg_'+arg+'"  onclick="remove_tool_arg(this)">'  +
                                      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="20" height="20">' +

                                      ' <path d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z" fill="#FFFFFF"/>' +
                                   ' </svg>'+

                             '</div>'  +
                         '</div>' +

                        '</div>';

             }
               //document.querySelector("#arg_"+arg).addEventListener("click",function(){display_file_selection(arg,user);});

           arg_type = meta_data["args"][arg];


      }

  }



      button_run_html= '<div class="row align-items-center " id="run_tool_container">'+
                  '<div class="col-12 col-lg-12 text-right">'+
                     '<a  class="btn btn-lg btn-primary" onclick="run_tool()" id = "run_tool"  style="color:white">Run</a>'+
                 '</div>'+
           '</div>'

     button_run = htmlToElement(button_run_html);

    document.querySelector("#tool_panel_container").appendChild(button_run);

}

function run_tool(){

  document.querySelector("#run_tool").onclick = "";
  //first update meta data
  new_meta_data = {};
  new_meta_data["entry_point"] = document.querySelector("#arg_entry_point").value;
  new_meta_data["args"] = args;

      $.ajax({
         type: "POST",
         url:"/update_meta",
         data:JSON.stringify({
          current_path: current_path,
          meta_data: new_meta_data

        }),
        contentType: "application/json",
        success: function(data, status){
          //console.info(data);
          console.info("meta data updated");
          //alert("meta data updated");

  }});

   arg_values ={};
   for(arg in args){
       arg_values[arg] = document.querySelector("#arg_"+arg).value;
   }

   exe_env = document.querySelector("#exe_env").value;

  //then send run tool request
       $.ajax({
         type: "POST",
         url:"/run_tool",
         data:JSON.stringify({
          entry_point: new_meta_data["entry_point"],
          exe_env: exe_env,
          arg_values: arg_values,
          arg_types : args

        }),
        contentType: "application/json",
        success: function(data, status){
          //alert("meta data updated");
          console.info(data);
          console.info("Program starts running.")
          display_warning_overlay("Program starts running.");
          document.querySelector("#run_tool").onclick = run_tool;

  }});

}

function remove_tool_arg(self){
  arg_name = self.id.split("_")[2];
  arg_container_name = "#arg_container_"+arg_name;
  arg_container = document.querySelector(arg_container_name);
  document.querySelector("#tool_panel_container").removeChild(arg_container);
  delete args[arg_name];

}

function add_tool_arg(){
   arg_name = document.querySelector("#arg_name").value.replace(" ","_").replace(".","_");
   arg_type = document.querySelector("#arg_type").value;
   if(arg_name in args){
         display_warning_overlay("Argument: <span style='color:red'>"+arg_name+"</span> already exists!");
         return;
   }
   //document.querySelector("#tool_panel_container").innerHTML = document.querySelector("#tool_panel_container").innerHTML.substr(0,document.querySelector("#tool_panel_container").innerHTML.length - button_run.length);
  document.querySelector("#tool_panel_container").removeChild(button_run);
         if(arg_type == "File" || arg_type == "Directory"){
               console.info(document.querySelector("#arg_"+arg_name));

                arg_container = htmlToElement('<div class="row align-items-center py-4" id="arg_container_'+arg_name+'">'+

                            '<div class="col-lg-3 col-12">'+
                             '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>'+arg_name+'</b></label>'+
                        '</div>'+
                         '<div class="col-lg-7 col-6">'+
                             '<input class="form-control" onclick="display_file_selection(\''+ arg_name  +'\',\''+user+'/ag_data\')" type="text" value="Specify arguments: '+arg_name +'" id="arg_'+arg_name+'">'+
                        '</div>'+
                          '<div class="col-lg-2 col-6">'+
                                    '<div href="#" class="btn btn-lg btn-danger"   id="remove_arg_'+arg_name+'"  onclick="remove_tool_arg(this)">'  +
                                      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="20" height="20">' +

                                      ' <path d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z" fill="#FFFFFF"/>' +
                                   ' </svg>'+

                             '</div>'  +
                         '</div>' +

                        '</div>');
                //document.querySelector("#tool_panel_container").innerHTML +=;

         }
         else{
             arg_container =htmlToElement('<div class="row align-items-center py-4" id="arg_container_'+arg_name+'">'+

                            '<div class="col-lg-3 col-12">'+
                             '<label class="form-check-label"  style="width:100%;margin-bottom: 15px"><b>'+arg_name+'</b></label>'+
                        '</div>'+
                         '<div class="col-lg-7 col-6">'+
                             '<input class="form-control"  type="text" value="Specify arguments: '+arg_name +'" id="arg_'+arg_name+'">'+
                        '</div>'+
                          '<div class="col-lg-2 col-6">'+
                                    '<div href="#" class="btn btn-lg btn-danger"   id="remove_arg_'+arg_name+'"  onclick="remove_tool_arg(this)">'  +
                                      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="20" height="20">' +

                                      ' <path d="M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z" fill="#FFFFFF"/>' +
                                   ' </svg>'+

                             '</div>'  +
                         '</div>' +

                        '</div>');


         }
         document.querySelector("#tool_panel_container").appendChild(arg_container);
         args[arg_name] = arg_type;
         document.querySelector("#tool_panel_container").appendChild(button_run);
         document.querySelector("#tool_panel").style.height = document.querySelector("#tool_panel_container").offsetHeight + 450 + "px";

}

select_file_names = [];

function display_file_selection(arg_name,path){

   console.info("display_file_selection");
   console.info(arg_name);
   $("#file_system_overlay")[0].style.display = "flex";
   document.body.style.overflow = "hidden";
   $("#file_list_in_overlay")[0].innerHTML = "";

    $.get("/meta_data",
        {
          current_path: path
         },
         function(data, status){
            selection_meta_data=JSON.parse(data);
            sub_dirs = selection_meta_data["subdirs"];
            file_system_overlay_path_components = selection_meta_data["abs_path"].split("/");
            path = "";
            $("#file_system_overlay_path")[0].innerHTML = "";
            for(var i = 2; i < file_system_overlay_path_components.length; i++){
                  path += file_system_overlay_path_components[i];
                  item_html='<li class="breadcrumb-item"><a style="color:#5e72e4;" class="file_system_overlay_path_component" onclick="display_file_selection(\''+ arg_name  +'\',\''+path+'\')">'+file_system_overlay_path_components[i]+'</a></li>'
                  path += "/";
                  item_node = htmlToElement(item_html);

                  $("#file_system_overlay_path")[0].appendChild(item_node);
             }




           select_file_names = [];
            for (var i =0;i<sub_dirs.length;i++){

                   sub_dir = sub_dirs[i];
                   console.info(sub_dir);
                   sub_dir_name = sub_dir.split("/")[sub_dir.split("/").length-1];
                   select_file_names.push(sub_dir_name);

                   if(sub_dir_name.indexOf(".") != -1){//file
                     item_html =  '<tr class="file_and_dir_item" id="file_item_'+i+'"  onclick="select_file(\''+ arg_name  +'\',\''+sub_dir.substr(6)+'\')" >'+
                       '<td scope="row"><div class="media align-items-center"><div class="media-body"><span class="name mb-0 text-sm">'+
                       ' <a >&nbsp; ' +sub_dir_name+
                       '</a></span> </div></div></td>"' +
                       '</tr>';

                   }
                   else{//dir
                       item_html =  '<tr class="file_and_dir_item" id="file_item_'+i+'" onclick="select_file(\''+ arg_name  +'\',\''+sub_dir.substr(6)+'\')" ondblclick="display_file_selection(\''+arg_name+'\',\''+sub_dir.substr(6)+'\')">'+
                       '<td scope="row"><div class="media align-items-center"><div class="media-body"><i class="ni ni-folder-17 text-primary"></i><span class="name mb-0 text-sm">'+
                       ' <a  >&nbsp; ' +sub_dir_name+
                       '</a></span> </div></div></td>"' +
                       '</tr>';

                   }
            item_node = htmlToElement(item_html);
            $("#file_list_in_overlay")[0].appendChild(item_node);

            }

         });

}



function select_file(arg_name,path){
    document.querySelector("#arg_"+arg_name).value = "/"+path;

    sub_dir_name = path.split("/")[path.split("/").length-1];

    i = select_file_names.indexOf(sub_dir_name);


    document.querySelector("#file_item_"+i).style.backgroundColor = "#69cfff";
    if(previous_selected_file && previous_selected_file!= document.querySelector("#file_item_"+i))
      previous_selected_file.style.backgroundColor = "";


    previous_selected_file = document.querySelector("#file_item_"+i);
    //document.querySelector(".file_and_dir_item").style.backgroundColor = "white";

}


async function get_meta_and_content(){
  /*await get_meta_data();

  if(meta_data["format"][0] == "Folder"){
    get_file_list();

    }
  else{
    get_file_content();
    document.querySelector("#file_table").style.display="none";
   }
   */

   if(current_path.indexOf(".")==-1){ //folder
    document.querySelector("#file_content").style.display="none";
     await get_meta_data();
     set_pipeline_panel();

     if(meta_data["mode"] == "Tool"){
        set_tool_panel();
        get_running_containers();
        document.querySelector("#running_containers_panel").style.display = "block";
     }

     get_file_list();

   }
   else{//file

      document.querySelector("#file_table").style.display="none";
      document.querySelector("#upload_file_button").style.display="none";
      document.querySelector("#upload_folder_button").style.display="none";
      document.querySelector("#create").style.display="none";
      document.querySelector("#file_content").style.display="none";
      await get_meta_data();

      set_pipeline_panel();
      if(suffix == "shp"){
        current_col =  meta_data["native"]["columns"][0];
     }
     else if(suffix == "tiff" || suffix == "tif"){ 
        current_band =  1;
     }

     if(meta_data["mode"] == "Tool"){
       set_tool_panel();
       get_running_containers();
        document.querySelector("#running_containers_panel").style.display = "block";

     }
      get_file_content();

   }

}


function set_pipeline_panel(){



        $.ajax({
         type: "POST",
         url:"/get_pipeline",
         data:{
          current_path: current_path
        },
        //contentType: "application/json",
        success: function(data, status){
           console.info(data);
          //console.info("meta data updated");
          //alert("meta data updated");
          graph = JSON.parse(data);

          draw_pipeline(graph);

  }});

  }



function draw_pipeline(graph){

  // Data for nodes and links
      nodes = [
        { id: 1, label: "A" },
        { id: 2, label: "B" },
        { id: 3, label: "C" },
      ];

      links = [
        { source: 1, target: 2, label: "a" },
        { source: 2, target: 3, label: "b" },
        { source: 3, target: 1, label: "c" },
      ];


  nodes = graph["nodes"];
  links = graph["links"];

  svg_width = document.querySelector("#pipeline_panel").offsetWidth;
  svg_height= 760;


   const svg = d3.select("#pipeline_svg");

      // Define arrow markers
      svg
          .attr("width", svg_width)
          .attr("height", 760)
        .append("defs")
        .selectAll("marker")
        .data(["end-arrow"])
        .enter()
        .append("marker")
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#888");



      // Create a simulation with nodes and links
      const simulation = d3
        .forceSimulation(nodes)
        .force(
          "link",
          d3.forceLink(links).id((d) => d.id).distance(250)
        )
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(svg_width / 2, svg_height / 2));


      // Draw links
      const link = svg
        .selectAll(".link")
        .data(links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke","#888")
        .style("stroke-width", 4); // Increase the edge thickness

      // Draw nodes
      const node = svg
        .selectAll(".node")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        //.attr("width", (d)=> d.label.length*10)
        //.attr("height", 20)
        //.attr("x",(d) => d.x)
        //.attr("y",(d) => d.y)
        .attr("r",30)
        .attr("fill", "#69b3a2")
         .attr("fill", (d) => {
                if (d.node_status == "current") {
                    return "red"; // Assign a specific color, e.g., red, to the special node
                }
                else if (d.node_status == "dead"){
                   return "#999";
                }
                else {
                    return "steelblue"; // Assign the default color to all other nodes
                }
      })
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

      // Add node labels
      const nodeLabels = svg
        .selectAll(".node-label")
        .data(nodes)
        .enter()
          .append("a") // Add an <a> element to wrap the node labels
        .attr("xlink:href", (d) => { if (d.label.indexOf("/")!=-1 || d.label == "/"+user) return "/files.html?current_path="+d.label.substr(1); else return "#"}) // Set the link URL based on the node data}
        .append("text")
        .attr("class", "node-label")
        .attr("text-anchor", "middle")
        .attr("dy", 0)
        .text((d) => d.label.split("/")[d.label.split("/").length-1])
        .attr("dominant-baseline", "central")
        .attr("font-size","14px")
        .attr("font-weight","bold");






             // Add link labels
      const linkLabels = svg
        .selectAll(".link-label")
        .data(links)
        .enter()
          .append("a") // Add an <a> element to wrap the node labels
        .attr("xlink:href", (d) => { if (d.label.indexOf("/")!=-1 || d.label == "/"+user) return "/files.html?current_path="+d.label.substr(1); else return "#"}) // Set the link URL based on the node data}
        .append("text")
        .attr("class", "link-label")
        .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", "12px") // Set the font size here
      .attr("font-weight", "bold") // Set the font weight to bold here
        .attr("dy", -10)
        .attr("fill","blue")
        .text((d) => d.label.split("/")[d.label.split("/").length-1]);








      // Update the position of the nodes, links, and labels on each tick of the simulation
      simulation.on("tick", () => {
        link
          .attr("x1", (d) => d.source.x)
          .attr("y1", (d) => d.source.y)
          .attr("x2", (d) => d.target.x)
          .attr("y2", (d) => d.target.y);

        node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

        nodeLabels
          .attr("x", (d) => d.x)
          .attr("y", (d) => d.y);

        linkLabels.attr("x", (d) => (d.source.x + d.target.x) / 2)
          .attr("y", (d) => (d.source.y + d.target.y) / 2);
      });

  function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}


}




function toggle_pipeline_panel(){
   if(document.querySelector("#pipeline_panel").style.height == "0px"){
     document.querySelector("#pipeline_panel").style.height = "800px";
     document.querySelector("#pipeline_panel").style.paddingTop = "1.25rem";
     document.querySelector("#pipeline_panel").style.paddingBottom = "1.25rem";

     }
    else{
     document.querySelector("#pipeline_panel").style.height = "0px";
     document.querySelector("#pipeline_panel").style.paddingTop = "0rem";
     document.querySelector("#pipeline_panel").style.paddingBottom = "0rem";
     }
}


function update_file(){
      $.ajax({
         type: "POST",
         url:"/update_file",
         data:JSON.stringify({
              current_path: current_path,
              new_content: file_content
          }),
        contentType: "application/json",
        success: function(data, status){
          //console.info(data);
          //alert("file updated");
           document.querySelector("#preloader").style.display = "none";

  }});

}

function move_file_or_folder(){

}

function copy_file_or_folder(){
}


function change_channel_dropdown(self){
 document.querySelector("#preloader2").style.display = "flex";
 document.querySelector("#file_content").style.display = "none";
 if(suffix == "shp"){

   current_col = self.innerHTML;

  }
 else if(suffix == "tif" || suffix == "tiff"){
  current_band = self.innerHTML;
  }

  get_file_content();
}

x={};
u = "";
file_format_names = {"txt":"plain_text","py":"python","m":"matlab","mlx":"matlab","r":"r","csv":"text","json":"json","xml":"xml","html":"html","prf":"plain_text","tfw":"plain_text"};

function get_file_content(){



if(suffix == "txt" || suffix == "py" || suffix == "m" || suffix == "mlx" || suffix == "r" || suffix == "csv" || suffix == "json" || suffix == "xml" || suffix=="html" || suffix == "prj" || suffix == "tfw"){
       $.ajax({
                url: '/get_file',
                type: 'POST',
                data: {current_path: current_path},
                xhrFields: {
                    responseType: 'text'
                },
                success: function(response,status,xhr) {
                  x=xhr;

                  document.querySelector("#channel_dropdown").style.display="none";
                   document.querySelector("#map_main").style.display="none";
                   document.querySelector("#opacity-slider-container").style.display="none";

                   document.querySelector("#file_content").style.display="block";


                  const contentType = xhr.getResponseHeader('Content-Type');
                   // Extract the filename from the Content-Disposition header
                   const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];


                     //create a text input area



                     const pre = document.createElement('pre');
                     document.querySelector("#file_content").appendChild(pre);
                     pre.setAttribute('id', 'editor');
                     pre.innerHTML = response;
                     file_content = response;

                      editor = ace.edit("editor");
                      editor.setTheme("ace/theme/ambiance");
                      editor.session.setMode("ace/mode/"+file_format_names[suffix]);

                      editor.session.on('change', function(delta) {
                            file_content = editor.getValue();
                            file_changed = true;
                       });

                       //check code change every 15s
                       setInterval(function(){
                            if(file_changed){
                                document.querySelector("#preloader").style.display = "block";
                                update_file();
                                file_changed = false;

                            }

                       },15000);


                     /*
                     code = document.createElement('code');

                     code.classList.add("language-python","line-numbers")
                     code.innerHTML = response;



                     pre.appendChild(code);


                     //hljs.highlightAll();
                       Prism.highlightAll();
                      */

                      document.querySelector("#preloader2").style.display="none";

                },
                error: function(xhr, status, error) {

                    console.error('Error retrieving file:', error);
                }
            });
}

else if(suffix == "tif" || suffix == "tiff" ){
             document.querySelector("#channel_list").innerHTML = "";
             document.querySelector("#dropdownMenuButton").innerHTML = "Band";
               for (band=1; band<=meta_data["native"]["bands"];band++){

                       document.querySelector("#channel_list").innerHTML +=  '<span class="dropdown-item"  onclick="change_channel_dropdown(this)" id="channel_dropdown_item_'+band+'">'+band+'</span>';
                  }

                 if (meta_data["native"]["bands"] == 4){
                 document.querySelector("#channel_list").innerHTML += '<span class="dropdown-item"  onclick="change_channel_dropdown(this)" id="channel_dropdown_item_RGBA">RGBA</span>';
                 }

          document.querySelector("#channel_dropdown_item_"+current_band).style.backgroundColor = "#87CEEB";

            $.ajax({
                url: '/get_file',
                type: 'POST',
                data: {current_path: current_path, band:current_band},
                xhrFields: {
                    responseType: 'blob'
                },
                success: function(response,status,xhr) {
                  x=xhr;
                  document.querySelector("#file_content").style.display="block";
                  const contentType = xhr.getResponseHeader('Content-Type');
                   // Extract the filename from the Content-Disposition header
                   const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];
                   const url = window.URL.createObjectURL(response);

                   if (meta_data["spatial_range"]["northeast"]["lat"] == "0" &&  meta_data["spatial_range"]["northeast"]["lng"] == "-180"){
                   //no geospatial info, only render a img

                   // Create a URL object from the blob response
                         const img = document.createElement('img');
                         img.src = url;
                         img.style.width="100%";
                         document.querySelector("#file_content").appendChild(img);
                         document.querySelector("#channel_dropdown").style.display="none";
                          document.querySelector("#map_main").style.display="none";
                           document.querySelector("#opacity-slider-container").style.display="none";
                   }

                   //has geospatial info, render on map
                   else{
                          north = parseFloat(meta_data["spatial_range"]["northeast"]["lat"]);
                          south = parseFloat(meta_data["spatial_range"]["southwest"]["lat"]);
                          east = meta_data["spatial_range"]["northeast"]["lng"];
                          west = meta_data["spatial_range"]["southwest"]["lng"];

                          const imageBounds = {
                              north: north,
                              south: south,
                              east:  east,
                              west:  west
                          };

                        new_center = new google.maps.LatLng((north+south)/2,(east+west)/2);
                        map_main.setCenter(new_center);
                        map_main.setZoom(15);
                        console.info(url);

                        // Iterate over all overlays added to the map
                            map_main.overlayMapTypes.forEach((overlay) => {
                              // Check if the overlay is currently displayed on the map
                                    overlays.setMap(null);
                            });


                        const overlay = new google.maps.GroundOverlay(url, imageBounds);


                        overlay.setMap(map_main);

                       // Create opacity slider
                        const slider = document.getElementById('opacity-slider');
                        slider.addEventListener('input', () => {
                          const opacity = slider.value / 100;
                          overlay.setOpacity(opacity);
                        });
                   }
                   document.querySelector("#file_content").style.display="block";
                      document.querySelector("#preloader2").style.display="none";
                },
                error: function(xhr, status, error) {

                    console.error('Error retrieving file:', error);
                }
            });




}


else if (suffix == "png" || suffix == "jpg" || suffix == "jpeg"){
     $.ajax({
                url: '/get_file',
                type: 'POST',
                data: {current_path: current_path},
                xhrFields: {
                    responseType: 'blob'
                },
                success: function(response,status,xhr) {
                  x=xhr;
                  document.querySelector("#file_content").style.display="block";
                  const contentType = xhr.getResponseHeader('Content-Type');
                   // Extract the filename from the Content-Disposition header
                   const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];
                   const url = window.URL.createObjectURL(response);

                   if (meta_data["spatial_range"]["northeast"]["lat"] == "0" &&  meta_data["spatial_range"]["northeast"]["lng"] == "-180"){
                   //no geospatial info, only render a img

                   // Create a URL object from the blob response
                         const img = document.createElement('img');
                         img.src = url;
                         img.style.width="100%";
                         document.querySelector("#file_content").appendChild(img);
                         document.querySelector("#channel_dropdown").style.display="none";
                          document.querySelector("#map_main").style.display="none";
                           document.querySelector("#opacity-slider-container").style.display="none";

                   }

                   //has geospatial info, render on map
                   else{

                          document.querySelector("#channel_dropdown").style.display="none";

                          north = parseFloat(meta_data["spatial_range"]["northeast"]["lat"]);
                          south = parseFloat(meta_data["spatial_range"]["southwest"]["lat"]);
                          south = parseFloat(meta_data["spatial_range"]["southwest"]["lat"]);
                          east = meta_data["spatial_range"]["northeast"]["lng"];
                          west = meta_data["spatial_range"]["southwest"]["lng"];

                          const imageBounds = {
                              north: north,
                              south: south,
                              east:  east,
                              west:  west
                          };

                        new_center = new google.maps.LatLng((north+south)/2,(east+west)/2);
                        map_main.setCenter(new_center);
                        map_main.setZoom(15);
                        console.info(url);

                        const overlay = new google.maps.GroundOverlay(url, imageBounds);

                        overlay.setMap(map_main);

                       // Create opacity slider
                        const slider = document.getElementById('opacity-slider');
                        slider.addEventListener('input', () => {
                          const opacity = slider.value / 100;
                          overlay.setOpacity(opacity);
                        });
                   }
                   document.querySelector("#file_content").style.display="block";
                      document.querySelector("#preloader2").style.display="none";
                },
                error: function(xhr, status, error) {

                    console.error('Error retrieving file:', error);
                }
            });

}

else if (suffix == "shp"){
                document.querySelector("#channel_list").innerHTML = "";
               for (i in meta_data["native"]["columns"]){
                          col = meta_data["native"]["columns"][i];
                          document.querySelector("#channel_list").innerHTML +=  '<span class="dropdown-item"  onclick="change_channel_dropdown(this)" id="channel_dropdown_item_'+col+'">'+col+'</span>';
                  }
            document.querySelector("#channel_dropdown_item_"+current_col).style.backgroundColor = "#87CEEB";

            $.ajax({
                url: '/get_file',
                type: 'POST',
                data: {current_path: current_path, col:current_col},
                xhrFields: {
                    responseType: 'blob'
                },
                success: function(response,status,xhr) {
                  x=xhr;
                  document.querySelector("#file_content").style.display="block";
                  const contentType = xhr.getResponseHeader('Content-Type');
                   // Extract the filename from the Content-Disposition header
                   const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];
                   const url = window.URL.createObjectURL(response);

                   if (meta_data["spatial_range"]["northeast"]["lat"] == "0" &&  meta_data["spatial_range"]["northeast"]["lng"] == "-180"){
                   //no geospatial info, only render a img

                   // Create a URL object from the blob response
                         const img = document.createElement('img');
                         img.src = url;
                         img.style.width="100%";
                         document.querySelector("#file_content").appendChild(img);
                         document.querySelector("#channel_dropdown").style.display="none";
                          document.querySelector("#map_main").style.display="none";
                           document.querySelector("#opacity-slider-container").style.display="none";
                   }

                   //has geospatial info, render on map
                   else{
                          north = parseFloat(meta_data["spatial_range"]["northeast"]["lat"]);
                          south = parseFloat(meta_data["spatial_range"]["southwest"]["lat"]);
                          east = meta_data["spatial_range"]["northeast"]["lng"];
                          west = meta_data["spatial_range"]["southwest"]["lng"];

                          const imageBounds = {
                              north: north,
                              south: south,
                              east:  east,
                              west:  west
                          };

                        new_center = new google.maps.LatLng((north+south)/2,(east+west)/2);
                        map_main.setCenter(new_center);
                        map_main.setZoom(15);
                        console.info(url);

                        // Iterate over all overlays added to the map
                            map_main.overlayMapTypes.forEach((overlay) => {
                              // Check if the overlay is currently displayed on the map
                                    overlays.setMap(null);
                            });




                        const overlay = new google.maps.GroundOverlay(url, imageBounds);


                        overlay.setMap(map_main);

                       // Create opacity slider
                        const slider = document.getElementById('opacity-slider');
                        slider.addEventListener('input', () => {
                          const opacity = slider.value / 100;
                          overlay.setOpacity(opacity);
                        });
                   }
                   document.querySelector("#file_content").style.display="block";
                      document.querySelector("#preloader2").style.display="none";
                },
                error: function(xhr, status, error) {

                    console.error('Error retrieving file:', error);
                }
            });

}
/*
$.post("/get_file",
        {
          current_path: current_path
         }, function(data, status,xhr) {
          if (xhr.status == 200) {
             console.info(200);
             const contentType = xhr.getResponseHeader('Content-Type');
             // Extract the filename from the Content-Disposition header
             const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];

             const blob = new Blob([data], { type: contentType });
             const url = window.URL.createObjectURL(blob);
             const img = document.createElement('img');
             img.src = url;
             document.querySelector("#file_content").appendChild(img);


          }
       });
*/
}

function download_file_or_folder(){
/*
shapefile.open("/read_file?"+current_path)
  .then(source => source.read()
    .then(function log(result) {
      if (result.done) return;
          const shape = result.value;
    const coords = shape.geometry.coordinates;

    // Create a new Google Maps polygon for each shape
    const polygon = new google.maps.Polygon({
      paths: coords.map(coords => ({ lat: coords[1], lng: coords[0] })),
      map: map,
      strokeColor: "#FF0000",
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#FF0000",
      fillOpacity: 0.35,
    });

      console.log(result.value);
      return source.read().then(log);
    }))
  .catch(error => console.error(error.stack));
*/

$.ajax({
    url: '/download_file',
    type: 'POST',
    data: {current_path: current_path},
    xhrFields: {
        responseType: 'blob'
    },
    success: function(response,status,xhr) {
      const contentType = xhr.getResponseHeader('Content-Type');
       // Extract the filename from the Content-Disposition header
       const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];
        // Create a URL object from the blob response
        const url = window.URL.createObjectURL(response);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;//.substr(1,filename.length-2);
        a.click();
        console.info(a);

    },
    error: function(xhr, status, error) {

        console.error('Error retrieving file:', error);
    }
});


/*
        $.post("/get_file",
        {
          current_path: current_path
         }, function(data, status,xhr) {
          if (xhr.status == 200) {
                 x = xhr;
                 //console.info(data);
                 //console.info(xhr.getResponseHeader('Content-Disposition'));

                 const contentType = xhr.getResponseHeader('Content-Type');
                // Extract the filename from the Content-Disposition header
                const filename =xhr.getResponseHeader('Content-Disposition').split('filename=')[1];
                console.info(filename);
                 // Extract the filename from the Content-Disposition header using a regular expression
                 //const match = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(data);
                //const filename = decodeURIComponent(match[1].replace(/['"]/g, ''));

                // Trigger the download by creating an <a> element with a temporary href and click it
                //const blob = new Blob([data]);
                // const blob = new Blob([data], { type: contentType });
                blob = xhr.responseText;

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;//.substr(1,filename.length-2);
                a.click();
                console.info(a);
                //window.URL.revokeObjectURL(url);
              } else {
                console.error('Failed to download file');
              }
        }).fail(function() {
          console.error('Error downloading file');
        });
*/

}





function get_file_list(){
get_item_list();
return;
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
          console.info(data);
          subdomains=[];
          times=[];

          //draw all the data & files in current_path on google map based
          data_points = data["data_points"];
          current_files_names = [];
          current_folders_names = [];
          console.info(data_points)
          //draw_points(data_points);


          for(var i=0;i<data['dirs'].length;i++){
            dir=data["dirs"][i];
            current_folders_names.push(dir["dir_name"]);

            item_html =  '<tr class="file_and_dir_item"><td scope="row"><div class="media align-items-center"><div class="media-body"><i class="ni ni-folder-17 text-primary"></i><span class="name mb-0 text-sm"> <a href="/files.html?current_path='+current_path+'/'+dir["dir_name"] +'&dir=true">&nbsp; ' +dir["dir_name"]+
            '</a></span> </div></div></td>"' +
                   '"<td class="budget">'+dir["created_time"]+'</td>"' +
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
          current_files_names.push(file["file_name"]);

            item_html =  '<tr  class="file_and_dir_item"><td scope="row"><div class="media align-items-center"><div class="media-body"><span class="name mb-0 text-sm"> &nbsp;<a href="/files.html?current_path='+current_path+'/'+file["file_name"]+'&dir=false"> ' +file["file_name"]+
            '</a></span> </div></div></td>" + "<td class="budget">'+file["created_time"]+'</td>"' +
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


  if(document.querySelector("#privilege-toggle-switch").checked)
    meta_data["public"] = "False";
   else
     meta_data["public"] = "True";

  if(document.querySelector("#realtime-toggle-switch").checked)
    meta_data["realtime"] = "Realtime";
   else
     meta_data["realtime"] = "Non-Realtime";

    meta_data["time_range"] = {"start":document.querySelector("#start_date").value, "end":document.querySelector("#end_date").value};
    meta_data["spatial_range"] = {"southwest":document.querySelector("#southwest").value, "northeast":document.querySelector("#northeast").value};
    other_meta = document.querySelector("#other_meta").value;
    meta_data["introduction"] = document.querySelector('#introduction').value;

    for(k_v_pair of other_meta.split("\n") ){
        if (k_v_pair.indexOf(":")==-1)
         continue;
        console.info(k_v_pair);
        first_split_index = k_v_pair.indexOf(":");
        k = k_v_pair.substring(0,first_split_index);
        v = k_v_pair.substring(first_split_index+1);

        meta_data[k] = JSON.parse(v);
    }

    $.ajax({
         type: "POST",
         url:"/update_meta",
         data:JSON.stringify({
          current_path: current_path,
          meta_data: meta_data

        }),
        contentType: "application/json",
        success: function(data, status){
         console.info(data);
          alert("meta data updated");
          if(meta_data["mode"] == "Tool")
            set_tool_panel();
          else{
              document.querySelector("#tool_panel_tab").style.display = "none";
             document.querySelector("#tool_panel").style.height = "1px";
              toggle_tool_panel();
          }


  }});
}



function get_meta_data(){
   return new Promise(function(resolve,reject){
    $.get("/meta_data",
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
                 //console.info(meta_key);
                 //console.info(meta_value);
                document.querySelector("#"+meta_key).querySelector("option[value="+meta_value[0]+"]").selected=true;
              }

              else if (meta_key == "time_range"){
                if(meta_value["start"] == "01/01/2030 00:00:00" && meta_value["end"] == "01/01/2030 00:00:00")
                  continue;
                document.querySelector("#start_date").value = meta_value["start"].substr(0,10);
                document.querySelector("#end_date").value = meta_value["end"].substr(0,10);

              }

              else if (meta_key == "spatial_range"){
                if(meta_value["northeast"]["lat"] == "0"  &&  meta_value["northeast"]["lng"] == "-180")
                  continue;
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

                               label_option_html += '<li class="label_item_in_file_meta"><span onclick="add_meta_data_option(this)" style="display:block;padding:3px 20px;">'+ labels[j] +'</span></li>';
                               }
                              document.querySelector("#label_option").innerHTML = label_option_html;

                 }
             else if (meta_key == "public"){
                 console.info(meta_value);
                  if(meta_value == "False"){
                     document.querySelector("#privilege-toggle-switch").checked = true;
                     document.getElementById("privilege").innerHTML = "Private Data";
                     }
                  else{
                     document.querySelector("#privilege-toggle-switch").checked = false;
                     document.getElementById("privilege").innerHTML = "Public Data";
                     }
             }
             else if (meta_key == "realtime"){
                 console.info(meta_value);
                  if(meta_value == "Realtime"){
                     document.querySelector("#realtime-toggle-switch").checked = true;
                     document.getElementById("realtime").innerHTML = "Realtime Data";
                     }
                  else{
                     document.querySelector("#realtime-toggle-switch").checked = false;
                     document.getElementById("realtime").innerHTML = "Non-Realtime Data";
                     }
             }

             else if (meta_key == "native"){
                    for(k in meta_value)

                        document.querySelector("#native_meta").value += k+": "+JSON.stringify(meta_value[k])+ "\n";


                    //document.querySelector("#native_meta_panel").style.display = "block";
             }

             else if (meta_key == "introduction"){
                  document.querySelector("#introduction").value =  meta_value + "\n";
             }


             else{
                document.querySelector("#other_meta").value += meta_key + ": "+ JSON.stringify(meta_value) + "\n";
            //    document.querySelector("#other_meta").value += meta_key + ": "+ meta_value + "\n";
             }

          }







        resolve();

         }); });

}


function get_running_containers(){
 setInterval(function(){
                         $.ajax({
                            type: "POST",
                            url: "/get_running_containers",
                            data:{
                                    current_path: current_path
                            },
                            success: function (data) {
                            document.querySelector("#container_list").innerHTML = "";
                                console.info(data);
                                containers = JSON.parse(data);
                                 for(container of containers){

                                      document.querySelector("#container_list").innerHTML += '<tr>'+
                                         '<td scope="row" ><b>'+container["container_id"].substr(0,12)+'</b></td>'+
                                         '<td scope="row" ><b>'+container["image"]+'</b></td>'+
                                         '<td scope="row" ><b>'+container["status"]+'</b></td>'+
                                         '<td scope="row" ><b>'+container["running_time"]+'s</b></td>'+
                                          '</tr>';


                                 }


                            }
                        });

                  },5000);
}

// Get the toggle switch element
var privilege_toggle_switch = document.getElementById("privilege-toggle-switch");

// Get the content element
var privilege_content = document.getElementById("privilege");

// Add an event listener to the toggle switch
privilege_toggle_switch.addEventListener("change", function() {
  if (privilege_toggle_switch.checked) {
    // Show the content
    privilege_content.innerHTML = "Private Data";
  } else {
    // Hide the content
   privilege_content.innerHTML = "Public Data";
  }
});

// Get the toggle switch element
var realtime_toggle_switch = document.getElementById("realtime-toggle-switch");

// Get the content element
var realtime_content = document.getElementById("realtime");

// Add an event listener to the toggle switch
realtime_toggle_switch.addEventListener("change", function() {
  if (realtime_toggle_switch.checked) {
    // Show the content
    realtime_content.innerHTML = "Realtime Data";
  } else {
    // Hide the content
   realtime_content.innerHTML = "Non-Realtime Data";
  }
});



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





function init_map_main(){
  map_main = new google.maps.Map(
    document.getElementById("map_main"),
    {
      center: { lat: 40.897, lng: -96.644 },
      zoom: 11,
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
      fillColor: "#0000ff",
      fillOpacity: .6,
      strokeWeight: 3,
      clickable: false,
      editable: true,
      zIndex: 1,
    },
  });

 // drawingManager.setMap(map_main);

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


function toggle_meta_data_panel(){
   if(meta_data["mode"].indexOf("Tool") !=-1)
       meta_data_panel_height = "2000px";
   else
       meta_data_panel_height = "1800px";


   if(document.querySelector("#meta_data_panel").style.height == "0px"){
     document.querySelector("#meta_data_panel").style.height = meta_data_panel_height;
     document.querySelector("#meta_data_panel").style.paddingTop = "1.25rem";
     document.querySelector("#meta_data_panel").style.paddingBottom = "1.25rem";

     }
    else{
     document.querySelector("#meta_data_panel").style.height = "0px";
          document.querySelector("#meta_data_panel").style.paddingTop = "0rem";
     document.querySelector("#meta_data_panel").style.paddingBottom = "0rem";
     }
}




function get_item_list(){

  $.post("/file_system_virtual",
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
          console.info(data);
          document.querySelector("#preloader5").style.display="none";
          data=JSON.parse(data);
          console.info(data);
          subdomains=[];
          times=[];


          current_files_names = [];
          current_folders_names = [];
          //console.info(data_points)
          //draw_points(data_points);

          //for each user's root folder, add enreec testbed
          if(current_path.endsWith("ag_data")){
            data.push({"name":"ENREEC TestBed", "running": "False",  "abs_path" :"/data/"+current_path+"/ENREEC_Testbed", "native":{"created_time":"01/01/2020 00:00:00","access_time":"01/01/2020 00:00:00","size":"0"}})
          }
          //for(file of data.files){
          for(var i=0;i<data.length;i++){

          file=data[i]; //meta data for file or dir

          //if(file["mode"] == "Collection")
           // continue;

          if (file["name"].indexOf(".") == -1){
             icon =  '<i class="ni ni-folder-17 text-primary"></i>'
             current_folders_names.push(file["name"]);

             }
          else if (file["running"] == "True"){
              icon = '<div class="green-dot"></div>';
          }
          else if (file["running"] == "False"){
             icon = '<div class="red-dot"></div>';
          }
          else{
             icon = '';
             current_files_names.push(file["name"]);
         }

           if (file["abs_path"] == "/data/public/ag_data")
               tabs = "";
           else
               tabs = '<a class="dropdown-item"  id="'+i+'_file_delete">Delete</a>'+
                    '<a class="dropdown-item" id="'+i+'_move">Move</a>'+
                   '<a class="dropdown-item"  id="'+i+'_duplicate">Duplicate</a>'+
                   '<a class="dropdown-item" id="'+i+'_get_JD_authorization_code" href="/api/get_JD_authorization_code/?file_path='+encodeURIComponent(file["abs_path"])+'" >Connect to JD</a>'


            if (file["abs_path"] == current_path+"/ENREEC_Testbed"){

              item_html =  '<tr  class="file_and_dir_item" id="'+i+'_file_and_dir"><td scope="row"><div class="media align-items-center"><div class="media-body">'+icon+'<span class="name mb-0 text-sm"> &nbsp;<a href="/files.html?current_path='+file["abs_path"].substr(6)+
              '&dir=false"> ' +file["name"]+ '</a></span> </div></div></td>" + "<td class="budget">'+file["native"]["created_time"]+'</td>"' +
               '<td> <span class="badge badge-dot mr-4">  <span class="status">'+file["native"]["access_time"]+'</span></span></td>' +
               '<td> <span class="badge badge-dot mr-4">  <span class="status">'+file["native"]["size"]+'</span></span></td>' +
               '<td> <div class="avatar-group"> <a href="#" data-toggle="tooltip" data-original-title='+user+'>'+file['owner']+'</a></div></td>' +
               '<td ><div class="dropdown"><a class="btn btn-sm btn-icon-only text-light" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></a>'+
               '<div class="dropdown-menu dropdown-menu-right dropdown-menu-arrow">'+
               tabs+
               '<a class="dropdown-item" href="#" id="'+i+'_add_to_collection">Add to Collection</a>'
               '</div> </div></td></tr>';

            }
            else{
            item_html =  '<tr  class="file_and_dir_item" id="'+i+'_file_and_dir"><td scope="row"><div class="media align-items-center"><div class="media-body">'+icon+'<span class="name mb-0 text-sm"> &nbsp;<a href="/files.html?current_path='+file["abs_path"].substr(6)+
                  '&dir=false"> ' +file["name"]+ '</a></span> </div></div></td>" + "<td class="budget">'+file["native"]["created_time"]+'</td>"' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+file["native"]["access_time"]+'</span></span></td>' +
                   '<td> <span class="badge badge-dot mr-4">  <span class="status">'+file["native"]["size"]+'</span></span></td>' +
                   '<td> <div class="avatar-group"> <a href="#" data-toggle="tooltip" data-original-title='+user+'>'+file['owner']+'</a></div></td>' +
                   '<td ><div class="dropdown"><a class="btn btn-sm btn-icon-only text-light" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-v"></i></a>'+
                   '<div class="dropdown-menu dropdown-menu-right dropdown-menu-arrow">'+
                   tabs+
                   '<a class="dropdown-item" href="#" id="'+i+'_add_to_collection">Add to Collection</a>'
                   '</div> </div></td></tr>';
            }
            item_node = htmlToElement(item_html);
            $("#file_list")[0].appendChild(item_node);
            /*
            if (document.querySelector("#enreec"))
                    document.querySelector("#enreec").addEventListener("click",function(){
                      // API Endpoint
                      const url = "https://sandboxapi.deere.com/platform/organizations/4193081";

                      // Headers
                      const headers = {
                        "Authorization": "Bearer eyJraWQiOiI4M3k5QWZNV1p6enQ2SDJSVVNHeFAzUG5IN256SUlwUmN4MnZEdW9KRzJVIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULlZJMXp5VXpUU2pqbXZTSmVFMWZFN0h3MUE5VHdDVkxfaGViajFETXZ5SjAub2FyMWhzYmRsNzBja2p5dDI1ZDciLCJpc3MiOiJodHRwczovL3NpZ25pbi5qb2huZGVlcmUuY29tL29hdXRoMi9hdXM3OHRubGF5c01yYUZoQzF0NyIsImF1ZCI6ImNvbS5kZWVyZS5pc2cuYXhpb20iLCJpYXQiOjE3MDI4NjcwNTcsImV4cCI6MTcwMjkxMDI1NywiY2lkIjoiMG9hYnFpM2ljN1pGRVpFM3o1ZDciLCJ1aWQiOiIwMHVicWhqc2ozM2ZLd1ZvcTVkNyIsInNjcCI6WyJhZzIiLCJhZzEiLCJvZmZsaW5lX2FjY2VzcyIsImZpbGVzIiwiYWczIiwid29yazEiLCJvcmcxIiwid29yazIiLCJvcmcyIiwiZXEyIiwiZXExIl0sImF1dGhfdGltZSI6MTcwMTM4MTMxMSwic3ViIjoieXUucGFuQHVubC5lZHUiLCJpc2NzYyI6dHJ1ZSwidGllciI6IlNBTkRCT1giLCJjbmFtZSI6ImFnIGRhdGEgbWFuYWdlbWVudCIsInVzZXJUeXBlIjoiQ3VzdG9tZXIifQ.DiMGBT41XeseSOkHv-mBBKWLL95clDZjLXrmB6rDYd1YvkI3WPxGMO99WG4K453L02lbmoQ7df8eoFMtrn-9JNA74yK9CBvl-mr7bermRPwKS6JP-XyJ2fnJiJa5njQ7SHJP-o2bFG-GI0A89FAKKHGmsX-9i6qn1JqEs17MKPxuLrNmb-RqnXxnFWojv0N3W860fEbuF8sJjWhF687lKPTU8EwPoOGf0CLwq-EV0xdJHoFUQW7Z0dLTjboHUl3XvC4uj7itV7DW0bCwGS0QwITlfcjLPWvsAEgU3VKQhw5MCRLsj9v80qeELllPFiqXSUeP616pKGJ8JQ2h7hBaxw",
                                          //Bearer eyJraWQiOiI4M3k5QWZNV1p6enQ2SDJSVVNHeFAzUG5IN256SUlwUmN4MnZEdW9KRzJVIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULlZJMXp5VXpUU2pqbXZTSmVFMWZFN0h3MUE5VHdDVkxfaGViajFETXZ5SjAub2FyMWhzYmRsNzBja2p5dDI1ZDciLCJpc3MiOiJodHRwczovL3NpZ25pbi5qb2huZGVlcmUuY29tL29hdXRoMi9hdXM3OHRubGF5c01yYUZoQzF0NyIsImF1ZCI6ImNvbS5kZWVyZS5pc2cuYXhpb20iLCJpYXQiOjE3MDI4NjcwNTcsImV4cCI6MTcwMjkxMDI1NywiY2lkIjoiMG9hYnFpM2ljN1pGRVpFM3o1ZDciLCJ1aWQiOiIwMHVicWhqc2ozM2ZLd1ZvcTVkNyIsInNjcCI6WyJhZzIiLCJhZzEiLCJvZmZsaW5lX2FjY2VzcyIsImZpbGVzIiwiYWczIiwid29yazEiLCJvcmcxIiwid29yazIiLCJvcmcyIiwiZXEyIiwiZXExIl0sImF1dGhfdGltZSI6MTcwMTM4MTMxMSwic3ViIjoieXUucGFuQHVubC5lZHUiLCJpc2NzYyI6dHJ1ZSwidGllciI6IlNBTkRCT1giLCJjbmFtZSI6ImFnIGRhdGEgbWFuYWdlbWVudCIsInVzZXJUeXBlIjoiQ3VzdG9tZXIifQ.DiMGBT41XeseSOkHv-mBBKWLL95clDZjLXrmB6rDYd1YvkI3WPxGMO99WG4K453L02lbmoQ7df8eoFMtrn-9JNA74yK9CBvl-mr7bermRPwKS6JP-XyJ2fnJiJa5njQ7SHJP-o2bFG-GI0A89FAKKHGmsX-9i6qn1JqEs17MKPxuLrNmb-RqnXxnFWojv0N3W860fEbuF8sJjWhF687lKPTU8EwPoOGf0CLwq-EV0xdJHoFUQW7Z0dLTjboHUl3XvC4uj7itV7DW0bCwGS0QwITlfcjLPWvsAEgU3VKQhw5MCRLsj9v80qeELllPFiqXSUeP616pKGJ8JQ2h7hBaxw
                        "Host": "sandboxapi.deere.com",
                        "User-Agent": "ADMA",
                        "Accept": "application/vnd.deere.axiom.v3+json",
                        "Connection": "keep-alive",
                        "Accept-Encoding": "gzip, deflate, br"
                      };

                      // Sending the GET request
                      fetch(url, { method: "GET", headers: headers })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json(); // or response.text() if the response is not in JSON format
                        })
                        .then(data => {
                            console.log("Success:", data);
                            


                        })
                        .catch(error => {
                            console.log("Failed to retrieve data:", error.message);
                        });



                  }  );

                */




            $(".file_and_dir_item").click(function(){
                //file_name = this.id.split("_")[this.id.split("_").length-1]

               this.style.backgroundColor = "#69cfff";
                if(previous_selected_file_and_dir && previous_selected_file_and_dir != this)
                  previous_selected_file_and_dir.style.backgroundColor = "";

                previous_selected_file_and_dir = this;



            });


            $(".file_and_dir_item").dblclick(function(){
                file_name= data[parseInt(this.id.split("_")[0])]["name"];
                file_path= data[parseInt(this.id.split("_")[0])]["abs_path"].substr(6);

                link = '/files.html?current_path='+file_path;

                window.location.href =link;




            });



            $("#"+i+"_file_delete").click(function(){
               file_name= data[parseInt(this.id.split("_")[0])]["name"];
               file_path= data[parseInt(this.id.split("_")[0])]["abs_path"];
               deleted_file_path = file_path;
               document.querySelector('#delete_file_overlay').style.display= "flex";



               console.info(file_name);



            });


            $("#"+i+"_add_to_collection").click(function(){
               file_name= data[parseInt(this.id.split("_")[0])]["name"];
               file_path = data[parseInt(this.id.split("_")[0])]["abs_path"]
               console.info(file_name);
               add_to_collection(file_path);


            });

            $("#"+i+"_move").click(function(){
               file_name= data[parseInt(this.id.split("_")[0])]["name"];
               //console.info(file_name);
               //add_to_domain(current_path,file_name);


            });

            $("#"+i+"_duplicate").click(function(){
               file_name= data[parseInt(this.id.split("_")[0])]["name"];
               file_path = data[parseInt(this.id.split("_")[0])]["abs_path"]
               //console.info(file_name);
               //add_to_domain(current_path,file_name);
               duplicate(file_path);


            });

            $("#"+i+"_get_JD_authorization_code").click(function(){
              document.getElementById('preloader4').style.display = 'flex';


           });

      


          }


    });
}

function duplicate(file_path){
     $.ajax({
            type: "POST",

            url: "/duplicate",
            data: {
                 file_path:file_path,

            },
            success: function (data) {
                console.info(data);
                $("#file_list")[0].innerHTML="";
                get_item_list();
               display_warning_overlay("A copy of "+file_path.split("/")[file_path.split("/").length-1]+" is generated.");

            }
        });

}

function connect_to_JD(file_path){
  $.ajax({
         type: "GET",

         url: "/api/connect_JD/",
         data: {
              file_path:file_path,

         },
         success: function(data, textStatus, jqXHR) {
          // Check if the response indicates a redirect
          if (jqXHR.status === 302 || jqXHR.status === 301) {
              // If a redirect is indicated, manually redirect the client
              const redirectUrl = jqXHR.getResponseHeader('Location');
              /*if (redirectUrl) {
                  window.location.href = redirectUrl;
                  return;
              }*/
              //display a overlay with the redirect url in the middle of the screen
              display_warning_overlay("Please click the link to connect to John Deere Operations Center: "+redirectUrl);
          }
      },
      error: function(xhr, status, error) {
          console.error('There was a problem with the ajax operation:', error);
          console.info(xhr.status);
          console.info(status);
      }
  });
}







function add_to_collection(file_path){

   selected_file_path = file_path;

   display_collections_selection();

}

collection_names=[];
function display_collections_selection(){
   path = user+"/collections";

   $("#collections_overlay")[0].style.display = "flex";
   document.body.style.overflow = "hidden";
   $("#collections_in_overlay")[0].innerHTML = "";

    $.get("/meta_data",
        {
          current_path: path
         },
         function(data, status){
            meta_data=JSON.parse(data);
            sub_dirs = meta_data["subdirs"];
            //collections_overlay_path_components = meta_data["abs_path"].split("/");
            path = "";
            $("#collections_overlay_path")[0].innerHTML = "Collections";


            for (var i =0;i<sub_dirs.length;i++){

                   sub_dir = sub_dirs[i];
                   console.info(sub_dir);
                   collection_name = sub_dir.split("/")[sub_dir.split("/").length-1];
                   collection_names.push(collection_name);

                   if(collection_name.indexOf(".") == -1){//folder
                     item_html =  '<tr class="collection_item" id="collection_item_'+i+'"  onclick="select_collection(this)" >'+
                       '<td scope="row"><div class="media align-items-center"><div class="media-body"><span class="name mb-0 text-sm">'+
                       ' <a >&nbsp; ' +collection_name+
                       '</a></span> </div></div></td>"' +
                       '</tr>';

                   }

            item_node = htmlToElement(item_html);
            $("#collections_in_overlay")[0].appendChild(item_node);

            }

         });

}
previous_selected_collection = null;
previous_selected_file_and_dir =null;


function select_collection(self){
   i = self.id.substr("collection_item_".length);
   selected_collection = collection_names[i];



   self.style.backgroundColor = "#69cfff";
    if(previous_selected_collection && previous_selected_collection != self)
      previous_selected_collection.style.backgroundColor = "";

    previous_selected_collection = self;
    //document.querySelector(".file_and_dir_item").style.backgroundColor = "white";

}


function set_collections_overlay(){

    const collections_overlay = document.querySelector('#collections_overlay');

    collections_overlay.addEventListener('click', function(event) {
        this.style.display  = "none";
        document.body.style.overflow = "auto";
    });

    const collections_tab = document.querySelector('#collections_tab');

    collections_tab.addEventListener('click', function(event) {
       event.stopPropagation();
    });


    const collections_button = document.querySelector('#collections_button');

    collections_button.addEventListener('click', function(event) {
           collections_overlay.style.display = "none";
           document.body.style.overflow = "auto";

              $.ajax({
            type: "POST",

            url: "/add_to_collection",
            data: {
                 selected_collection:selected_collection,
                 selected_file_path: selected_file_path
            },
            success: function (data) {
                console.info(data);

                display_warning_overlay(selected_file_path.split("/")[selected_file_path.split("/").length-1]+" added to colletion: "+selected_collection);

            }
        });



    });

    document.querySelector("#collections_tab").addEventListener('scroll',function(event){
       // event.stopPropagation();
         //event.preventDefault();

    });

}



