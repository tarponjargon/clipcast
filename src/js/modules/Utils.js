// disables the button (and shows spinner) after submit
export function spinButton(id, text = "Submitting") {
  if (!id) {
    return false;
  }
  try {
    let button = document.getElementById(id);
    button.disabled = true;
    button.classList.remove("success-button");
    button.setAttribute("data-original-text", button.innerText);
    button.innerHTML = text + ` ... <i class="fa fa-spinner fa-spin"></i>`;
  } catch (e) {
    // console.log("problem with spinButton", e);
  }
  return true;
}

// undos the spinButton action
export function unSpinButton(id, text) {
  try {
    var button = document.getElementById(id);
    var hidden = button.getAttribute("data-original-text");
    text = typeof text !== "undefined" ? text : hidden;
    button.disabled = false;
    button.innerHTML = text;
  } catch (e) {}
  return true;
}

export const isElementVisible = function (e) {
  // this is borrowed from jquery's .is(":visible")
  if (!e) {
    return false;
  }
  return !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
};

export const insertDelay = function (ms) {
  // workaround for waiting for animation to complete
  return new Promise((resolve) => setTimeout(resolve, ms));
};

export const isMobile = function () {
  return (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
    window.innerWidth < 992
  );
};

export const slideUp = function (elm, duration = CFG.userInterfaceConfig.animation.speed) {
  if (!elm.classList.contains("transitioning")) {
    elm.classList.add("transitioning");
    elm.style.transitionProperty = "height, margin, padding";
    elm.style.transitionDuration = duration + "ms";
    elm.style.boxSizing = "border-box";
    elm.style.height = elm.offsetHeight + "px";
    elm.offsetHeight;
    elm.style.overflow = "hidden";
    elm.style.height = 0;
    elm.style.paddingTop = 0;
    elm.style.paddingBottom = 0;
    elm.style.marginTop = 0;
    elm.style.marginBottom = 0;
    window.setTimeout(() => {
      elm.style.display = "none";
      elm.style.removeProperty("height");
      elm.style.removeProperty("padding-top");
      elm.style.removeProperty("padding-bottom");
      elm.style.removeProperty("margin-top");
      elm.style.removeProperty("margin-bottom");
      elm.style.removeProperty("overflow");
      elm.style.removeProperty("transition-duration");
      elm.style.removeProperty("transition-property");
      elm.classList.remove("transitioning");
    }, duration);
  }
};

export const slideDown = function (elm, duration = CFG.userInterfaceConfig.animation.speed) {
  if (!elm.classList.contains("transitioning")) {
    elm.classList.add("transitioning");
    elm.style.removeProperty("display");
    let display = window.getComputedStyle(elm).display;
    if (display === "none") display = "block";
    elm.style.display = display;
    let height = elm.offsetHeight;
    elm.style.overflow = "hidden";
    elm.style.height = 0;
    elm.style.paddingTop = 0;
    elm.style.paddingBottom = 0;
    elm.style.marginTop = 0;
    elm.style.marginBottom = 0;
    elm.offsetHeight;
    elm.style.boxSizing = "border-box";
    elm.style.transitionProperty = "height, margin, padding";
    elm.style.transitionDuration = duration + "ms";
    elm.style.height = height + "px";
    elm.style.removeProperty("padding-top");
    elm.style.removeProperty("padding-bottom");
    elm.style.removeProperty("margin-top");
    elm.style.removeProperty("margin-bottom");
    window.setTimeout(() => {
      elm.style.removeProperty("height");
      elm.style.removeProperty("overflow");
      elm.style.removeProperty("transition-duration");
      elm.style.removeProperty("transition-property");
      elm.classList.remove("transitioning");
    }, duration);
  }
};

export const slideToggle = function (elm, duration = CFG.userInterfaceConfig.animation.speed) {
  if (window.getComputedStyle(elm).display === "none") {
    return slideDown(elm, duration);
  } else {
    return slideUp(elm, duration);
  }
};

export const waitForSelector = (sel) => {
  return new Promise((resolve, reject) => {
    if (!sel) {
      reject("no selector passed");
      return false;
    }
    let r = 0;
    let i = setInterval(() => {
      r += 1;
      if (r > 80) {
        clearInterval(i);
        reject("selector never appeared " + sel);
      }
      const el = document.querySelector(sel);
      if (el) {
        clearInterval(i);
        resolve(el);
      }
    }, 100);
  });
};
