function toggle_filter_condition(){
   if(document.querySelector("#filter-condition").style.display == "block")
     document.querySelector("#filter-condition").style.display = "none";
    else
     document.querySelector("#filter-condition").style.display = "block";
}

function toggle_filter_condition_2(){
   if(document.querySelector("#filter-condition").style.height == "0px"){
     document.querySelector("#filter-condition").style.height = "1180px";
     document.querySelector("#filter-condition").style.paddingTop = "1.25rem";
     document.querySelector("#filter-condition").style.paddingBottom = "1.25rem";

     }
    else{
     document.querySelector("#filter-condition").style.height = "0px";
          document.querySelector("#filter-condition").style.paddingTop = "0rem";
     document.querySelector("#filter-condition").style.paddingBottom = "0rem";
     }
}