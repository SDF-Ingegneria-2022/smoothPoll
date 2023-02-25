/* 
    Sidedrawer nav menu code. Insipired by
    https://github.com/StartBootstrap/startbootstrap-simple-sidebar 
    but heavily customized
*/

window.addEventListener('DOMContentLoaded', event => {

    // get all boxes that toggle the sidebar
    const sidebarTogglers = Array.from(
        document.getElementsByClassName("sidebar-toggler")
    );
    
    // On desktop I want to remember if sidebar is open or close, 
    // On mobile I want it closed by default
    const width = (window.innerWidth > 0) ? window.innerWidth : screen.width;
    if (width > 768 && sidebarTogglers.length > 0) {
        if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
            document.body.classList.toggle('sb-sidenav-toggled');
        }
    }

    // make sidebar toggle when one of the 
    // togglers is clicked
    sidebarTogglers.forEach((box) => {
        box.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }); 
});