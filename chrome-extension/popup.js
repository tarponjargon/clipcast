document.addEventListener("DOMContentLoaded", async () => {
  const urlInput = document.getElementById("url");
  const form = document.getElementById("urlForm");
  const errorDiv = document.getElementById("error");

  // Populate the input field with the current page's URL
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]?.url) {
      urlInput.value = tabs[0].url;
    }
  });

  // Handle form submission
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent form from reloading the popup

    const url = urlInput.value;
    try {
      const response = await fetch("https://dev.clipcast.local/partials/app/add-podcast-url", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ url }),
      });

      if (response.status === 403) {
        errorDiv.style.display = "block";
      } else {
        errorDiv.style.display = "none";
        alert("URL submitted successfully!");
      }
    } catch (error) {
      console.error("An error occurred:", error);
      errorDiv.textContent = "An unexpected error occurred. Please try again. " + error;
      errorDiv.style.display = "block";
    }
  });
});
