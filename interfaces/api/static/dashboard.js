// dashboard.js v1.0.0 — Finalised & Bound to dashboard.html

// ==========================
// 📥 Input Tab
// ==========================


// 🤖 Ghost Employee Selector

async function loadGhostEmployeeSelector(jobId = null) {
  try {
    const res = await fetch("/jobs"); // Returns list of registered job IDs
    const jobList = await res.json();

    const selector = document.getElementById("ghost-selector");
    selector.innerHTML = ""; // Clear previous options

    jobList.forEach(jobId => {
      const option = document.createElement("option");
      option.value = jobId;
      option.textContent = jobId.replace(/_/g, " ");
      selector.appendChild(option);
    });

    // Optional: Store selected job in localStorage
    selector.addEventListener("change", () => {
      localStorage.setItem("selectedJob", selector.value);
      refreshDashboardForJob(selector.value);
    });

    // Restore last selected job
    const saved = localStorage.getItem("selectedJob");
    if (saved && jobList.includes(saved)) {
      selector.value = saved;
      refreshDashboardForJob(saved);
    } else {
      selector.value = jobList[0];
      refreshDashboardForJob(jobList[0]);
    }

  } catch (err) {
    console.error("❌ Failed to load ghost employee list", err);
  }
}

function getSelectedJobId() {
  const selector = document.getElementById("ghost-selector");
  return selector?.value || null;
}

async function loadInputLog(jobId = null) {
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

async function loadActiveJobs(jobId = null) {
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

async function loadRetryQueue(jobId = null) {
  try {
    const res = await fetch("/dashboard/retry-queue");
    const data = await res.json();
    const queue = data.retry_queue || [];

    const body = document.getElementById("retry-body");
    body.innerHTML = "";

    queue.forEach(entry => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code>${entry.description || "(no description)"}</code></td>
        <td>${entry.timestamp || "-"}</td>
        <td><button onclick="retryTask('${entry.id}')">Retry</button></td>
      `;
      body.appendChild(row);
    });
  } catch (err) {
    console.warn("⚠️ Retry queue not available:", err.message);
  }
}

async function loadLatestTasks(jobId = null) {
  const res = await fetch("/dashboard/latest-tasks");
  const data = await res.json();
  const container = document.getElementById("latest-tasks-processing");

  if (!container) return;

  container.innerHTML = "";

  if (data.tasks.length === 0) {
    container.innerHTML = "<p class='text-gray-500'>No tasks logged yet.</p>";
    return;
  }

  data.tasks.forEach(task => {
    const color = task.success ? "text-green-600" : "text-red-600";
    const item = `
      <div class="mb-1">
        <span class="${color}">[${task.job_id}]</span>
        <span class="ml-2"><code>${task.description}</code></span>
      </div>`;
    container.innerHTML += item;
  });
}

async function retryTask(id) {
  alert("Retry not implemented in minimal v1.0.0");
}

// ==========================
// 📤 Output Tab
// ==========================

async function loadLatestExport(jobId = null) {
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

// 📁 Recent Export Files

async function loadRecentExportFiles(jobId = null) {
  try {
    const res = await fetch("/dashboard/recent-export-files");
    const data = await res.json();
    const files = data.files || [];

    const container = document.getElementById("recent-export-files");
    container.innerHTML = "";

    if (files.length === 0) {
      container.innerHTML = "<li class='text-gray-500'>No export files found.</li>";
      return;
    }

    files.forEach(file => {
      const li = document.createElement("li");
      li.textContent = `• ${file}`;
      container.appendChild(li);
    });
  } catch (err) {
    console.error("❌ Failed to load recent export files", err);
  }
}

// 📤 Export Logs
async function loadExportLog() {
  const list = document.getElementById("export-log-list");
  list.innerHTML = "<li>Loading...</li>";

  try {
    const res = await fetch("/dashboard/latest-exports");
    const data = await res.json();
    const logs = data.exports;

    if (logs.length === 0) {
      list.innerHTML = "<li>No exports yet.</li>";
      return;
    }

    list.innerHTML = "";
    logs.forEach(log => {
      const li = document.createElement("li");
      const ts = new Date(log.timestamp).toLocaleString();
      li.textContent = `[${ts}] ${log.destination || "Unknown"} — ${log.task_description || "No description"}`;
      list.appendChild(li);
    });
  } catch (err) {
    list.innerHTML = `<li class="text-red-600">⚠️ Failed to load export logs</li>`;
  }
}

// ==========================
// 📊 Insights Tab
// ==========================

async function loadRetryStats(jobId = null) {
  try {
    const res = await fetch("/dashboard/retry-stats");
    const stats = await res.json();

    const box = document.getElementById("retryStatsBox");
    if (!box) return;

    box.innerHTML = `
      <div><strong>Total Retries:</strong> ${stats.total}</div>
      <div><strong>Failed:</strong> ${stats.failed}</div>
      <div class="mt-2"><strong>Recent Entries:</strong></div>
      <ul class="list-disc list-inside text-sm text-gray-700 mt-1">
        ${stats.recent.map(e => `<li><code>${e.description || "(no description)"}</code> — ${e.result_timestamp || "-"}</li>`).join("")}
      </ul>
    `;
  } catch (err) {
    console.error("❌ Failed to load retry stats", err);
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

function refreshDashboardForJob(jobId) {
  console.log("🔁 Switched to ghost employee:", jobId);

  loadInputLog(jobId);
  loadRetryQueue(jobId);
  loadLatestTasks(jobId);
  //loadLatestExport(jobId);
  loadRetryStats(jobId);
  loadRecentExportFiles(jobId);
  loadExportLog();
}


// ==========================
// 🚀 Init Everything
// ==========================

window.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  document.getElementById("tab-input").click();

  await loadGhostEmployeeSelector();
  // await loadActiveJobs(); // Must be loaded first
  const jobId = getSelectedJobId();
  refreshDashboardForJob(jobId); // This now triggers all tile loads
  handleUpload();
});

