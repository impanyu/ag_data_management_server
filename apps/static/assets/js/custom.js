

nav_links = document.querySelectorAll('.nav-link');

for(i=0;i<nav_links.length;i++){
 nav_
  nav_links[i].addEventListener('mouseover', function(event){
     add_active(event);
});
  nav_links[i].addEventListener('mouseout', function(event) {
  remove_active(event);
});

}



function add_active(event){
event.currentTarget.classList.add('active');
}

function remove_active(self){
event.currentTarget.classList.remove('active');
}
