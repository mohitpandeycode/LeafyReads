$(function () {
  // === Element & audio references ===
  const $flipbook = $(".flipbook");
  const $container = $("#container");
  const $pages = $(".flipbook .page");
  const $spine = $("#spine-illusion");
  const $prevBtn = $("#prevBtn");
  const $nextBtn = $("#nextBtn");
  const flipForward = document.getElementById("flipForward");
  const flipBackward = document.getElementById("flipBackward");
  const fullscreenBtn = document.getElementById("fullscreenBtn");
  const darkModeBtn = document.getElementById("darkModeBtn");
  const muteBtn = document.getElementById("muteBtn");
  const click = new Audio("/static/sounds/click.mp3");

  // === State variables ===
  let isFullscreen = false;
  let lastPage = 1;
  let isMuted = false;

  // === Default dimensions (non-fullscreen mode) ===
  let currentWidth = 880;
  let currentHeight = 580;

  // === Initialize flipbook plugin ===
  $flipbook.turn({
    width: currentWidth,
    height: currentHeight,
    autoCenter: true,
    elevation: 50,
    gradients: true,
    when: {
      // 🔁 Page is turning
      turning(event, page) {
        if (!isMuted) {
          if (page > lastPage) {
            flipForward.currentTime = 0;
            flipForward.play(); // Play forward flip sound
          } else if (page < lastPage) {
            flipBackward.currentTime = 0;
            flipBackward.play(); // Play backward flip sound
          }
        }
        lastPage = page;

        // ⛔ Hide the spine illusion while turning
        $spine.attr("hidden", true);
      },

      // ✅ Page has turned
      turned(e, page) {
        const totalPages = $flipbook.turn("pages");

        // 🎯 Show spine only if not on first or last page
        $spine.toggle(page > 1 && page < totalPages);

        // 📊 Update progress bar
        const progressPercent = (page / totalPages) * 100;
        const progressBar = document.getElementById("progress-bar");
        progressBar.style.width = `${progressPercent}%`;
        progressBar.setAttribute("aria-valuenow", progressPercent.toFixed(0));
      },
    },
  });

  // === Button click handlers ===
  $("#prevBtn").click(() => $flipbook.turn("previous"));
  $("#nextBtn").click(() => $flipbook.turn("next"));

  // === Keyboard shortcut handlers ===
  $(document).keydown((e) => {
    switch (e.key) {
      case "ArrowRight":
        $flipbook.turn("next");
        break;
      case "ArrowLeft":
        $flipbook.turn("previous");
        break;
      case "f":
      case "F":
        click.currentTime = 0;
        click.play();
        toggleFullscreen();
        break;
      case "d":
      case "D":
        click.currentTime = 0;
        click.play();
        toggleDarkMode();
        break;
      case "m":
      case "M":
        click.currentTime = 0;
        click.play();
        toggleMute();
        break;
    }
  });

  // === Button listeners ===
  fullscreenBtn?.addEventListener("click", toggleFullscreen);
  darkModeBtn?.addEventListener("click", toggleDarkMode);
  muteBtn?.addEventListener("click", toggleMute);

  // === Fullscreen toggle logic ===
  function toggleFullscreen() {
    click.currentTime = 0;
    click.play();

    if (!document.fullscreenElement) {
      // Enter fullscreen
      document.documentElement.requestFullscreen().catch((err) => alert(`Error: ${err.message}`));
      fullscreenBtn.innerText = "🗗";
      document.querySelector(".co-header").style.display = "none";
      isFullscreen = true;

      applyFullscreenStyles();
    } else {
      // Exit fullscreen
      document.exitFullscreen();
      fullscreenBtn.innerText = "⛶";
      document.querySelector(".co-header").style.display = "block";
      isFullscreen = false;

      applyNormalStyles();
    }
  }

  // === Apply styles for fullscreen ===
  function applyFullscreenStyles() {
    $container.css({ width: "1320px", height: "820px", marginTop: "0px" });
    $flipbook.css({ width: "1300px", height: "800px" });
    $pages.css({ width: "650px", height: "800px", fontSize: "1rem" });
    $nextBtn.css({ right: "3%" });
    $prevBtn.css({ left: "3%" });

    $flipbook.turn("size", 1300, 800);
  }

  // === Apply styles for normal (non-fullscreen) view ===
  function applyNormalStyles() {
    $container.css({ width: "900px", height: "600px", marginTop: "50px" });
    $flipbook.css({ width: "880px", height: "580px" });
    $pages.css({ width: "440px", height: "580px", fontSize: "0.7rem" });
    $nextBtn.css({ right: "15%" });
    $prevBtn.css({ left: "15%" });

    $flipbook.turn("size", 880, 580);
  }

  // === Toggle dark mode and save preference ===
  function toggleDarkMode() {
    const isDark = document.body.classList.toggle("dark-mode");
    click.currentTime = 0;
    click.play();
    document.documentElement.classList.toggle("dark-mode");

    localStorage.setItem("darkMode", isDark ? "enabled" : "disabled");
    darkModeBtn.innerText = isDark ? "☀️" : "🌙";
  }

  // === Toggle sound mute/unmute ===
  function toggleMute() {
    click.play();
    isMuted = !isMuted;
    flipForward.muted = isMuted;
    flipBackward.muted = isMuted;
    muteBtn.innerText = isMuted ? "🔇" : "🔊";
  }

  // === Apply dark mode if saved in localStorage ===
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    document.documentElement.classList.add("dark-mode");
    if (darkModeBtn) darkModeBtn.innerText = "☀️";
  }
});

// === Alert dismiss logic ===
const myAlert = document.getElementById("myAlert");
const closeButton = myAlert?.querySelector(".alert-close-btn");

function hideAlert() {
  myAlert?.classList.add("alert-hide");
  myAlert?.addEventListener(
    "transitionend",
    () => {
      if (myAlert?.classList.contains("alert-hide")) {
        myAlert.remove();
      }
    },
    { once: true }
  );
}
setTimeout(hideAlert, 4000); // Auto-hide after 3s
closeButton?.addEventListener("click", hideAlert); // Manual close

// === Shortcuts panel toggle ===
const shortcutsBtn = document.getElementById("shortcutsBtn");
const shortcutsPanel = document.getElementById("shortcutsPanel");
const closeShortcuts = document.getElementById("closeShortcuts");

shortcutsBtn?.addEventListener("click", () => {
  shortcutsPanel.classList.toggle("visible");
});
closeShortcuts?.addEventListener("click", () => {
  shortcutsPanel.classList.remove("visible");
});
