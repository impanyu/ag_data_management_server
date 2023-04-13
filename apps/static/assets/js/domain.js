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
          //console.info(data);
          data=JSON.parse(data);
          subdomains=[];
          times=[];


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

            item_html =  '<tr  class="file_and_dir_item"><td scope="row"><div class="media align-items-center"><div class="media-body"><span class="name mb-0 text-sm"> &nbsp;<a href="/files.html?current_path='+current_path+'/'+file["file_name"]+'&dir=false"> ' +file["file_name"]+ '</a></span> </div></div></td>" + "<td class="budget">'+file["created_time"]+'</td>"' +
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