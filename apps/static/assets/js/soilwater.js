domain="{{domain}}";

 app="{{app}}";

 plot ="{{location}}";


 subdomain_path= "{{subdomain_paths.0}}";
 layer="{{layers.0}}";
 time="{{times.0}}";
 if(domain=="spidercam"){
  layer="{{layer}}";
  time="{{time}}";
}

 var metricName="";
 var metricCount=[];
 var metricMonths=[];
 var overlays=[];


let info_window;
//let historicalOverlay;
zoom = 20;
lower_lat = 41.145632;
left_ln = -96.439434;
upper_lat = 41.145942;
right_ln = -96.439201;
rectangles =new Map();
rectangles_reverse = {};
lat_per_rect=(upper_lat-lower_lat)/8;
ln_per_rect=(right_ln-left_ln)/10;
var rect_select;
var test;
var map;
var cur_plot;

function rect_zoom(event){



  $.get("/domain_data",
    {
      app:app,
      plot:cur_plot,
      time:time,
      layer:layer,
      meta:false,
    },function(data,status){
      data=JSON.parse(data)
      src="";
      for ( t in data[cur_plot]){

        src=data[cur_plot][t][layer];
        if(t==time)
          break
      }
      //console.info(src);
      if(src[0]=="/"){
        $("#zoom_window")[0].innerHTML="<img id='subdomain_img' width='320' height='240' /> ";
        $("#subdomain_img")[0].src=src;
      }
      else{
        value=src;
        console.info(value);
        fill_color=parseInt(Math.min(value*255,255));
        $("#zoom_window")[0].innerHTML="<p id='value'></p>";
        $("#zoom_window")[0].style.backgroundColor="rgb("+0+","+fill_color+","+0+")";
        $("#value")[0].innerHTML="<b>"+layer+": "+src+"</b>";
        $("#value")[0].style.color="white";

      }



    });


}


function init_map_spidercam() {
   map = new google.maps.Map(document.getElementById("map"), {
    zoom: zoom,
    minZoom: zoom-3,
    maxZoom: 22,
    center: { lat: (lower_lat+upper_lat)/2, lng: (left_ln+right_ln)/2},
    mapTypeId:'satellite'
  });


  for(i=0;i<8;i++){
    for(j=0;j<10;j++){
      rect_lower_lat=lower_lat+i*lat_per_rect;
      rect_upper_lat=rect_lower_lat+lat_per_rect;
      rect_left_ln=left_ln+j*ln_per_rect;
      rect_right_ln=rect_left_ln+ln_per_rect;

  const rectCoords = [
    { lat: rect_lower_lat, lng: rect_left_ln },
    { lat: rect_lower_lat, lng: rect_right_ln},
    { lat: rect_upper_lat, lng: rect_right_ln },
    { lat: rect_upper_lat, lng: rect_left_ln }
  ];
// Construct the rect.
  const rectangle = new google.maps.Polygon({
    paths: rectCoords,
    strokeColor: "#ffc800",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#ffcc00",
    fillOpacity: 1,
  });

  rectangle.setMap(map);
  rectangle.addListener("click",rect_highlight);

  //rectangle.addListener("mouseout",rect_reset);
  //rectangle.addListener("click",show_info);
  rectangles.set(rectangle,1301+i*10+j);
  rectangles_reverse[1301+i*10+j]=rectangle;
  console.info(rectangles);
    }
  }



  info_window = new google.maps.InfoWindow();




function rect_highlight(event){
  const rect = this;
  path=rect.getPath().getArray();
  console.info(path[0]);
  test=path;
  rectCoords=[
  {lat:path[0].lat()-lat_per_rect/4, lng:path[0].lng()-ln_per_rect/3},
{lat:path[1].lat()-lat_per_rect/4, lng:path[1].lng()+ln_per_rect/3},
{lat:path[2].lat()+lat_per_rect/4, lng:path[2].lng()+ln_per_rect/3},
{lat:path[3].lat()+lat_per_rect/4, lng:path[3].lng()-ln_per_rect/3},

  ];

if(rect_select)
rect_select.setMap(null);


rect_select = new google.maps.Polygon({
    paths: rectCoords,
    strokeColor: "red",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#ffcc00",
    fillOpacity: 0,
  });
rect_select.setMap(map);

cur_plot=rectangles.get(rect);
$("#spidercam_location")[0].value=cur_plot;
//console.info(plot);
rect_select.addListener("dblclick",rect_zoom);
}

function rect_reset(event){
  const rect = this;
  rect.setOptions({fillOpacity:0});

}
/*
function show_info(event){
  info_window.setContent("<b>Current Field ID:  "+(1301+rectangles.get(this)[0]*10+rectangles.get(this)[1])+"</b>");
  info_window.setPosition(event.latLng);
  //info_window.setOptions({"maxWidth":20});
  info_window.open(map);
    info_window.focus();

}*/
 }

var locations;
var meta_data;
var sorted_times;
var bars=[];

if(domain=="spidercam"){
    $.get("/domain_data",
    {
      app:app,
      plot:plot,
      time:time,
      layer:layer,
      meta:true,
    },
      function(data,status){

        meta_data = JSON.parse(data);

        locations = Object.keys(meta_data);

        //cur_location = locations[0];
        times = {};
        layers = {};
        for(loc in meta_data){

          for (t in meta_data[loc]){
             times[t]=true;
             for(l in meta_data[loc][t])


              layers[l]=true;
          }
        }

        sorted_times=Object.keys(times).sort((first,second)=>(new Date(first)-new Date(second)));

        $("#spidercam_location")[0].innerHTML="";
        for(loc in meta_data){
          var loc_option=document.createElement("option");
          loc_option.innerHTML=loc;
          $("#spidercam_location")[0].appendChild(loc_option);
        }

        $("#spidercam_time")[0].innerHTML="";
        for(t of sorted_times){
          var t_option=document.createElement("option");
          t_option.innerHTML=t;
          $("#spidercam_time")[0].appendChild(t_option);
        }

        $("#spidercam_layer")[0].innerHTML="";
        for(l in layers){
          var l_option=document.createElement("option");
          l_option.innerHTML=l;
          $("#spidercam_layer")[0].appendChild(l_option);
        }



        //time_selector = document.getElementById("spidercam_time");
        //time = time_selector.selectedOptions[0];

        //layer_selector = document.getElementById("spidercam_layer");
        //layer = layer_selector.selectedOptions[0];
        time = sorted_times[0];
        layer=Object.keys(layers)[0];
        console.info(plot);

        get_data();

        time_span=new Date(sorted_times[sorted_times.length-1]).getTime()-new Date(sorted_times[0]).getTime();
        console.info(time_span);
        for(t of sorted_times){
          t_ms=new Date(t).getTime()-new Date(sorted_times[0]).getTime();
          bar_pos = t_ms/time_span* $("#spidercam_progress")[0].offsetWidth;
          //console.info(t_ms);
          bar = document.createElement("div");
          bar.style.width="0.6%";
          bar.style.height="35px";
          bar.style.position = "absolute";
          bar.style.backgroundColor = "green";
          bar.style.borderRadius="3px";
          bar.style.left=parseInt(bar_pos)+"px";
          bar.style.bottom="0px";



          $("#spidercam_progress")[0].appendChild(bar);
          bars.push(bar);
        }



          t_ms=new Date(time).getTime()-new Date(sorted_times[0]).getTime();
          time_pos = t_ms/time_span* $("#spidercam_progress")[0].offsetWidth;


  if(time_box)
    $("#spidercam_progress")[0].removeChild(time_box);
  time_box = document.createElement("div");
          time_box.style.width="20px";
          time_box.style.height="55px";
          time_box.style.position = "absolute";
          time_box.style.borderColor = "red";
          time_box.style.borderWidth = "thick";
          time_box.style.borderRadius="3px";
          time_box.style.left=(parseInt(time_pos)-10)+"px";
          time_box.style.bottom="-10px";
          time_box.style.border="solid blue 5px";



          $("#spidercam_progress")[0].appendChild(time_box);




      });


function get_data(){

        $.get("/domain_data",
         {
      app:app,
      plot:plot,
      time:time,
      layer:layer,
      meta:false,
    },
          function(data,status){
            data = JSON.parse(data);
            console.info(data);

            for (p in rectangles_reverse)
                rectangles_reverse[p].setOptions({fillOpacity:0});

            for (overlay of overlays){
                overlay.setMap(null);
                overlays=[];
              }





            for(loc in data){
              t=Object.keys(data[loc])[0];


              value=data[loc][t][layer];
              if(time in data[loc])
                value=data[loc][time][layer];

              if(value[0]=="/"){
                path=rectangles_reverse[loc].getPath().getArray();
                 imageBounds = {
                    north: path[2].lat(),
                    south: path[0].lat(),
                    east: path[1].lng(),
                    west: path[0].lng(),
                  };
                  historicalOverlay = new google.maps.GroundOverlay(
                  value,
                  imageBounds
                );
                historicalOverlay.setMap(map);
                overlays.push(historicalOverlay);

              }
              else{
                fill_color=parseInt(Math.min(value*255,255));
                rectangles_reverse[loc].setOptions({fillColor:"rgb("+0+","+fill_color+","+0+")",fillOpacity:1});
                //console.info(fill_color);

              }


            }





          });
}


var time_box;
$("#spidercam_time").change(function(){

   time=this.options[this.selectedIndex].value;
  get_data();
  if(rect_select){
     rect_zoom();

  }



 time_span=new Date(sorted_times[sorted_times.length-1]).getTime()-new Date(sorted_times[0]).getTime();


          t_ms=new Date(time).getTime()-new Date(sorted_times[0]).getTime();
          time_pos = t_ms/time_span* $("#spidercam_progress")[0].offsetWidth;


  if(time_box)
    $("#spidercam_progress")[0].removeChild(time_box);
  time_box = document.createElement("div");
          time_box.style.width="20px";
          time_box.style.height="55px";
          time_box.style.position = "absolute";
          time_box.style.borderColor = "red";
          time_box.style.borderWidth = "thick";
          time_box.style.borderRadius="3px";
          time_box.style.left=(parseInt(time_pos)-10)+"px";
          time_box.style.bottom="-10px";
          time_box.style.border="solid blue 5px";



          $("#spidercam_progress")[0].appendChild(time_box);




});

$("#spidercam_layer").change(function(){

   layer=this.options[this.selectedIndex].value;
  get_data();
   if(rect_select){
     rect_zoom();

  }

});

$("#spidercam_location").change(function(){

   p=this.options[this.selectedIndex].value;
   cur_plot=p;

   rect=rectangles_reverse[p];
   path=rect.getPath().getArray();
  console.info(path[0]);
  test=path;
  rectCoords=[
  {lat:path[0].lat()-lat_per_rect/4, lng:path[0].lng()-ln_per_rect/3},
{lat:path[1].lat()-lat_per_rect/4, lng:path[1].lng()+ln_per_rect/3},
{lat:path[2].lat()+lat_per_rect/4, lng:path[2].lng()+ln_per_rect/3},
{lat:path[3].lat()+lat_per_rect/4, lng:path[3].lng()-ln_per_rect/3},

  ];

if(rect_select)
rect_select.setMap(null);


  rect_select = new google.maps.Polygon({
    paths: rectCoords,
    strokeColor: "red",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#ffcc00",
    fillOpacity: 0,
  });
rect_select.setMap(map);
 if(rect_select){
     rect_zoom();

  }

 for(bar of bars){
  $("#spidercam_progress")[0].removeChild(bar);
 }
 bars=[];
 times=Object.keys(meta_data[cur_plot]);
 sorted_times=times.sort((first,second)=>(new Date(first).getTime()-new Date(second).getTime()));
 time_span=new Date(sorted_times[sorted_times.length-1]).getTime()-new Date(sorted_times[0]).getTime();
        console.info(sorted_times);
        for(t of sorted_times){
          t_ms=new Date(t).getTime()-new Date(sorted_times[0]).getTime();
          bar_pos = t_ms/time_span* $("#spidercam_progress")[0].offsetWidth;

          bar = document.createElement("div");
          bar.style.width="0.6%";
          bar.style.height="35px";
          bar.style.position = "absolute";
          bar.style.backgroundColor = "green";
          bar.style.borderRadius="3px";
          bar.style.left=parseInt(bar_pos)+"px";
          bar.style.bottom="0px";



          $("#spidercam_progress")[0].appendChild(bar);
          bars.push(bar);
        }




});

}

else{
$.post("/domain_data",
      {
        subdomain_path: subdomain_path,
        layer: layer,
        time: time
      },
      function(data, status){

        if(domain=="spidercam")
          $("#subdomain_img")[0].src=data;
        else if(domain=="soilwater"){
         //console.info(data);

          data = JSON.parse(data);
          console.info(data["times"]);



           metricName   = "Water Content (m³/m³)";

           metricCount  = data["soilwaters"];

            metricMonths = data["times"];
            d3.selectAll("svg").remove();
            draw_time_series_chart();
        }

        $(".my_dataviz p b")[0].innerHTML=subdomain_path+"/"+time+"/"+layer;

  });

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}



$("#spidercam_layer").change(function(){

   layer=this.options[this.selectedIndex].value;

   console.info(layer);



        $.post("/domain_data",
      {
        subdomain_path: subdomain_path,
        layer: layer,
        time: time
      },
      function(data, status){

        if(subdomain != "all")
              $("#subdomain_img")[0].src=data;
        else{
              //data=JSON.parse(data);
              //console.info(data);
              data={1373:0.903,1374:1.072,1375:1.011,1376:0.897};

              for(k in data){
                value = data[k]*100;
                color ="rgb("+ parseInt(value)+","+parseInt(value)+","+parseInt(value) +")";
                console.info(color);
                $("#"+k+"_box").css("background-color",color);
            }
       }




        $(".my_dataviz p b")[0].innerHTML=subdomain_path+"/"+time+"/"+layer;
      });

});

$("#subdomain_location").change(function(){

   subdomain_path=this.options[this.selectedIndex].value;
   subdomain = subdomain_path.split("/")[2];
   if(subdomain == "all"){
     var all = document.createElement("div");
     all.setAttribute("id","subdomain_img");


     for(i=0;i<10;i++){
      var row = document.createElement("div");

      for(j=0;j<8;j++){
        var col_div = document.createElement("div");
        var col = document.createElement("img");
        col.setAttribute("id",1301+j*10+i);
        col.setAttribute("width",640/8);
        col.setAttribute("height",480/10);
        //col.setAttribute("src","/static/data_cache/white.png");
        col_div.className="domain_all";
        col_div.setAttribute("id",1301+j*10+i+"_box");
        //col_div.appendChild(col);
        row.appendChild(col_div);
      }
      all.appendChild(row);
     }

     document.getElementById("subdomain_img").replaceWith(all);




   }
   else{
    var img = document.createElement("img");
    img.setAttribute("id","subdomain_img");
    img.setAttribute("width",640);
    img.setAttribute("height",480);
    document.getElementById("subdomain_img").replaceWith(img);


   }

   $.post("/domain_time",
      {
        subdomain_path: subdomain_path,
      },
      function(data, status){
        data=JSON.parse(data);
        time = data[0];
        $("#spidercam_time")[0].innerHTML="";
        console.info(data);

        for(t of data){
          time_html='<option>'+t+'</option>';
          time_node = htmlToElement(time_html);
          $("#spidercam_time")[0].appendChild(time_node);
        }



       $.post("domain_data",
          {

            subdomain_path: subdomain_path,
            layer: layer,
            time: time
          },
          function(data, status){



              if(domain=="spidercam"){
                if(subdomain != "all")
                  $("#subdomain_img")[0].src=data;
                else{
                  data=JSON.parse(data);
                  console.info(data);
                  for(k in data){
                    $("#"+k)[0].src=data[k];
                  }
                }

              }
              else if(domain=="soilwater"){
                data = JSON.parse(data);
                //console.info(data["times"]);



                 metricName   = "Water Content (m³/m³)";

                 metricCount  = data["soilwaters"];

                  metricMonths = data["times"];
                  d3.selectAll("svg").remove();
                  draw_time_series_chart();
              }

              $(".my_dataviz p b")[0].innerHTML=subdomain_path+"/"+time+"/"+layer;

      });
     });

});




$("#spidercam_time").change(function(){

   time=this.options[this.selectedIndex].value;


      $.post("domain_data",
      {
        subdomain_path: subdomain_path,
        layer: layer,
        time: time
      },
      function(data, status){
       //alert("Data: " + data + "\nStatus: " + status);




        if(subdomain != "all"){
            $("#subdomain_img")[0].src=data;
            $(".my_dataviz p b")[0].innerHTML=subdomain_path+"/"+time+"/"+layer;
        }
        else{
                  data=JSON.parse(data);
                  console.info(data);
                  for(k in data){
                    $("#"+k)[0].src=data[k];
                  }
                $(".my_dataviz p b")[0].innerHTML=subdomain_path+"/"+time+"/"+layer;
        }
  });

});

}