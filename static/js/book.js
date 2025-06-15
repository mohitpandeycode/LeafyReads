lucide.createIcons();
$(function () {
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

  let isFullscreen = false;
  let lastPage = 1;
  let isMuted = false;

  // === Default (non-fullscreen) dimensions ===
  let currentWidth = 880;
  let currentHeight = 580;

  $flipbook.turn({
    width: currentWidth,
    height: currentHeight,
    autoCenter: true,
    elevation: 50,
    gradients: true,
    when: {
      turning(event, page) {
        if (!isMuted) {
          if (page > lastPage) {
            flipForward.currentTime = 0;
            flipForward.play();
          } else if (page < lastPage) {
            flipBackward.currentTime = 0;
            flipBackward.play();
          }
        }
        lastPage = page;
      },
      turned(e, page) {
        const totalPages = $flipbook.turn("pages");
        $spine.toggle(page > 1 && page < totalPages);

        const progressPercent = (page / totalPages) * 100;
        const progressBar = document.getElementById("progress-bar");
        progressBar.style.width = `${progressPercent}%`;
        progressBar.setAttribute("aria-valuenow", progressPercent.toFixed(0));
      },
    },
  });

  $("#prevBtn").click(() => $flipbook.turn("previous"));
  $("#nextBtn").click(() => $flipbook.turn("next"));

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

  fullscreenBtn?.addEventListener("click", toggleFullscreen);
  darkModeBtn?.addEventListener("click", toggleDarkMode);
  muteBtn?.addEventListener("click", toggleMute);

  function toggleFullscreen() {
    click.currentTime = 0;
    click.play();

    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => alert(`Error: ${err.message}`));
      fullscreenBtn.innerText = "🗗";
      document.querySelector(".co-header").style.display = "none";
      isFullscreen = true;

      applyFullscreenStyles();
    } else {
      document.exitFullscreen();
      fullscreenBtn.innerText = "⛶";
      document.querySelector(".co-header").style.display = "block";
      isFullscreen = false;

      applyNormalStyles();
    }
  }

  function applyFullscreenStyles() {
    $container.css({ width: "1320px", height: "820px",marginTop:"0px" });
    $flipbook.css({ width: "1300px", height: "800px" });
    $pages.css({ width: "650px", height: "800px",fontSize:"0.85rem"});
     $nextBtn.css({ right: "3%"});
    $prevBtn.css({ left: "3%"});

    $flipbook.turn("size", 1300, 800);
  }

  function applyNormalStyles() {
    $container.css({ width: "900px", height: "600px",marginTop:"50px" });
    $flipbook.css({ width: "880px", height: "580px" });
    $pages.css({ width: "440px", height: "580px",fontSize:"0.6rem" });
    $nextBtn.css({ right: "15%"});
    $prevBtn.css({ left: "15%"});

    $flipbook.turn("size", 880, 580);
  }

  function toggleDarkMode() {
    const isDark = document.body.classList.toggle("dark-mode");
    click.currentTime = 0;
    click.play();
    document.documentElement.classList.toggle("dark-mode");

    localStorage.setItem("darkMode", isDark ? "enabled" : "disabled");
    darkModeBtn.innerText = isDark ? "☀️" : "🌙";
  }

  function toggleMute() {
    click.play();
    isMuted = !isMuted;
    flipForward.muted = isMuted;
    flipBackward.muted = isMuted;
    muteBtn.innerText = isMuted ? "🔇" : "🔊";
  }

  // === Dark mode on load ===
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    document.documentElement.classList.add("dark-mode");
    if (darkModeBtn) darkModeBtn.innerText = "☀️";
  }
});

// === Alert Logic ===
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
setTimeout(hideAlert, 3000);
closeButton?.addEventListener("click", hideAlert);

// === Shortcuts Panel ===
const shortcutsBtn = document.getElementById("shortcutsBtn");
const shortcutsPanel = document.getElementById("shortcutsPanel");
const closeShortcuts = document.getElementById("closeShortcuts");

shortcutsBtn?.addEventListener("click", () => {
  shortcutsPanel.classList.toggle("visible");
});
closeShortcuts?.addEventListener("click", () => {
  shortcutsPanel.classList.remove("visible");
});
