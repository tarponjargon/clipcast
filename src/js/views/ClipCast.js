import "shikwasa/dist/style.css";
import { Player } from "shikwasa";
import { waitForSelector, slideDown, slideUp, isElementVisible } from "../modules/Utils";

export default class ClipCast {
  constructor() {
    this.player = undefined;
    this.podcastCloseBtn = document.getElementById("podcast-player-close");
    this.playIconHTML = '<i class="fa fa-play-circle fa-3x"></i>';
    this.stopIconHTML = '<i class="fa fa-pause-circle fa-3x"></i>';
    this.currentlyPlayingEl = undefined;
    this.topDeleteAllButton = document.getElementById("top-delete-all-btn");
  }

  init = () => {
    return new Promise((resolve, reject) => {
      this.checkAllListener();
      this.checkboxListener();
      this.playPodcastListener();
      this.closePodcastListener();
      setInterval(() => {
        this.checkForNewPodcasts();
      }, 30000);
    });
  };

  checkForNewPodcasts = async () => {
    const totalEl = document.querySelector("[data-total-episodes]");
    if (!totalEl) return;
    const viewableEpisodes = parseInt(totalEl.getAttribute("data-total-episodes"));
    const res = await fetch("/api/total-episodes");
    const data = await res.json();
    const totalEpisodes = data.totalEpisodes;
    if (viewableEpisodes < totalEpisodes) {
      window.location.reload();
    }
  };

  checkAllListener = () => {
    const selectAllCheckbox = document.getElementById("check-all");
    if (!selectAllCheckbox) return;
    selectAllCheckbox.addEventListener("change", () => {
      const itemCheckboxes = document.querySelectorAll('[type="checkbox"]');
      itemCheckboxes.forEach((checkbox) => {
        checkbox.checked = selectAllCheckbox.checked;
      });
    });
  };

  checkboxListener = () => {
    const allCheckBoxes = document.querySelectorAll('[type="checkbox"]');
    if (!allCheckBoxes.length) return;
    allCheckBoxes.forEach((box) => {
      box.addEventListener("change", () => {
        this.deleteButtonVisibility();
      });
    });
  };

  deleteButtonVisibility = () => {
    const allCheckBoxes = document.querySelectorAll('[type="checkbox"]');
    const checkedBoxes = Array.from(allCheckBoxes).filter((box) => box.checked);
    if (checkedBoxes.length) {
      if (isElementVisible(this.topDeleteAllButton)) return;
      slideDown(this.topDeleteAllButton);
    } else {
      if (!isElementVisible(this.topDeleteAllButton)) return;
      slideUp(this.topDeleteAllButton);
    }
  };

  stopPodcast = () => {
    if (this.player) {
      document.removeEventListener("keydown", this.playerKeyListener, false);
      this.player.pause();
      this.player.destroy();
      this.player = undefined;
      this.podcastCloseBtn.style.display = "none";
      // reset all row play icons
      document.querySelectorAll("a[data-mp3]").forEach((element) => {
        element.innerHTML = this.playIconHTML;
      });
    }
  };

  playPodcast = (element) => {
    this.currentlyPlayingEl = element;

    // Play the selected podcast
    this.player = new Player({
      container: document.getElementById("podcast-player"),
      fixed: {
        type: "fixed",
        position: "bottom",
      },
      themeColor: "#000000",
      audio: {
        title: this.currentlyPlayingEl.getAttribute("data-title"),
        artist: this.currentlyPlayingEl.getAttribute("data-author"),
        cover: this.currentlyPlayingEl.getAttribute("data-image"),
        src: this.currentlyPlayingEl.getAttribute("data-mp3"),
        duration: this.currentlyPlayingEl.getAttribute("data-duration"),
        album: this.currentlyPlayingEl.getAttribute("data-hostname"),
        live: false,
      },
      loop: false,
    });

    // console.log("Player", this.player);

    this.player.audio.addEventListener("play", () => {
      // console.log("The podcast is now playing");
      this.podcastCloseBtn.style.display = "block";
      this.currentlyPlayingEl.innerHTML = this.stopIconHTML;
    });

    this.player.audio.addEventListener("pause", () => {
      // console.log("The podcast is now paused");
      this.currentlyPlayingEl.innerHTML = this.playIconHTML;
    });

    this.player.audio.addEventListener("ended", () => {
      // console.log("The podcast is now ended");
      this.currentlyPlayingEl.innerHTML = this.playIconHTML;
    });

    document.addEventListener("keydown", this.playerKeyListener, false);

    // Wait for the player to be ready and play the podcast, show the close button
    // bind the playing icon to the current podcast
    waitForSelector("#podcast-player .shk-btn_toggle").then((el) => {
      this.player.play();
    });
  };

  playerKeyListener = (e) => {
    if (e.key === "Escape") {
      this.stopPodcast();
      document.removeEventListener("keydown", this.playerKeyListener, false);
    }
    if (e.key === " ") {
      e.preventDefault();
      if (this.player.audio.paused) {
        this.player.play();
      } else {
        this.player.pause();
      }
    }
  };

  determinePodcastState = (el) => {
    // console.log("determinePodcastState", el);
    if (this.player) {
      if (this.player.audio.src === el.getAttribute("data-mp3")) {
        if (this.player.audio.paused) {
          this.player.play();
        } else {
          this.player.pause();
        }
      } else {
        this.stopPodcast();
        this.playPodcast(el);
      }
    } else {
      this.playPodcast(el);
    }
  };

  playPodcastListener = () => {
    // listen for clicks on the document traverse up and filter for a[data-mp3]
    document.addEventListener("click", (event) => {
      let target = event.target;
      while (target && target !== document) {
        if (target.tagName === "A" && target.hasAttribute("data-mp3")) {
          event.preventDefault();
          this.determinePodcastState(target);
          break;
        }
        target = target.parentNode;
      }
    });
  };

  closePodcastListener = () => {
    this.podcastCloseBtn.addEventListener(
      "click",
      () => {
        this.stopPodcast();
      },
      false
    );
  };
}
