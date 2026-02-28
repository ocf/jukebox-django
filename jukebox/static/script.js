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
    };
    this.elements.playButton.style.display = "none";
    this.isSeeking = false;
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
    };

    this.socket.onmessage = (e) => this.handleMessage(e);
    this.socket.onerror = (e) => console.error("WebSocket error:", e);
    this.socket.onclose = () => console.warn("WebSocket closed");
  }

  bindEvents() {
    const { urlButton, urlInput, pauseButton, playButton, nextButton, volumeSlider, seekSlider } = this.elements;

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

    volumeSlider.addEventListener("change", () => {
      this.send("volume", { volume: volumeSlider.value / 100 });
    });

    seekSlider.addEventListener("input", () => {
      this.isSeeking = true;
    });

    seekSlider.addEventListener("change", () => {
      this.send("time", { new_pos: seekSlider.value / 1000 });
      this.isSeeking = false;
    });
  }

  send(type, payload = {}) {
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
    const { songTitle, songAuthor, songThumbnail, defaultThumbnail } = this.elements;
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
    this.elements.queue.innerHTML = songs
      .map(
        (song) => `
        <div class="queue-item">
          <img src="${song.thumbnail}" alt="Thumbnail" />
          <div class="queue-info">
            <div>${song.title}</div>
            <div>${song.author}</div>
          </div>
        </div>`
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
    this.elements.volumeSlider.value = volume * 100;
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
      .map((line, i) => (i === index ? `<div id="active-lyric">${line}</div>` : `<div>${line}</div>`))
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
