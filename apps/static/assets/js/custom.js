

nav_links = document.querySelectorAll('.nav-link');

for(i=0;i<nav_links.length;i++){
  nav_links[i].addEventListener('mouseover', function(this){
     add_active(this);
});
  nav_links[i].addEventListener('mouseout', function(this) {
  remove_active(this);
});

}



function add_active(self){
self.classList.add('active');
}

function remove_active(self){
self.classList.remove('active');
}
