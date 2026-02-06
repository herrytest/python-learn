const state = {
  token: localStorage.getItem("token") || "",
};

const authStatus = document.getElementById("authStatus");
const uploadStatus = document.getElementById("uploadStatus");
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const gallery = document.getElementById("gallery");

async function register() {
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });

  authStatus.textContent = res.ok ? "Registered successfully" : "Register failed";
}

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const res = await fetch("/api/auth/login", {
    method: "POST",
    body,
  });

  if (!res.ok) {
    authStatus.textContent = "Login failed";
    return;
  }

  const data = await res.json();
  state.token = data.access_token;
  localStorage.setItem("token", state.token);
  authStatus.textContent = "Logged in";
  refreshGallery();
}

async function uploadFiles(files) {
  if (!state.token) {
    uploadStatus.textContent = "Login first";
    return;
  }

  for (const file of files) {
    const form = new FormData();
    form.append("file", file);

    const res = await fetch("/api/images/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${state.token}` },
      body: form,
    });

    uploadStatus.textContent = res.ok ? "Upload complete" : "Upload failed";
  }

  refreshGallery();
}

async function refreshGallery() {
  if (!state.token) {
    gallery.innerHTML = "";
    return;
  }

  const res = await fetch("/api/images/", {
    headers: { Authorization: `Bearer ${state.token}` },
  });

  if (!res.ok) {
    gallery.innerHTML = "<p>Failed to load gallery</p>";
    return;
  }

  const images = await res.json();
  gallery.innerHTML = "";

  images.forEach((img) => {
    const card = document.createElement("div");
    card.className = "item";
    card.innerHTML = `
      <img src="/uploads/${img.file_path.split('/').pop()}" alt="${img.filename}" />
      <div class="meta">
        <div>${img.filename}</div>
        <button data-id="${img.id}">Run OCR</button>
        <p id="ocr-${img.id}">${img.ocr_text || "No OCR yet"}</p>
      </div>
    `;
    card.querySelector("button").addEventListener("click", () => runOCR(img.id));
    gallery.appendChild(card);
  });
}

async function runOCR(id) {
  const res = await fetch(`/api/images/${id}/ocr`, {
    method: "POST",
    headers: { Authorization: `Bearer ${state.token}` },
  });

  if (!res.ok) {
    return;
  }

  const data = await res.json();
  const p = document.getElementById(`ocr-${id}`);
  p.textContent = data.ocr_text || "No text found";
}

document.getElementById("registerBtn").addEventListener("click", register);
document.getElementById("loginBtn").addEventListener("click", login);
document.getElementById("refreshBtn").addEventListener("click", refreshGallery);

dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => uploadFiles(e.target.files));

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

["dragleave", "dragend"].forEach((ev) =>
  dropZone.addEventListener(ev, () => dropZone.classList.remove("dragover"))
);

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  uploadFiles(e.dataTransfer.files);
});

refreshGallery();
