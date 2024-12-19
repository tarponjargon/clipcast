document.addEventListener("DOMContentLoaded", async () => {
  const urlInput = document.getElementById("url");
  const form = document.getElementById("urlForm");
  const errorDiv = document.getElementById("error");

  const appUrl = "https://clipcast.duckdns.org/app/add-url";

  // Populate the input field with the current page's URL
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]?.url) {
      urlInput.value = tabs[0].url;
    }
  });

  // Handle form submission
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent form from reloading the popup

    const url = encodeURIComponent(urlInput.value);
    window.open(`${appUrl}?url=${url}`, "_blank");
  });
});
