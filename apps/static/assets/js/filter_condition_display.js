function toggle_filter_condition(){
   if(document.querySelector("#filter-condition").style.display == "block")
     document.querySelector("#filter-condition").style.display = "none";
    else
     document.querySelector("#filter-condition").style.display = "block";
}

function toggle_filter_condition_2(){
   if(document.querySelector("#filter-condition").style.height == "0px")
     document.querySelector("#filter-condition").style.height = "auto";
    else
     document.querySelector("#filter-condition").style.height = "0px";
}