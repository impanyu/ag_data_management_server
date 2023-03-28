

nav_link = document.querySelector('.nav-link');

nav_link.addEventListener('mouseover', add_active(this));

nav_link.addEventListener('mouseout', function(this) {
  this.classList.remove('active');
});


function add_active(self){
   self.classList.add('active');
}