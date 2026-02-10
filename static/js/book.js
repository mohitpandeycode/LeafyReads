lucide.createIcons();
$(function () {
  // === Element & audio references ===
  const $flipbook = $(".flipbook");
  const $container = $("#container");
  const $pages = $(".flipbook .page");
  const $spine = $("#spine-illusion");
  const $prevBtn = $("#prevBtn");
  const $pageImages = $(".pagestyle img");
  const $nextBtn = $("#nextBtn");
  const $play = $("#play");
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

  // === Default dimensions ===
  let currentWidth = 880;
  let currentHeight = 580;

  // === Add blank/end page logic ===
  const totalPages = $(".flipbook .page").length;
  if (totalPages % 2 === 0) {
    // Even → Add blank + end
    const blankPage = `
      <article class="page">
        <div class="pagestyle"></div>
      </article>
    `;
    const endPage = `
      <article class="page cover hard" style="border: 2px solid white;">
        <img src="/static/images/coverback2.png" alt="Back Cover Image" class="cover-image" />
      </article>
    `;
    $flipbook.append(blankPage + endPage);
  } else {
    // Odd → Add only end
    const endPage = `
      <article class="page cover hard" style="border: 2px solid white;">
        <img src="/static/images/coverback2.png" alt="Back Cover Image" class="cover-image" />
      </article>
    `;
    $flipbook.append(endPage);
  }

  // === Go to Page Logic ===
  const $pageInput = $("#pageInput");
  const $goBtn = $("#goBtn");
  const toast = document.getElementById('toast-notification');
  const toastMessage = document.getElementById('toast-message');
  function showToast(message) {
      toastMessage.textContent = message;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3000);
  }
  function goToPage() {
    // 1. Get the page number the user typed
    let pageNumber = parseInt($pageInput.val());
    const totalPages = $flipbook.turn("pages");

    // 2. Validation: Ensure it's a real page
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      
      // 3. Auto flip to that pageq to the pge number
      $flipbook.turn("page", pageNumber);
      
      // Play sound
      click.currentTime = 0;
      click.play();
      
      // Clear input and remove focus
      $pageInput.val('');
      $pageInput.blur();
      
    } else {
      showToast(`That page does not exist. Please enter 1 to ${totalPages}.`);
    }
  }

  // Event Listener: Click "Go" button
  $goBtn.on("click", goToPage);

  // Event Listener: Press "Enter" key inside input
  $pageInput.on("keypress", function (e) {
    if (e.which === 13) { // 13 is the Enter key
      goToPage();
    }
  });
  // === Initialize flipbook plugin ===
  $flipbook.turn({
    width: currentWidth,
    height: currentHeight,
    autoCenter: true,
    duration: 1000,
    acceleration: true,
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
        $spine.attr("hidden", true);
      },
      // UPDATED SECTION
      turned(e, page) {
        const total = $flipbook.turn("pages");
        $spine.toggle(page > 1 && page < total);
        
        // Progress Bar
        const percent = (page / total) * 100;
        const bar = document.getElementById("progress-bar");
        bar.style.width = `${percent}%`;
        bar.setAttribute("aria-valuenow", percent.toFixed(0));

        // Page Number Update
        $(".pagesinfo").text(`Page ( ${page} / ${total} )`);
      },
    },
  });

  // INITIALIZE TEXT ON LOAD
  const startPage = $flipbook.turn("page");
  const startTotal = $flipbook.turn("pages");
  $(".pagesinfo").text(`Page ( ${startPage} / ${startTotal} )`);



  // === Navigation buttons ===
  $("#prevBtn").click(() => $flipbook.turn("previous"));
  $("#nextBtn").click(() => {
    $flipbook.turn("next");
    $play.prop("disabled", false);
  });

  // === Keyboard navigation ===
  $(document).keydown((e) => {
    if ($(e.target).is("input, textarea")) {
      return;
    }

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
      case "Escape":
        click.currentTime = 0;
        click.play();
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

  // === Detect fullscreen exit (Esc pressed or user clicked exit) ===
  document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
      // Restore normal styles/layout
      applyNormalStyles();
      document.querySelector(".co-header").style.display = "block";
      isFullscreen = false;
      if (fullscreenBtn) fullscreenBtn.innerText = "⛶";
    }
  });
  // === Fullscreen toggle ===
  function toggleFullscreen() {
    click.currentTime = 0;
    click.play();
    if (!document.fullscreenElement) {
      document.documentElement
        .requestFullscreen()
        .catch((err) => alert(`Error: ${err.message}`));
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
    $container.css({ width: "1320px", height: "820px", marginTop: "0px" });
    $flipbook.css({ width: "1300px", height: "800px" });
    $pageImages.css({width:"115%"})
    document.body.classList.add("fullscreen");
    $nextBtn.css({ right: "3%" });
    $prevBtn.css({ left: "3%" });
    $flipbook.turn("size", 1300, 800);
  }

  function applyNormalStyles() {
    $container.css({ width: "900px", height: "600px", marginTop: "50px" });
    $flipbook.css({ width: "880px", height: "580px" });
    $pageImages.css({width:"125%"})
    document.body.classList.remove("fullscreen");
    $nextBtn.css({ right: "15%" });
    $prevBtn.css({ left: "15%" });
    $flipbook.turn("size", 880, 580);
  }

  // === Dark mode toggle ===
  function toggleDarkMode() {
    const isDark = document.body.classList.toggle("dark-mode");
    click.currentTime = 0;
    click.play();
    document.documentElement.classList.toggle("dark-mode");
    localStorage.setItem("darkMode", isDark ? "enabled" : "disabled");
    darkModeBtn.innerText = isDark ? "☀️" : "🌙";
  }

  // === Mute toggle ===
  function toggleMute() {
    click.play();
    isMuted = !isMuted;
    flipForward.muted = isMuted;
    flipBackward.muted = isMuted;
    muteBtn.innerText = isMuted ? "🔇" : "🔊";
  }

  // === Persist dark mode ===
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    document.documentElement.classList.add("dark-mode");
    if (darkModeBtn) darkModeBtn.innerText = "☀️";
  }
});

// === Alert auto-dismiss ===
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
setTimeout(hideAlert, 7000);
closeButton?.addEventListener("click", hideAlert);

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
