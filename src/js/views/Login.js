import {
  spinButton,
  unSpinButton,
  isElementVisible,
  insertDelay,
  slideDown,
  slideUp,
} from "../modules/Utils";

export default class Login {
  constructor() {
    this.formSel = '[data-js="login-form"]';
    this.formEl = document.querySelector(this.formSel);
    this.errorSel = "#error-card";
    this.errorEl = document.querySelector(this.errorSel);
    this.loginButtonId = "login-submit-button";
  }

  init = () => {
    this.formEl.addEventListener("submit", this.handleSubmit);
  };

  showError = (msg) => {
    this.errorEl.innerHTML = msg;
    slideDown(this.errorEl);
  };

  handleSubmit = async (e) => {
    e.preventDefault();

    // clear any errors
    if (isElementVisible(this.errorEl)) {
      slideUp(this.errorEl);
      this.errorEl.innerHTML = "";
      await insertDelay(CFG?.userInterfaceConfig?.animation?.speed || 300);
    }

    const form = e.target;
    const formData = new FormData(form);

    spinButton(this.loginButtonId);
    const response = await fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData).toString(),
    });
    const json = await response.json();
    if (json.error) {
      this.showError(json.errors.join(", "));
      unSpinButton(this.loginButtonId);
    } else {
      window.location.href = "/app";
    }
  };
}
