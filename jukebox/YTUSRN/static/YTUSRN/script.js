document.addEventListener("DOMContentLoaded", () => {
  const socket = new WebSocket("ws://localhost:42069");

  function sendPacket(type, payload = {}) {
    const packet = JSON.stringify({ type, payload });
    console.log("Sending packet:", packet);
    socket.send(packet);
  }

  const urlInput = document.querySelector("#url-input");
  const urlButton = document.querySelector("#url-button");

  const pauseButton = document.querySelector("#pause-button");
  const playButton = document.querySelector("#play-button");
  playButton.style.display = "none";
  const nextButton = document.querySelector("#next-button");
  const volumeSlider = document.querySelector("#volume-slider");

  const songTitle = document.querySelector("#song-title");
  const songAuthor = document.querySelector("#song-author");
  const songThumbnail = document.querySelector("#song-thumbnail");
  const defaultThumbnail = document.querySelector("#default-thumbnail");
  const startTime = document.querySelector("#start-time");
  const endTime = document.querySelector("#end-time");
  const timelineSlider = document.querySelector("#timeline-slider");

  const lyricsContainer = document.querySelector("#lyrics-container");

  const queue = document.querySelector("#queue");

  urlButton.addEventListener("click", (e) => {
    e.preventDefault();
    const urlValue = urlInput.value.trim();
    if (urlValue) {
      sendPacket("play", { url: urlValue });
      urlInput.value = "";
    }
  });

  pauseButton.addEventListener("click", () => {
    sendPacket("pause");
  });

  playButton.addEventListener("click", () => {
    sendPacket("pause");
  });

  nextButton.addEventListener("click", () => {
    sendPacket("next");
  });

  volumeSlider.addEventListener("change", () => {
    const volume = volumeSlider.value / 100;
    sendPacket("volume", { volume: volume });
  });

  timelineSlider.addEventListener("change", () => {
    const newPos = timelineSlider.value / 100;
    sendPacket("time", { new_pos: newPos });
  });

  socket.onerror = (error) => {
    console.error("Socket errror:", error);
  };

  socket.onclose = () => {
    console.warn("WebSocket closed, attempting to reconnect...");
  };

  socket.onmessage = (event) => {
    try {
      const response = JSON.parse(event.data);
      console.log("Received packet:", response);

      if (response.type === "now_playing") {
        const title = response.payload.title;
        const author = response.payload.author;
        const thumbnail = response.payload.thumbnail;

        songTitle.innerHTML = title;
        songAuthor.innerHTML = author;
        if (thumbnail === "") {
          defaultThumbnail.style.display = "block";
          songThumbnail.style.display = "none";
        } else {
          songThumbnail.src = thumbnail;
          defaultThumbnail.style.display = "none";
          songThumbnail.style.display = "block";
        }
      } else if (response.type === "songs") {
        const songs = response.payload.songs;
        queue.innerHTML = songs
          .map((song) => {
            return `<div class="outlined queue-song-container">
                    <img id="queue-thumbnail" src=${song.thumbnail} alt="Queue Thumbnail" />
                    <div class="queue-song-info-container">
                        <div>${song.title}</div>
                        <div>${song.author}</div>
                    </div>
                </div>`;
          })
          .join("");
      } else if (response.type === "play_pause") {
        const status = response.payload.status;
        if (status == "play") {
          playButton.style.display = "none";
          pauseButton.style.display = "block";
        } else {
          pauseButton.style.display = "none";
          playButton.style.display = "block";
        }
      } else if (response.type === "volume") {
        const volume = response.payload.volume;
        volumeSlider.value = volume * 100;
      } else if (response.type === "time") {
        const duration = response.payload.duration;
        const currPos = response.payload.curr_pos;

        console.log(duration, currPos);

        var start = new Date(0);
        start.setSeconds(currPos);
        startTime.innerHTML = start.toISOString().substring(14, 19);

        var end = new Date(0);
        end.setSeconds(duration);
        endTime.innerHTML = end.toISOString().substring(14, 19);

        timelineSlider.value = (currPos * 100) / duration;
      } else if (response.type === "lyrics") {
        const index = response.payload.index;
        const lyrics = response.payload.lyrics;

        lyricsContainer.innerHTML = lyrics
          .map((lyric, i) => {
            if (i === index) {
              return `<div id="active-lyric">${lyric}</div>`;
            } else {
              return `<div>${lyric}</div>`;
            }
          })
          .join("");

        document.querySelector("#active-lyric").scrollIntoView();
      }
    } catch (error) {
      console.error("Error parsing message:", error);
    }
  };
});
