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
    this.googleButton = document.getElementById("google-start-login-button");
  }

  init = () => {
    this.formEl.addEventListener("submit", this.handleSubmit);
    this.googleButton.addEventListener("click", this.handleGoogeSignup);
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

  handleGoogeSignup = async (e) => {
    console.log("handleGoogeSignup", e);

    e.preventDefault();
    const requiredCheckbox = document.getElementById("customCheck1");
    if (!requiredCheckbox.checked) {
      this.showError("Please read and agree to the terms and conditions to continue.");
      return;
    } else {
      window.location.href = "/google/start-login";
    }
  };
}
