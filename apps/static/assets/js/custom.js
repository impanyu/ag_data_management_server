

nav_link = document.querySelector('.nav-link');

nav_link.addEventListener('mouseover', function() {
  nav_link.classList.add('active');
});

nav_link.addEventListener('mouseout', function() {
  nav_link.classList.remove('active');
});
