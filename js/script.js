// ── Hamburger / Nav toggle ─────────────────────────────
const hamburger = document.getElementById("hamburger");
const nav = document.getElementById("main-nav");
if (hamburger && nav) {
  hamburger.addEventListener("click", () => {
    nav.classList.toggle("open");
    hamburger.classList.toggle("fa-bars");
    hamburger.classList.toggle("fa-times");
  });
}

// ── Scroll-top button ──────────────────────────────────
const scrollTopBtn = document.querySelector(".scroll-top");
if (scrollTopBtn) {
  window.addEventListener("scroll", () => {
    scrollTopBtn.classList.toggle("visible", window.scrollY > 300);
  });
}

// ── File input display ─────────────────────────────────
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");
if (fileInput && fileName) {
  fileInput.addEventListener("change", function () {
    fileName.value = this.files[0] ? this.files[0].name : "No file selected";
    if (this.files[0]) {
      demoOptions.forEach((opt) => {
        opt.classList.remove("selected");
        const radio = opt.querySelector('input[type="radio"]');
        if (radio) radio.checked = false;
      });
    }
  });
}
// ── Demo Selection ─────────────────────────────────────
const demoOptions = document.querySelectorAll(".demo-option");
demoOptions.forEach((option) => {
  option.addEventListener("click", function () {
    // Remove selected class from others
    demoOptions.forEach((opt) => opt.classList.remove("selected"));
    // Add to this one
    this.classList.add("selected");
    // Check the radio
    const radio = this.querySelector('input[type="radio"]');
    if (radio) radio.checked = true;
    // Clear file input if a demo is selected
    if (fileInput) fileInput.value = "";
    if (fileName) fileName.value = "No file selected";
  });
});

const analysisForm = document.getElementById("analysis-form");
if (analysisForm) {
  analysisForm.addEventListener("submit", function (e) {
    e.preventDefault();
    showLoader();

    const formData = new FormData(this);
    fetch("run_analysis.php", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "error") {
          alert("Error: " + data.message);
          hideLoader();
        }
        // Background process started, startPolling handles the rest
      })
      .catch((err) => {
        console.error("Error starting analysis", err);
        alert("Failed to start analysis. Check console for details.");
        hideLoader();
      });
  });
}

let pollInterval;

function showLoader() {
  const loader = document.getElementById("loader");
  if (loader) {
    loader.classList.add("active");
    startPolling();
  }
}

function hideLoader() {
  const loader = document.getElementById("loader");
  if (loader) {
    loader.classList.remove("active");
    if (pollInterval) clearInterval(pollInterval);
  }
}

const cancelBtn = document.getElementById("cancel-analysis");
if (cancelBtn) {
  cancelBtn.addEventListener("click", () => {
    hideLoader();
    // Optional: could notify server to kill process, but UI side is most immediate
  });
}

function startPolling() {
  const progressBar = document.getElementById("progress-bar");
  const percentageText = document.getElementById("percentage");
  const loaderText = document.getElementById("loader-text");

  let pollCount = 0;
  if (pollInterval) clearInterval(pollInterval);

  pollInterval = setInterval(() => {
    fetch("progress.php")
      .then((response) => response.json())
      .then((data) => {
        const progress = data.progress || 0;
        if (progressBar) progressBar.style.width = progress + "%";
        if (percentageText) percentageText.innerText = progress + "%";

        if (progress >= 100) {
          clearInterval(pollInterval);
          if (loaderText)
            loaderText.innerText = "Processing Complete! Redirecting...";
          setTimeout(() => {
            window.location.href = "analysis.php?status=complete";
          }, 2000);
        } else if (progress >= 60) {
          if (loaderText) loaderText.innerText = "Rendering output video...";
        } else if (progress >= 55) {
          if (loaderText) loaderText.innerText = "Analyzing team possession...";
        } else if (progress >= 5) {
          if (loaderText) loaderText.innerText = "Tracking players and ball...";
        } else {
          pollCount++;
          if (pollCount > 60) {
            if (loaderText)
              loaderText.innerText =
                "Still starting AI model (this may take a minute)...";
          }
        }
      })
      .catch((err) => console.error("Error polling progress", err));
  }, 1000);

  window.addEventListener("beforeunload", () => clearInterval(pollInterval));
}
