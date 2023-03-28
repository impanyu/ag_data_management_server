

nav_links = document.querySelectorAll('.nav-link');

for(i=0;i<nav_links.length;i++){
  nav_links[i].addEventListener('mouseover', function(){
     nav_links[i].classList.add('active')
});
  nav_links[i].addEventListener('mouseout', function() {
  nav_links[i].classList.remove('active');
});

}






