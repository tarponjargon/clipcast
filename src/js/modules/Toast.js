/* close toast on escape key */
const toastKeyListener = function (e) {
  if (e.key === "Escape") {
    const toastEl = document.getElementById("toast-2");
    if (!toastEl) return;
    const toast = bootstrap.Toast.getInstance(toastEl);
    if (toast) {
      toast.hide();
    }
    document.removeEventListener("keydown", toastKeyListener, false);
  }
};

// custom bootstrap toast wrapper for window
export const showToast = function (text, isError = false, delay = 3000) {
  const toastEl = document.getElementById("toast-2");
  if (!toastEl || !text || typeof text !== "string") return;
  toastEl.addEventListener("show.bs.toast", () => {
    if (isError) toastEl.classList.add("bg-danger", "text-white");
  });
  toastEl.addEventListener("hidden.bs.toast", () => {
    if (isError) toastEl.classList.remove("bg-danger", "text-white");
  });
  toastEl.addEventListener("shown.bs.toast", function () {
    document.addEventListener("keydown", toastKeyListener, false);
  });
  const bodyContainer = toastEl.querySelector(".toast-body");
  bodyContainer.innerHTML = "";
  const toast = new bootstrap.Toast(toastEl, { delay });
  bodyContainer.innerHTML = text;
  toast.show();
};
