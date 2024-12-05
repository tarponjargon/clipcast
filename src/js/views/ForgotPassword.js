import {
  spinButton,
  unSpinButton,
  isElementVisible,
  insertDelay,
  slideDown,
  slideUp,
} from "../modules/Utils";

export default class ForgotPassword {
  constructor() {
    this.formSel = '[data-js="forgotpassword-form"]';
    this.formEl = document.querySelector(this.formSel);
    this.errorSel = "#error-card";
    this.errorEl = document.querySelector(this.errorSel);
    this.successSel = "#success-card";
    this.successEl = document.querySelector(this.successSel);
    this.buttonId = "forgotpassword-submit-button";
  }

  init = () => {
    this.formEl.addEventListener("submit", this.handleSubmit);
  };

  showError = (msg) => {
    this.errorEl.innerHTML = msg;
    slideDown(this.errorEl);
  };

  showSuccess = (msg) => {
    this.successEl.innerHTML = msg;
    slideDown(this.successEl);
  };

  handleSubmit = async (e) => {
    e.preventDefault();

    // clear any existing feedback containers
    let feedbackDivVisible = false;
    if (isElementVisible(this.errorEl)) {
      slideUp(this.errorEl);
      this.errorEl.innerHTML = "";
      feedbackDivVisible = true;
    }

    if (isElementVisible(this.successEl)) {
      slideUp(this.successEl);
      this.successEl.innerHTML = "";
      feedbackDivVisible = true;
    }

    if (feedbackDivVisible) {
      await insertDelay(CFG?.userInterfaceConfig?.animation?.speed || 300);
    }

    const form = e.target;
    const formData = new FormData(form);

    spinButton(this.buttonId);
    const response = await fetch("/api/forgotpassword", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData).toString(),
    });
    const json = await response.json();
    if (json.error) {
      this.showError(json.errors.join(", "));
    } else {
      this.showSuccess(
        "If you have an account with us, you will receive an email with \
        password reset instructions. If it does not arrive, please \
        check your spam folder."
      );
    }
    unSpinButton(this.buttonId);
  };
}
