function scrollL(id) {
    let x = document.getElementById(id);
    let step = window.outerWidth / 2;
    x.scrollLeft -= step;
  }
  
function scrollR(id) {
    let x = document.getElementById(id);
    let step = window.outerWidth / 2;
    x.scrollLeft += step;
}