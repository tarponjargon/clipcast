import views from "./js/views";
import Global from "./js/views/Global";

document.addEventListener("DOMContentLoaded", function () {
  // init DOM funcions needed on every page
  const global = new Global();
  global.init();

  // init route controllers (handles code-splitting)
  views();
});
