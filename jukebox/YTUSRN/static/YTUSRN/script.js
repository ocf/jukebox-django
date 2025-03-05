document.addEventListener("DOMContentLoaded", () => {
  const socket = new WebSocket("ws://localhost:42069");

  function sendPacket(type, payload = {}) {
    const packet = JSON.stringify({type, payload});
    console.log("Sending packet:", packet);
    socket.send(packet);
  }

  const urlInput = document.querySelector("#url-input");
  const urlButton = document.querySelector("#url-button");

  const pauseButton = document.querySelector("#pause-button");
  const nextButton = document.querySelector("#next-button");

  const songTitle = document.querySelector("#song-title");
  const songAuthor = document.querySelector("#song-author");
  const songThumbnail = document.querySelector("#song-thumbnail");

  const queue = document.querySelector("#queue");

  urlButton.addEventListener("click", (e) => {
    e.preventDefault();
    const urlValue = urlInput.value.trim();
    if (urlValue) {
      sendPacket("play", {url: urlValue});
      urlInput.value = "";
    }
  });

  pauseButton.addEventListener("click", () => {
    sendPacket("pause");
  });

  nextButton.addEventListener("click", () => {
    sendPacket("next");
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
            songThumbnail.src = thumbnail;
        }

        else if (response.type === "songs") {
            const songs = response.payload.songs
            
            queue.innerHTML = songs.map((song) => {
                return `<div class="outlined queue-song-container">
                    <img id="queue-thumbnail" src=${song.thumbnail} alt="Queue Thumbnail" />
                    <div class="queue-song-info-container">
                        <div>${song.title}</div>
                        <div>${song.author}</div>
                    </div>
                </div>`
            }).join('');
        }

    } catch(error) {
        console.error("Error parsing message:", error)
    }
  }
});
