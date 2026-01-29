async function createPaste() {
  const content = document.getElementById("content").value;
  const ttl = document.getElementById("ttl").value;
  const maxViews = document.getElementById("maxViews").value;
  const resultDiv = document.getElementById("result");

  if (!content.trim()) {
    resultDiv.innerHTML = "<p style='color:red'>Paste content cannot be empty.</p>";
    resultDiv.hidden = false;
    return;
  }

  try {
    const response = await fetch("/api/api_services/pastes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        content: content,
        ttl: ttl || null,
        max_views: maxViews || null
      })
    });

    if (!response.ok) {
      throw new Error("Failed to create paste");
    }

    const data = await response.json();

    const pasteUrl = data.url || `/paste/${data.id}`;

    resultDiv.innerHTML = `
      <p><strong>Paste created successfully!</strong></p>
      <a href="${pasteUrl}" target="_blank">${pasteUrl}</a>
    `;
    resultDiv.hidden = false;

  } catch (err) {
    resultDiv.innerHTML = `<p style="color:red">${err.message}</p>`;
    resultDiv.hidden = false;
  }
}
