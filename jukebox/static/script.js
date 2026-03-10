class Jukebox {
  constructor() {
    this.initElements();
    this.initSocket();
    this.bindEvents();
  }

  initElements() {
    this.elements = {
      urlInput: document.querySelector("#url-input"),
      urlButton: document.querySelector("#url-button"),
      pauseButton: document.querySelector("#pause-button"),
      playButton: document.querySelector("#play-button"),
      nextButton: document.querySelector("#next-button"),
      volumeSlider: document.querySelector("#volume-slider"),
      songTitle: document.querySelector("#song-title"),
      songAuthor: document.querySelector("#song-author"),
      songThumbnail: document.querySelector("#song-thumbnail"),
      defaultThumbnail: document.querySelector("#default-thumbnail"),
      startTime: document.querySelector("#start-time"),
      endTime: document.querySelector("#end-time"),
      lyricsContainer: document.querySelector("#lyrics-container"),
      queue: document.querySelector("#queue"),
      seekSlider: document.querySelector("#seek-slider"),
      loopButton: document.querySelector("#loop-button"),
    };
    this.elements.playButton.style.display = "none";
    this.isSeeking = false;
    this.isAdjustingVolume = false;
    this.isDragging = false;
    this.isLooping = false;
    this.draggedIndex = null;
  }

  initSocket() {
    const wsProtocol = location.protocol === "https:" ? "wss:" : "ws:";
    this.socket = new WebSocket(`${wsProtocol}//${location.host}/ws/`);

    this.handlers = {
      now_playing: (p) => this.onNowPlaying(p),
      songs: (p) => this.onSongs(p),
      play_pause: (p) => this.onPlayPause(p),
      volume: (p) => this.onVolume(p),
      time: (p) => this.onTime(p),
      lyrics: (p) => this.onLyrics(p),
      loop: (p) => this.onLoop(p),
    };

    this.socket.onmessage = (e) => this.handleMessage(e);
    this.socket.onerror = (e) => console.error("WebSocket error:", e);
    this.socket.onclose = () => console.warn("WebSocket closed");
  }

  bindEvents() {
    const {
      urlButton,
      urlInput,
      pauseButton,
      playButton,
      nextButton,
      volumeSlider,
      seekSlider,
      loopButton,
    } = this.elements;

    urlButton.addEventListener("click", (e) => {
      e.preventDefault();
      const url = urlInput.value.trim();
      if (url) {
        this.send("play", { url });
        urlInput.value = "";
      }
    });

    pauseButton.addEventListener("click", () => this.send("pause"));
    playButton.addEventListener("click", () => this.send("pause"));
    nextButton.addEventListener("click", () => this.send("next"));

    loopButton.addEventListener("click", () => {
      this.send("loop", { looping: !this.isLooping });
    });

    volumeSlider.addEventListener("input", () => {
      this.isAdjustingVolume = true;
    });

    volumeSlider.addEventListener("change", () => {
      this.send("volume", { volume: volumeSlider.value / 100 });
      this.isAdjustingVolume = false;
    });

    seekSlider.addEventListener("input", () => {
      this.isSeeking = true;
    });

    seekSlider.addEventListener("change", () => {
      this.send("time", { new_pos: seekSlider.value / 1000 });
      this.isSeeking = false;
    });

    this.elements.queue.addEventListener("click", (e) => {
      const button = e.target.closest(".delete-button");
      if (!button) {
        return;
      }
      const songId = button.getAttribute("data-id");
      if (!songId) {
        return;
      }
      this.send("delete", { id: songId });
    });

    this.elements.queue.addEventListener("mousedown", (e) => {
      // Only handle should be draggable
      const queueItem = e.target.closest(".queue-item");
      if (queueItem && queueItem.dataset.index !== "0") {
        const handle = e.target.closest(".drag-handle");
        queueItem.draggable = !!handle;
      }
    });

    this.elements.queue.addEventListener("dragstart", (e) => {
      const queueItem = e.target.closest(".queue-item");
      if (!queueItem || !queueItem.draggable) {
        e.preventDefault();
        return;
      }
      this.draggedIndex = parseInt(queueItem.dataset.index);
      this.isDragging = true;
    });

    this.elements.queue.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    this.elements.queue.addEventListener("drop", (e) => {
      e.preventDefault();
      const dropTarget = e.target.closest(".queue-item");
      if (!dropTarget) {
        return;
      }
      const newIndex = parseInt(dropTarget.dataset.index);
      if (newIndex > 0 && newIndex !== this.draggedIndex) {
        this.send("reorder", {
          old_index: this.draggedIndex,
          new_index: newIndex,
        });
      }
      this.isDragging = false;
    });

    this.elements.queue.addEventListener("dragend", () => {
      this.isDragging = false;
    });
  }

  send(type, payload = {}) {
    console.log("Sending message:", { type, payload });
    this.socket.send(JSON.stringify({ type, payload }));
  }

  handleMessage(event) {
    try {
      const { type, payload } = JSON.parse(event.data);
      this.handlers[type]?.(payload);
    } catch (e) {
      console.error("Error parsing message:", e);
    }
  }

  onNowPlaying({ title, author, thumbnail }) {
    const { songTitle, songAuthor, songThumbnail, defaultThumbnail } =
      this.elements;
    songTitle.textContent = title;
    songAuthor.textContent = author;

    if (thumbnail) {
      songThumbnail.src = thumbnail;
      songThumbnail.style.display = "block";
      defaultThumbnail.style.display = "none";
    } else {
      songThumbnail.style.display = "none";
      defaultThumbnail.style.display = "block";
    }
  }

  onSongs({ songs }) {
    if (this.isDragging) {
      return;
    }
    this.elements.queue.innerHTML = songs
      .map(
        (song, index) => `
        <div class="queue-item" data-index="${index}" ${index > 0 ? 'draggable="false"' : ""}>
          <img src="${song.thumbnail}" alt="Thumbnail" />
          <div class="queue-info">
            <div>${song.title}</div>
            <div>${song.author}</div>
          </div>
          ${
            index > 0
              ? `
            <div class="queue-actions">
              <button class="delete-button" data-id="${song.id}"><i class="fa-solid fa-trash"></i></button>
              <div class="drag-handle"><i class="fa-solid fa-grip-lines"></i></div>
            </div>`
              : ""
          }
        </div>`,
      )
      .join("");
  }

  onPlayPause({ status }) {
    const { playButton, pauseButton } = this.elements;
    if (status === "play") {
      playButton.style.display = "none";
      pauseButton.style.display = "block";
    } else {
      pauseButton.style.display = "none";
      playButton.style.display = "block";
    }
  }

  onVolume({ volume }) {
    if (!this.isAdjustingVolume) {
      this.elements.volumeSlider.value = volume * 100;
    }
  }

  onLoop({ looping }) {
    this.isLooping = looping;
    this.elements.loopButton.style.color = looping ? "var(--text)" : "var(--text-muted)";
  }

  onTime({ duration, curr_pos }) {
    const { startTime, endTime, seekSlider } = this.elements;
    startTime.textContent = this.formatTime(curr_pos);
    endTime.textContent = this.formatTime(duration);

    if (!this.isSeeking && duration > 0) {
      seekSlider.value = (curr_pos / duration) * 1000;
    }
  }

  onLyrics({ lyrics, index }) {
    const container = this.elements.lyricsContainer;
    container.innerHTML = lyrics
      .map((line, i) =>
        i === index
          ? `<div id="active-lyric">${line}</div>`
          : `<div>${line}</div>`,
      )
      .join("");

    const active = document.querySelector("#active-lyric");
    if (active) active.scrollIntoView({ block: "center", behavior: "smooth" });
  }

  formatTime(seconds) {
    const date = new Date(0);
    date.setSeconds(seconds || 0);
    return date.toISOString().substring(14, 19);
  }
}

document.addEventListener("DOMContentLoaded", () => new Jukebox());
