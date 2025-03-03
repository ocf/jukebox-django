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
    // Reload the webpage to reconnect
    setTimeout(() => location.reload());
  };

  socket.onmessage = (event) => {
    try {
        const response = JSON.parse(event.data);
        console.log("Received packet:", response);
    } catch(error) {
        console.error("Error parsing message:", error)
    }
  }
});
