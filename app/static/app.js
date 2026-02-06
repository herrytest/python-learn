let token = localStorage.getItem("token") || "";
let selectedId = null;
let dragSrcId = null;

const authStatus = document.getElementById("authStatus");
const gallery = document.getElementById("gallery");
const ocrOutput = document.getElementById("ocrOutput");

function headers() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function auth(endpoint) {
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const payload = endpoint.includes("register")
    ? { username, email, password }
    : { username, password };

  const response = await fetch(`/api/auth/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    authStatus.innerText = data.detail || "Auth failed";
    return;
  }
  token = data.access_token;
  localStorage.setItem("token", token);
  authStatus.innerText = "Authenticated";
  loadImages();
}

async function uploadImage() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  await fetch("/api/images", {
    method: "POST",
    headers: headers(),
    body: formData,
  });
  loadImages();
}

function renderImages(images) {
  gallery.innerHTML = "";
  images.forEach((img) => {
    const li = document.createElement("li");
    li.className = `card ${selectedId === img.id ? "selected" : ""}`;
    li.draggable = true;
    li.dataset.id = img.id;
    li.innerHTML = `
      <img src="/uploads/${img.filename}" alt="${img.original_name}" />
      <small>${img.original_name}</small>
      <button data-delete="${img.id}">Delete</button>
    `;

    li.addEventListener("click", () => {
      selectedId = img.id;
      ocrOutput.innerText = img.ocr_text || "No OCR text yet";
      loadImages();
    });

    li.addEventListener("dragstart", () => {
      dragSrcId = img.id;
    });

    li.addEventListener("dragover", (event) => event.preventDefault());
    li.addEventListener("drop", async () => {
      if (!dragSrcId || dragSrcId === img.id) return;
      await reorder(dragSrcId, img.id, images);
    });

    const delBtn = li.querySelector("button");
    delBtn.addEventListener("click", async (event) => {
      event.stopPropagation();
      await fetch(`/api/images/${img.id}`, { method: "DELETE", headers: headers() });
      loadImages();
    });

    gallery.appendChild(li);
  });
}

async function reorder(sourceId, targetId, images) {
  const ids = images.map((i) => i.id);
  const sourceIndex = ids.indexOf(sourceId);
  const targetIndex = ids.indexOf(targetId);
  ids.splice(sourceIndex, 1);
  ids.splice(targetIndex, 0, sourceId);

  await fetch("/api/images/reorder", {
    method: "PUT",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ image_ids: ids }),
  });
  loadImages();
}

async function loadImages() {
  if (!token) return;
  const response = await fetch("/api/images", { headers: headers() });
  if (!response.ok) return;
  const images = await response.json();
  renderImages(images);
}

async function runOcr() {
  if (!selectedId) {
    ocrOutput.innerText = "Select an image first";
    return;
  }
  const response = await fetch(`/api/images/${selectedId}/ocr`, {
    method: "POST",
    headers: headers(),
  });
  const data = await response.json();
  if (response.ok) {
    ocrOutput.innerText = data.ocr_text || "No text found";
  } else {
    ocrOutput.innerText = data.detail || "OCR failed";
  }
}

document.getElementById("registerBtn").addEventListener("click", () => auth("register"));
document.getElementById("loginBtn").addEventListener("click", () => auth("login"));
document.getElementById("uploadBtn").addEventListener("click", uploadImage);
document.getElementById("ocrBtn").addEventListener("click", runOcr);

loadImages();
