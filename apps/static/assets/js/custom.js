

nav_link = document.querySelector('.nav-link');

nav_link.addEventListener('mouseover', function(this) {
  this.classList.add('active');
});

nav_link.addEventListener('mouseout', function(this) {
  this.classList.remove('active');
});
