lucide.createIcons();
$(function () {
  const $flipbook = $(".flipbook");
  const $spine = $("#spine-illusion");
  const flipForward = document.getElementById("flipForward");
  const flipBackward = document.getElementById("flipBackward");
  const fullscreenBtn = document.getElementById("fullscreenBtn");
  const darkModeBtn = document.getElementById("darkModeBtn");
  const muteBtn = document.getElementById("muteBtn");
  const click = new Audio("/static/sounds/click.mp3");

  // Apply saved dark mode preference
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    document.documentElement.classList.add("dark-mode");

    if (darkModeBtn) {
      darkModeBtn.innerText = "☀️";
    }
  }

  let lastPage = 1;
  let isMuted = false;

  $flipbook.turn({
    width: 1300,
    height: 750,
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
      document.documentElement
        .requestFullscreen()
        .catch((err) => alert(`Error: ${err.message}`));
      fullscreenBtn.innerText = "🗗";
      document.querySelector(".co-header").style.display = "none";
    } else {
      click.currentTime = 0;
      click.play();
      document.exitFullscreen();
      fullscreenBtn.innerText = "⛶";
      document.querySelector(".co-header").style.display = "block";
    }
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
});

const myAlert = document.getElementById("myAlert");
const closeButton = myAlert.querySelector(".alert-close-btn");

function hideAlert() {
  myAlert.classList.add("alert-hide");
  myAlert.addEventListener(
    "transitionend",
    () => {
      if (myAlert.classList.contains("alert-hide")) {
        myAlert.remove();
      }
    },
    { once: true }
  );
}
setTimeout(hideAlert, 4000);
closeButton.addEventListener("click", hideAlert);
const shortcutsBtn = document.getElementById("shortcutsBtn");
const shortcutsPanel = document.getElementById("shortcutsPanel");
const closeShortcuts = document.getElementById("closeShortcuts");

shortcutsBtn?.addEventListener("click", () => {
  shortcutsPanel.classList.toggle("visible");
});

closeShortcuts?.addEventListener("click", () => {
  shortcutsPanel.classList.remove("visible");
});
