document.addEventListener("DOMContentLoaded", () => {
  const locationInput = document.getElementById("eventLocation");
  const statusMsg = document.getElementById("locationStatus");

  const civicKeywords = [
    "park", "reserve", "hall", "community centre", "foreshore",
    "beach", "oval", "plaza", "square", "green", "public space"
  ];

  locationInput.addEventListener("input", () => {
    const value = locationInput.value.toLowerCase();
    const matched = civicKeywords.some(keyword => value.includes(keyword));

    if (value.trim() === "") {
      statusMsg.textContent = "";
      statusMsg.className = "status-msg";
    } else if (matched) {
      statusMsg.textContent = "✅ Location appears to be a civic space.";
      statusMsg.className = "status-msg success";
    } else {
      statusMsg.textContent = "⚠️ Location may not be a recognized civic space.";
      statusMsg.className = "status-msg warning";
    }
  });
});