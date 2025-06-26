// dashboard.js v1.0.0 — Finalised & Bound to dashboard.html

// ==========================
// 📥 Input Tab
// ==========================

async function loadGhostEmployeeSelector() {
  try {
    const res = await fetch("/dashboard/jobs");
    const data = await res.json();
    const jobs = data.jobs || [];

    const ghostSelect = document.getElementById("ghostSelector");
    const uploadSelect = document.getElementById("uploadJobSelect");

    ghostSelect.innerHTML = "";
    uploadSelect.innerHTML = "";

    jobs.forEach(job => {
      const opt = document.createElement("option");
      opt.value = job.job_id;
      opt.textContent = job.job_name;
      ghostSelect.appendChild(opt);
      uploadSelect.appendChild(opt.cloneNode(true));
    });
  } catch (err) {
    console.error("❌ Failed to load job list", err);
  }
}

async function loadInputLog() {
  try {
    const res = await fetch("/dashboard/input-log");
    const data = await res.json();
    const logs = data.log || [];

    const list = document.getElementById("input-log-list");
    list.innerHTML = "";

    logs.forEach(entry => {
      const li = document.createElement("li");
      li.textContent = `${entry.timestamp} — ${entry.file}`;
      list.appendChild(li);
    });
  } catch (err) {
    console.error("❌ Failed to load input log", err);
  }
}

function handleUpload() {
  const form = document.getElementById("uploadForm");
  const status = document.getElementById("uploadStatus");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    status.textContent = "Uploading...";

    const formData = new FormData(form);
    const jobId = document.getElementById("uploadJobSelect")?.value;
    if (!jobId) {
      status.textContent = "❌ Please select a job.";
      return;
    }

    try {
      const res = await fetch("/dashboard/upload", {
        method: "POST",
        body: formData,
      });

      const result = await res.json();
      if (res.ok) {
        status.textContent = result.message || "✅ Upload complete.";
        form.reset();
        loadInputLog();
        showToast("✅ File uploaded.");
      } else {
        status.textContent = result.error || "❌ Upload failed.";
      }
    } catch (err) {
      status.textContent = "❌ Upload error: " + err.message;
    }
  });
}

// ==========================
// ⚙️ Processing Tab
// ==========================

async function loadActiveJobs() {
  try {
    const res = await fetch("/dashboard/active-jobs");
    const data = await res.json();
    const list = document.getElementById("active-jobs-list");
    list.innerHTML = "";

    Object.entries(data).forEach(([job_id, job]) => {
      const li = document.createElement("li");
      li.textContent = `${job_id} — ${job.status}`;
      list.appendChild(li);
    });
  } catch (err) {
    console.error("❌ Failed to load job status", err);
  }
}

async function loadRetryQueue() {
  try {
    const res = await fetch("/dashboard/retry-queue");
    const data = await res.json();
    const queue = data.retry_queue || [];

    const body = document.getElementById("retry-body");
    body.innerHTML = "";

    queue.forEach(entry => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${entry.description || "(no description)"}</td>
        <td>${entry.timestamp || "-"}</td>
        <td><button onclick="retryTask('${entry.id}')">Retry</button></td>
      `;
      body.appendChild(row);
    });
  } catch (err) {
    console.warn("⚠️ Retry queue not available:", err.message);
  }
}

async function loadLatestTasks() {
  try {
    const res = await fetch("/dashboard/latest-tasks");
    const data = await res.json();
    const tasks = data.tasks || [];

    const container = document.getElementById("latest-tasks");
    container.innerHTML = "";

    tasks.forEach(task => {
      const div = document.createElement("div");
      div.textContent = `• ${task.description}`;
      container.appendChild(div);
    });
  } catch (err) {
    console.error("❌ Failed to load latest tasks", err);
  }
}

async function retryTask(id) {
  alert("Retry not implemented in minimal v1.0.0");
}

// ==========================
// 📤 Output Tab
// ==========================

async function loadLatestExport() {
  try {
    const res = await fetch("/dashboard/latest-compliance-export");
    const data = await res.json();
    const container = document.getElementById("latestDemoExportTile");

    container.innerHTML = `
      <div><strong>Summary:</strong></div>
      <div class="bg-gray-100 p-2 rounded text-sm">${data.summary || "—"}</div>
    `;
  } catch (err) {
    console.warn("⚠️ Failed to load export summary", err.message);
  }
}

// ==========================
// 🧭 Tab Control + Toast
// ==========================

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

function setupTabs() {
  document.querySelectorAll(".tab-button").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("bg-blue-600"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.add("hidden"));

      btn.classList.add("bg-blue-600");
      const target = btn.id.replace("tab-", "content-");
      document.getElementById(target).classList.remove("hidden");
    });
  });
}

// ==========================
// 🚀 Init Everything
// ==========================

window.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  document.getElementById("tab-input").click();

  await loadGhostEmployeeSelector();
  await loadInputLog();
  await loadActiveJobs();
  await loadRetryQueue();
  await loadLatestTasks();
  await loadLatestExport();
  handleUpload();
});
