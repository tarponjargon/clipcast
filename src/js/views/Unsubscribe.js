import {
  spinButton,
  unSpinButton,
  isElementVisible,
  insertDelay,
  slideDown,
  slideUp,
} from "../modules/Utils";

export default class Unsubscribe {
  constructor() {
    this.formSel = '[data-js="unsubscribe-form"]';
    this.formEl = document.querySelector(this.formSel);
    this.errorSel = "#error-card";
    this.errorEl = document.querySelector(this.errorSel);
    this.successSel = "#success-card";
    this.successEl = document.querySelector(this.successSel);
    this.subscribeButtonId = "unsubscribe-button";
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

    spinButton(this.subscribeButtonId);
    const response = await fetch("/api/unsubscribe", {
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
      this.showSuccess("You are now unsubscribed");
    }
    unSpinButton(this.subscribeButtonId);
  };
}
