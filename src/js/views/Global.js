/* this is mostly code used as-is from SeanTheme's bootstrap 5 "HUD Admin" theme */

import "../../scss/styles.scss";
import "../../css/all.min.css";
import "../../css/animate.min.css";
import "../vendor/iconify-icon.min.js";
import { isMobile } from "../modules/Utils";
import { showToast } from "../modules/Toast";

// even though these are specified in ProvidePlugin, it's not available in the window w/o these
global.bootstrap = require("bootstrap");

// adds htmx and plugins to window
window.htmx = require("htmx.org").default;
require("htmx-ext-response-targets"); // htmx-plugin
//require("../vendor/class-tools"); // htmx-plugin
// require("../vendor/response-targets.js"); // htmx-plugin

window.showToast = showToast;

const app = CFG.userInterfaceConfig;

window.markNotificationAsViewed = async function (event) {
  event.preventDefault();
  const response = await fetch(`/api/notifications-viewed`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  await response.json();
  const notificationBadge = document.getElementById("notifications-badge");
  if (notificationBadge) {
    notificationBadge.remove();
  }
};

window.scrollToTop = function () {
  window.scrollTo({ top: 0, behavior: "smooth" });
};

window.scrollToSelector = function (selector) {
  const element = document.querySelector(selector);
  if (element) {
    element.scrollIntoView({ behavior: "smooth" });
  }
};

/* 03. Handle Sidebar Menu
------------------------------------------------ */
var handleSidebarMenuToggle = function (menus) {
  menus.map(function (menu) {
    menu.onclick = function (e) {
      e.preventDefault();
      var target = this.nextElementSibling;

      menus.map(function (m) {
        var otherTarget = m.nextElementSibling;
        if (otherTarget !== target) {
          otherTarget.style.display = "none";
          otherTarget
            .closest("." + app.sidebar.menu.itemClass)
            .classList.remove(app.sidebar.menu.expandClass);
        }
      });

      var targetItemElm = target.closest("." + app.sidebar.menu.itemClass);

      if (
        targetItemElm.classList.contains(app.sidebar.menu.expandClass) ||
        (targetItemElm.classList.contains(app.sidebar.menu.activeClass) && !target.style.display)
      ) {
        targetItemElm.classList.remove(app.sidebar.menu.expandClass);
        target.style.display = "none";
      } else {
        targetItemElm.classList.add(app.sidebar.menu.expandClass);
        target.style.display = "block";
      }
    };
  });
};
var handleSidebarMenu = function () {
  "use strict";

  var menuBaseSelector =
    "." +
    app.sidebar.class +
    " ." +
    app.sidebar.menu.class +
    " > ." +
    app.sidebar.menu.itemClass +
    "." +
    app.sidebar.menu.hasSubClass;
  var submenuBaseSelector =
    " > ." +
    app.sidebar.menu.submenu.class +
    " > ." +
    app.sidebar.menu.itemClass +
    "." +
    app.sidebar.menu.hasSubClass;

  // menu
  var menuLinkSelector = menuBaseSelector + " > ." + app.sidebar.menu.itemLinkClass;
  var menus = [].slice.call(document.querySelectorAll(menuLinkSelector));
  handleSidebarMenuToggle(menus);

  // submenu lvl 1
  var submenuLvl1Selector = menuBaseSelector + submenuBaseSelector;
  var submenusLvl1 = [].slice.call(
    document.querySelectorAll(submenuLvl1Selector + " > ." + app.sidebar.menu.itemLinkClass)
  );
  handleSidebarMenuToggle(submenusLvl1);

  // submenu lvl 2
  var submenuLvl2Selector = menuBaseSelector + submenuBaseSelector + submenuBaseSelector;
  var submenusLvl2 = [].slice.call(
    document.querySelectorAll(submenuLvl2Selector + " > ." + app.sidebar.menu.itemLinkClass)
  );
  handleSidebarMenuToggle(submenusLvl2);
};

/* 04. Handle Sidebar Scroll Memory
------------------------------------------------ */
var handleSidebarScrollMemory = function () {
  if (!isMobile()) {
    try {
      if (typeof Storage !== "undefined" && typeof localStorage !== "undefined") {
        var elm = document.querySelector("." + app.sidebar.class + " [" + app.scrollBar.attr + "]");

        if (elm) {
          elm.onscroll = function () {
            localStorage.setItem(app.sidebar.scrollBar.localStorage, this.scrollTop);
          };
          var defaultScroll = localStorage.getItem(app.sidebar.scrollBar.localStorage);
          if (defaultScroll) {
            document.querySelector(
              "." + app.sidebar.class + " [" + app.scrollBar.attr + "]"
            ).scrollTop = defaultScroll;
          }
        }
      }
    } catch (error) {
      console.log(error);
    }
  }
};

/* 05. Handle Card Action
------------------------------------------------ */
var handleCardAction = function () {
  "use strict";

  if (app.card.expand.status) {
    return false;
  }
  app.card.expand.status = true;

  // expand
  var expandTogglerList = [].slice.call(
    document.querySelectorAll("[" + app.card.expand.toggleAttr + "]")
  );
  var expandTogglerTooltipList = expandTogglerList.map(function (expandTogglerEl) {
    expandTogglerEl.onclick = function (e) {
      e.preventDefault();

      var target = this.closest(".card");
      var targetClass = app.card.expand.class;
      var targetTop = 40;

      if (document.body.classList.contains(targetClass) && target.classList.contains(targetClass)) {
        target.removeAttribute("style");
        target.classList.remove(targetClass);
        document.body.classList.remove(targetClass);
      } else {
        document.body.classList.add(targetClass);
        target.classList.add(targetClass);
      }

      window.dispatchEvent(new Event("resize"));
    };

    return new bootstrap.Tooltip(expandTogglerEl, {
      title: app.card.expand.toggleTitle,
      placement: "bottom",
      trigger: "hover",
      container: "body",
    });
  });
};

/* 06. Handle Tooltip & Popover Activation
------------------------------------------------ */
var handelTooltipPopoverActivation = function () {
  "use strict";

  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll("[" + app.bootstrap.tooltip.attr + "]")
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  var popoverTriggerList = [].slice.call(
    document.querySelectorAll("[" + app.bootstrap.popover.attr + "]")
  );
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
};

/* 08. Handle hexToRgba
------------------------------------------------ */
var hexToRgba = function (hex, transparent = 1) {
  var c;
  if (/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
    c = hex.substring(1).split("");
    if (c.length == 3) {
      c = [c[0], c[0], c[1], c[1], c[2], c[2]];
    }
    c = "0x" + c.join("");
    return "rgba(" + [(c >> 16) & 255, (c >> 8) & 255, c & 255].join(",") + "," + transparent + ")";
  }
  throw new Error("Bad Hex");
};

/* 09. Handle Scroll To
------------------------------------------------ */
var handleScrollTo = function () {
  var elmTriggerList = [].slice.call(document.querySelectorAll("[" + app.scrollTo.attr + "]"));
  var elmList = elmTriggerList.map(function (elm) {
    elm.onclick = function (e) {
      e.preventDefault();

      var targetAttr = elm.getAttribute(app.scrollTo.target)
        ? this.getAttribute(app.scrollTo.target)
        : this.getAttribute(app.scrollTo.linkTarget);
      var targetElm = document.querySelectorAll(targetAttr)[0];
      var targetHeader = document.querySelectorAll(app.header.id)[0];
      var targetHeight = targetHeader.offsetHeight;
      if (targetElm) {
        var targetTop = targetElm.offsetTop - targetHeight - 24;
        window.scrollTo({ top: targetTop, behavior: "smooth" });
      }
    };
  });
};

/* 10. Handle Toggle Class
------------------------------------------------ */
var handleToggleClass = function () {
  var elmList = [].slice.call(document.querySelectorAll("[" + app.toggleClass.toggleAttr + "]"));

  elmList.map(function (elm) {
    elm.onclick = function (e) {
      e.preventDefault();

      var targetToggleClass = this.getAttribute(app.toggleClass.toggleAttr);
      var targetDismissClass = this.getAttribute(app.dismissClass.toggleAttr);
      var targetToggleElm = document.querySelector(this.getAttribute(app.toggleClass.targetAttr));

      if (!targetDismissClass) {
        if (targetToggleElm.classList.contains(targetToggleClass)) {
          targetToggleElm.classList.remove(targetToggleClass);
        } else {
          targetToggleElm.classList.add(targetToggleClass);
        }
      } else {
        if (
          !targetToggleElm.classList.contains(targetToggleClass) &&
          !targetToggleElm.classList.contains(targetDismissClass)
        ) {
          if (targetToggleElm.classList.contains(targetToggleClass)) {
            targetToggleElm.classList.remove(targetToggleClass);
          } else {
            targetToggleElm.classList.add(targetToggleClass);
          }
        } else {
          if (targetToggleElm.classList.contains(targetToggleClass)) {
            targetToggleElm.classList.remove(targetToggleClass);
          } else {
            targetToggleElm.classList.add(targetToggleClass);
          }
          if (targetToggleElm.classList.contains(targetDismissClass)) {
            targetToggleElm.classList.remove(targetDismissClass);
          } else {
            targetToggleElm.classList.add(targetDismissClass);
          }
        }
      }
    };
  });
};

/* 12. Handle CSS Variable
------------------------------------------------ */
var handleCssVariable = function () {
  var rootStyle = getComputedStyle(document.body);

  // font
  if (app.variableFontList && app.variablePrefix) {
    for (var i = 0; i < app.variableFontList.length; i++) {
      app.font[
        app.variableFontList[i].replace(/-([a-z|0-9])/g, (match, letter) => letter.toUpperCase())
      ] = rootStyle.getPropertyValue("--" + app.variablePrefix + app.variableFontList[i]).trim();
    }
  }

  // color
  if (app.variableColorList && app.variablePrefix) {
    for (var i = 0; i < app.variableColorList.length; i++) {
      app.color[
        app.variableColorList[i].replace(/-([a-z|0-9])/g, (match, letter) => letter.toUpperCase())
      ] = rootStyle.getPropertyValue("--" + app.variablePrefix + app.variableColorList[i]).trim();
    }
  }
};

/* 13. Handle Top Menu - Unlimited Top Menu Render
------------------------------------------------ */
var handleUnlimitedTopNavRender = function () {
  "use strict";
  // function handle menu button action - next / prev
  function handleMenuButtonAction(element, direction) {
    var obj = element.closest("." + app.topNav.menu.class);
    var objStyle = window.getComputedStyle(obj);
    var bodyStyle = window.getComputedStyle(document.querySelector("body"));
    var targetCss =
      bodyStyle.getPropertyValue("direction") == "rtl" ? "margin-right" : "margin-left";
    var marginLeft = parseInt(objStyle.getPropertyValue(targetCss));
    var containerWidth =
      document.querySelector("." + app.topNav.class).clientWidth -
      document.querySelector("." + app.topNav.class).clientHeight * 2;
    var totalWidth = 0;
    var finalScrollWidth = 0;
    var controlPrevObj = obj.querySelector(".menu-control-start");
    var controlPrevWidth = controlPrevObj ? controlPrevObj.clientWidth : 0;
    var controlNextObj = obj.querySelector(".menu-control-end");
    var controlNextWidth = controlPrevObj ? controlNextObj.clientWidth : 0;
    var controlWidth = controlPrevWidth + controlNextWidth;

    var elms = [].slice.call(obj.querySelectorAll("." + app.topNav.menu.itemClass));
    if (elms) {
      elms.map(function (elm) {
        if (!elm.classList.contains(app.topNav.control.class)) {
          totalWidth += elm.clientWidth;
        }
      });
    }

    switch (direction) {
      case "next":
        var widthLeft = totalWidth + marginLeft - containerWidth;
        if (widthLeft <= containerWidth) {
          finalScrollWidth = widthLeft - marginLeft - controlWidth;
          setTimeout(function () {
            obj
              .querySelector(
                "." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class
              )
              .classList.remove("show");
          }, app.animation.speed);
        } else {
          finalScrollWidth = containerWidth - marginLeft - controlWidth;
        }

        if (finalScrollWidth !== 0) {
          obj.style.transitionProperty = "height, margin, padding";
          obj.style.transitionDuration = app.animation.speed + "ms";
          if (bodyStyle.getPropertyValue("direction") != "rtl") {
            obj.style.marginLeft = "-" + finalScrollWidth + "px";
          } else {
            obj.style.marginRight = "-" + finalScrollWidth + "px";
          }
          setTimeout(function () {
            obj.style.transitionProperty = "";
            obj.style.transitionDuration = "";
            obj
              .querySelector(
                "." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class
              )
              .classList.add("show");
          }, app.animation.speed);
        }
        break;
      case "prev":
        var widthLeft = -marginLeft;

        if (widthLeft <= containerWidth) {
          obj
            .querySelector(
              "." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class
            )
            .classList.remove("show");
          finalScrollWidth = 0;
        } else {
          finalScrollWidth = widthLeft - containerWidth + controlWidth;
        }

        obj.style.transitionProperty = "height, margin, padding";
        obj.style.transitionDuration = app.animation.speed + "ms";

        if (bodyStyle.getPropertyValue("direction") != "rtl") {
          obj.style.marginLeft = "-" + finalScrollWidth + "px";
        } else {
          obj.style.marginRight = "-" + finalScrollWidth + "px";
        }

        setTimeout(function () {
          obj.style.transitionProperty = "";
          obj.style.transitionDuration = "";
          obj
            .querySelector(
              "." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class
            )
            .classList.add("show");
        }, app.animation.speed);
        break;
    }
  }

  // handle page load active menu focus
  function handlePageLoadMenuFocus() {
    var targetMenu = document.querySelector("." + app.topNav.class + " ." + app.topNav.menu.class);
    if (!targetMenu) {
      return;
    }
    var targetMenuStyle = window.getComputedStyle(targetMenu);
    var bodyStyle = window.getComputedStyle(document.body);
    var targetCss =
      bodyStyle.getPropertyValue("direction") == "rtl" ? "margin-right" : "margin-left";
    var marginLeft = parseInt(targetMenuStyle.getPropertyValue(targetCss));
    var viewWidth = document.querySelector("." + app.topNav.class + "").clientWidth;
    var prevWidth = 0;
    var speed = 0;
    var fullWidth = 0;
    var controlPrevObj = targetMenu.querySelector(".menu-control-start");
    var controlPrevWidth = controlPrevObj ? controlPrevObj.clientWidth : 0;
    var controlNextObj = targetMenu.querySelector(".menu-control-end");
    var controlNextWidth = controlPrevObj ? controlNextObj.clientWidth : 0;
    var controlWidth = 0;

    var elms = [].slice.call(
      document.querySelectorAll(
        "." +
          app.topNav.class +
          " ." +
          app.topNav.menu.class +
          " > ." +
          app.topNav.menu.itemClass +
          ""
      )
    );
    if (elms) {
      var found = false;
      elms.map(function (elm) {
        if (!elm.classList.contains("menu-control")) {
          fullWidth += elm.clientWidth;
          if (!found) {
            prevWidth += elm.clientWidth;
          }
          if (elm.classList.contains("active")) {
            found = true;
          }
        }
      });
    }

    var elm = targetMenu.querySelector(
      "." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class
    );
    if (prevWidth != fullWidth && fullWidth >= viewWidth) {
      elm.classList.add(app.topNav.control.showClass);
      controlWidth += controlNextWidth;
    } else {
      elm.classList.remove(app.topNav.control.showClass);
    }

    var elm = targetMenu.querySelector(
      "." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class
    );
    if (prevWidth >= viewWidth && fullWidth >= viewWidth) {
      elm.classList.add(app.topNav.control.showClass);
    } else {
      elm.classList.remove(app.topNav.control.showClass);
    }

    if (prevWidth >= viewWidth) {
      var finalScrollWidth = prevWidth - viewWidth + controlWidth;
      if (bodyStyle.getPropertyValue("direction") != "rtl") {
        targetMenu.style.marginLeft = "-" + finalScrollWidth + "px";
      } else {
        targetMenu.style.marginRight = "-" + finalScrollWidth + "px";
      }
    }
  }

  // handle menu next button click action
  var elm = document.querySelector("[" + app.topNav.control.buttonNext.toggleAttr + "]");
  if (elm) {
    elm.onclick = function (e) {
      e.preventDefault();
      handleMenuButtonAction(this, "next");
    };
  }

  // handle menu prev button click action
  var elm = document.querySelector("[" + app.topNav.control.buttonPrev.toggleAttr + "]");
  if (elm) {
    elm.onclick = function (e) {
      e.preventDefault();
      handleMenuButtonAction(this, "prev");
    };
  }

  function enableFluidContainerDrag(containerClassName) {
    const container = document.querySelector(containerClassName);
    if (!container) {
      return;
    }

    const menu = container.querySelector(".menu");
    const menuItem = menu.querySelectorAll(".menu-item:not(.menu-control)");

    let startX, scrollLeft, mouseDown;
    let menuWidth = 0;
    let maxScroll = 0;

    menuItem.forEach((element) => {
      menuWidth += element.offsetWidth;
    });

    container.addEventListener("mousedown", (e) => {
      mouseDown = true;
      startX = e.pageX;
      scrollLeft = menu.style.marginLeft ? parseInt(menu.style.marginLeft) : 0;
      maxScroll = container.offsetWidth - menuWidth;
    });

    container.addEventListener("touchstart", (e) => {
      mouseDown = true;
      const touch = e.targetTouches[0];
      startX = touch.pageX;
      scrollLeft = menu.style.marginLeft ? parseInt(menu.style.marginLeft) : 0;
      maxScroll = container.offsetWidth - menuWidth;
    });

    container.addEventListener("mouseup", () => {
      mouseDown = false;
    });

    container.addEventListener("touchend", () => {
      mouseDown = false;
    });

    container.addEventListener("mousemove", (e) => {
      if (!startX || !mouseDown) return;
      if (window.innerWidth < app.breakpoints.md) return;
      e.preventDefault();
      const x = e.pageX;
      const walkX = (x - startX) * 1;
      var totalMarginLeft = scrollLeft + walkX;
      if (totalMarginLeft <= maxScroll) {
        totalMarginLeft = maxScroll;
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class)
          .classList.remove("show");
      } else {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class)
          .classList.add("show");
      }
      if (menuWidth < container.offsetWidth) {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class)
          .classList.remove("show");
      }
      if (maxScroll > 0) {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class)
          .classList.remove("show");
      }
      if (totalMarginLeft > 0) {
        totalMarginLeft = 0;
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class)
          .classList.remove("show");
      } else {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class)
          .classList.add("show");
      }
      menu.style.marginLeft = totalMarginLeft + "px";
    });

    container.addEventListener("touchmove", (e) => {
      if (!startX || !mouseDown) return;
      if (window.innerWidth < app.breakpoints.md) return;
      e.preventDefault();

      const touch = e.targetTouches[0];
      const x = touch.pageX;
      const walkX = (x - startX) * 1;
      var totalMarginLeft = scrollLeft + walkX;
      if (totalMarginLeft <= maxScroll) {
        totalMarginLeft = maxScroll;
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class)
          .classList.remove("show");
      } else {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class)
          .classList.add("show");
      }
      if (menuWidth < container.offsetWidth) {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class)
          .classList.remove("show");
      }
      if (maxScroll > 0) {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonNext.class)
          .classList.remove("show");
      }
      if (totalMarginLeft > 0) {
        totalMarginLeft = 0;
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class)
          .classList.remove("show");
      } else {
        menu
          .querySelector("." + app.topNav.control.class + "." + app.topNav.control.buttonPrev.class)
          .classList.add("show");
      }
      menu.style.marginLeft = totalMarginLeft + "px";
    });
  }

  window.addEventListener("resize", function () {
    if (window.innerWidth >= app.breakpoints.md) {
      var targetElm = document.querySelector("." + app.topNav.class);
      if (targetElm) {
        targetElm.removeAttribute("style");
      }
      var targetElm2 = document.querySelector(
        "." + app.topNav.class + " ." + app.topNav.menu.class
      );
      if (targetElm2) {
        targetElm2.removeAttribute("style");
      }
      var targetElm3 = document.querySelectorAll(
        "." + app.topNav.class + " ." + app.topNav.menu.submenu.class
      );
      if (targetElm3) {
        targetElm3.forEach((elm3) => {
          elm3.removeAttribute("style");
        });
      }
      handlePageLoadMenuFocus();
    }
    enableFluidContainerDrag("." + app.topNav.class);
  });

  if (window.innerWidth >= app.breakpoints.md) {
    handlePageLoadMenuFocus();
    enableFluidContainerDrag("." + app.topNav.class);
  }
};

/* 14. Handle Top Nav - Sub Menu Toggle
------------------------------------------------ */
var handleTopNavToggle = function (menus, forMobile = false) {
  menus.map(function (menu) {
    menu.onclick = function (e) {
      e.preventDefault();

      if (!forMobile || (forMobile && document.body.clientWidth < app.breakpoints.md)) {
        var target = this.nextElementSibling;
        menus.map(function (m) {
          var otherTarget = m.nextElementSibling;
          if (otherTarget !== target) {
            slideUp(otherTarget);
            otherTarget
              .closest("." + app.topNav.menu.itemClass)
              .classList.remove(app.topNav.menu.expandClass);
            otherTarget
              .closest("." + app.topNav.menu.itemClass)
              .classList.add(app.topNav.menu.closedClass);
          }
        });

        slideToggle(target);
      }
    };
  });
};
var handleTopNavSubMenu = function () {
  "use strict";

  var menuBaseSelector =
    "." +
    app.topNav.class +
    " ." +
    app.topNav.menu.class +
    " > ." +
    app.topNav.menu.itemClass +
    "." +
    app.topNav.menu.hasSubClass;
  var submenuBaseSelector =
    " > ." +
    app.topNav.menu.submenu.class +
    " > ." +
    app.topNav.menu.itemClass +
    "." +
    app.topNav.menu.hasSubClass;

  // 14.1 Menu - Toggle / Collapse
  var menuLinkSelector = menuBaseSelector + " > ." + app.topNav.menu.itemLinkClass;
  var menus = [].slice.call(document.querySelectorAll(menuLinkSelector));
  handleTopNavToggle(menus, true);

  // 14.2 Menu - Submenu lvl 1
  var submenuLvl1Selector = menuBaseSelector + submenuBaseSelector;
  var submenusLvl1 = [].slice.call(
    document.querySelectorAll(submenuLvl1Selector + " > ." + app.topNav.menu.itemLinkClass)
  );
  handleTopNavToggle(submenusLvl1);

  // 14.3 submenu lvl 2
  var submenuLvl2Selector = menuBaseSelector + submenuBaseSelector + submenuBaseSelector;
  var submenusLvl2 = [].slice.call(
    document.querySelectorAll(submenuLvl2Selector + " > ." + app.topNav.menu.itemLinkClass)
  );
  handleTopNavToggle(submenusLvl2);
};

/* 15. Handle Top Nav - Mobile Top Menu Toggle
------------------------------------------------ */
var handleTopNavMobileToggle = function () {
  "use strict";

  var elm = document.querySelector("[" + app.topNav.mobile.toggleAttr + "]");
  if (elm) {
    elm.onclick = function (e) {
      e.preventDefault();
      slideToggle(document.querySelector("." + app.topNav.class));
      window.scrollTo(0, 0);
    };
  }
};

var addModalListeners = function () {
  var myModal = document.getElementById("myModal");
  myModal.addEventListener("show.bs.modal", function (event) {
    var button = event.relatedTarget; // Button that triggered the modal
    var url = button.getAttribute("data-bs-url"); // Extract URL from data-bs-url attribute

    var modalBody = myModal.querySelector(".modal-body");
    modalBody.innerHTML = "Loading..."; // Show loading message while fetching

    // Fetch the content from the URL
    fetch(url)
      .then((response) => response.text())
      .then((data) => {
        modalBody.innerHTML = data; // Inject the fetched content into modal-body
      })
      .catch((error) => {
        modalBody.innerHTML = "Error loading content."; // Error handling
        console.error("Error fetching modal content:", error);
      });
  });
};

var listenForHashScroll = function () {
  // handle when page loads with a hash location on the url.  the browser will
  // nateily scroll there, but it's not going to take into account the sticky header.
  // I am hijacking the scrolling here to make sure the header is accounted for.
  if (location.hash) {
    console.log("Page loaded with hash:", location.hash);
    var targetElm = document.querySelector(location.hash);
    var targetHeader = document.querySelector(app.header.id);
    var targetHeight = targetHeader.offsetHeight;
    if (targetElm) {
      var targetTop = targetElm.offsetTop - targetHeight - 24;
      setTimeout(() => {
        window.scrollTo({ top: targetTop, behavior: "smooth" });
      }, 100);
    }
  }
};

window.closeModal = function () {
  const modalClose = document.querySelector(".modal-header [data-bs-dismiss]");
  if (modalClose) {
    modalClose.click();
  }
};

window.copyToClipboard = function (id) {
  const urlEl = document.getElementById(id);
  if (!urlEl) {
    return;
  }
  const text = urlEl.textContent;
  if (!text) {
    return;
  }

  // Copy the text to the clipboard
  navigator.clipboard
    .writeText(text.trim())
    .then(() => showToast("Text copied to your clipboard."))
    .catch((error) => console.error("Copy failed:", error));
};

/* Application Controller
------------------------------------------------ */
export default class Global {
  constructor() {}
  init = () => {
    this.initComponent();
    this.initSidebar();
    this.initTopNav();
    this.initAppLoad();
  };

  initAppLoad = () => {
    document.querySelector("body").classList.add(app.init.class);
    listenForHashScroll();
  };

  initSidebar = () => {
    handleSidebarMenu();
    handleSidebarScrollMemory();
  };

  initTopNav = () => {
    handleUnlimitedTopNavRender();
    handleTopNavSubMenu();
    handleTopNavMobileToggle();
  };

  initComponent = () => {
    handleScrollTo();
    handleCardAction();
    handelTooltipPopoverActivation();
    handleToggleClass();
    handleCssVariable();
    addModalListeners();
  };

  scrollTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
}
