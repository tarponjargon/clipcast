import {
  spinButton,
  unSpinButton,
  isElementVisible,
  insertDelay,
  slideDown,
  slideUp,
} from "../modules/Utils";

export default class Signup {
  constructor() {
    this.formSel = '[data-js="signup-form"]';
    this.formEl = document.querySelector(this.formSel);
    this.errorSel = "#error-card";
    this.errorEl = document.querySelector(this.errorSel);
    this.signupButtonId = "signup-submit-button";
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

    spinButton(this.signupButtonId);
    const response = await fetch("/api/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData).toString(),
    });
    const json = await response.json();
    if (json.error) {
      this.showError(json.errors.join(", "));
      unSpinButton(this.signupButtonId);
    } else {
      window.location.href = "/app";
    }
  };
}
