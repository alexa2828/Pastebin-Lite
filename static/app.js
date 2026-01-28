async function createPaste() {
  const content = document.getElementById("content").value;
  const ttl = document.getElementById("ttl").value;
  const maxViews = document.getElementById("maxViews").value;
  const result = document.getElementById("result");

  result.textContent = "Creating...";

  const payload = {
    content: content,
    ttl_seconds: ttl ? Number(ttl) : null,
    max_views: maxViews ? Number(maxViews) : null
  };

  try {
    const res = await fetch("/api/api_services/pastes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      result.textContent = data.error || "Error creating paste";
      return;
    }

    result.innerHTML = `
      <p>Paste created!</p>
      <a href="${data.url}" target="_blank">${data.url}</a>
    `;
  } catch (err) {
    result.textContent = "Network error";
  }
  function closeModal() {
  const modal = document.getElementById("errorModal");
  if (modal) {
    modal.style.display = "none";
    window.history.back(); // optional: go back
  }
}
}
