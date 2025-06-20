async function refreshDashboard() {
            const logsRes = await fetch("/jobs/logs");
            const statusRes = await fetch("/jobs/status");
            const retryRes = await fetch("/jobs/retry-queue");

            const logs = await logsRes.json();
            const statuses = await statusRes.json();
            const retry = await retryRes.json();

            const logsEl = document.getElementById("logs");
            const statusEl = document.getElementById("status");

            const jobsRes = await fetch("/jobs");              // ✅ full job configs
            const jobs = await jobsRes.json();
            renderJobTiles(jobs);                              // ✅ contains job_id, job_name, active, etc.

            if (logsEl) logsEl.innerText = logs.logs.join("\n");
            if (statusEl) statusEl.innerText = JSON.stringify(statuses, null, 2);

            const retryBody = document.getElementById("retry-body");
            retryBody.innerHTML = "";

            if (retry.retry_queue.length === 0) {
                retryBody.innerHTML = "<tr><td colspan='3' class='py-2 px-4 text-center text-gray-500'>No retry tasks.</td></tr>";
            } else {
                retry.retry_queue.forEach(entry => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${entry.description || entry.task?.description || "No description"}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${entry.timestamp}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">
                            <button onclick="retryTask('${entry.id}')" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">Retry</button>
                        </td>
                    `;
                    retryBody.appendChild(row);
                });
            }

            loadExportLogs();
        }

        // ⬇️ Renders the job tiles with toggle buttons
        function renderJobTiles(jobs) {
        const container = document.getElementById("jobTiles");
        container.innerHTML = "";
        for (const job of jobs) {
            const tile = document.createElement("div");
            tile.className = "tile w-full max-w-md bg-white rounded shadow p-4 m-2";

            tile.innerHTML = `
            <h3 class="text-lg font-bold mb-1">${job.job_name}</h3>
            <p><strong>ID:</strong> ${job.job_id}</p>
            <p><strong>Interval:</strong> ${job.run_interval_seconds}s</p>
            <p><strong>Status:</strong> ${job.active ? "🟢 Active" : "⏸️ Paused"}</p>
            <button onclick="toggleJobState('${job.job_id}', this)" class="mt-2 px-4 py-1 rounded text-white ${job.active ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}">
                ${job.active ? 'Pause' : 'Resume'}
            </button>
            `;

            container.appendChild(tile);
        }
        }

        // ✅ FINAL version to keep — handles UI + error + login
        async function toggleJobState(jobId, btnElement) {
            try {
                const res = await fetch(`/jobs/${jobId}/toggle`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include" // ✅ important for session-based auth
                });

                const data = await res.json();

                if (data.active !== undefined) {
                    btnElement.textContent = data.active ? "Pause" : "Resume";
                    btnElement.className = `mt-2 px-4 py-1 rounded text-white ${
                        data.active ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"
                    }`;

                    const statusLine = btnElement.parentElement.querySelector("p:nth-of-type(3)");
                    statusLine.innerHTML = `<strong>Status:</strong> ${data.active ? "🟢 Active" : "⏸️ Paused"}`;
                }
            } catch (err) {
                console.error("Failed to toggle job state:", err);
                alert("Something went wrong while toggling the job.");
            }
        }

        async function populateGhostSelector() {
            const dropdown = document.getElementById("ghostSelector");

            try {
                const res = await fetch("/jobs");
                const data = await res.json();

                const selected = localStorage.getItem("selectedGhost") || "all";

                // Dropdown
                if (dropdown) {
                    dropdown.innerHTML = "";
                    const allOpt = document.createElement("option");
                    allOpt.value = "all";
                    allOpt.text = "All Ghosts";
                    dropdown.appendChild(allOpt);

                    data.forEach(job => {
                        const option = document.createElement("option");
                        option.value = job.job_name;
                        option.text = job.job_name;
                        dropdown.appendChild(option);
                    });

                    dropdown.value = selected;

                    dropdown.addEventListener("change", () => {
                        localStorage.setItem("selectedGhost", dropdown.value);
                        location.reload();
                    });
                }

                // Tiles
                if (tileContainer) {
                    tileContainer.innerHTML = "";

                    const ghosts = [
                        { name: "All Ghosts", value: "all" },
                        ...data.map(job => ({ name: job.job_name, value: job.job_name }))
                    ];

                    ghosts.forEach(g => {
                        const tile = document.createElement("button");
                        tile.textContent = `👻 ${g.name}`;
                        tile.className = `py-2 px-4 rounded font-semibold text-white shadow 
                            ${selected === g.value ? "bg-blue-600" : "bg-gray-700"}
                            hover:bg-blue-500`;

                        tile.onclick = () => {
                            localStorage.setItem("selectedGhost", g.value);
                            location.reload();
                        };

                        tileContainer.appendChild(tile);
                    });
                }

            } catch (e) {
                console.error("❌ Failed to populate ghost selector:", e);
            }
        }

        async function loadJobStats() {
            const res = await fetch("/dashboard/job-stats");
            const stats = await res.json();
            const container = document.getElementById("jobStats");
            container.innerHTML = "";

            const selectedGhost = localStorage.getItem("selectedGhost");

            for (const [job, data] of Object.entries(stats)) {
                // 🧠 Apply filter early in loop
                if (selectedGhost && selectedGhost !== "all" && job !== selectedGhost) continue;

                container.innerHTML += `
                    <div style="border:1px solid #ccc;padding:1rem;margin-bottom:1rem;border-radius:8px;background:#f9f9f9;">
                        <strong>🛠️ ${job}</strong><br/>
                        <b>Last run:</b> ${new Date(data.last_run).toLocaleString()}<br/>
                        <b>Total tasks:</b> ${data.total_tasks}<br/>
                        <b>Runs:</b> ${data.runs}<br/>
                        <b>Exports:</b> ${data.export_count}<br/>
                        <b>Failed Exports:</b> ${data.failed_exports}
                    </div>
                `;
            }
        }

        async function loadActivityLog() {
            const res = await fetch("/logs/activity");
            const logs = await res.json();
            const container = document.getElementById("activityLog");
            container.innerHTML = logs.map(entry =>
                `[${entry.timestamp}] (${entry.trigger}) ${entry.job_name} — ${entry.status}`
                + (entry.file ? ` [${entry.file}]` : "")
            ).join("<br>");
        }

        async function retryExport(entryId) {
            try {
                const res = await fetch(`/dashboard/retry-export/${entryId}`, { method: "POST" });
                const data = await res.json();
                alert(data.message || "Retry triggered.");
                loadExportLogs();  // Refresh table
            } catch (err) {
                console.error("Retry export failed", err);
                alert("❌ Retry failed.");
            }
        }

        async function retryTask(taskId) {
            try {
                const res = await fetch(`/dashboard/retry-task/${taskId}`, { method: "POST" });
                const data = await res.json();
                console.log("Retry response:", data); // 🔍 Log full response for debugging

                if (!data.message) throw new Error("Missing response message");
                alert(data.message);

                refreshDashboard();
            } catch (err) {
                console.error("Retry failed", err);
                alert("❌ Retry failed.");
            }
        }

        async function runJob(jobName) {
            await fetch(`/jobs/run/` + jobName, { method: "POST" });
            loadJobs();
            loadLogs();
        }

        // ⏯️ Toggle Job (Grey Tile Style)
        async function toggleJob(jobId) {
            try {
                const res = await fetch(`/toggle/${jobId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                });

                if (!res.ok) throw new Error("Failed to toggle");

                const data = await res.json();
                showToast(`Job ${data.job_id} is now ${data.paused ? 'paused' : 'resumed'}`, 'success');

                // 👇 Immediately update tile UI
                const tiles = document.querySelectorAll("#jobTiles > div");
                tiles.forEach(tile => {
                    if (tile.innerHTML.includes(`ID:</strong> ${data.job_id}`)) {
                        tile.classList.toggle("opacity-50", data.paused);
                        tile.classList.toggle("grayscale", data.paused);
                        tile.classList.toggle("cursor-not-allowed", data.paused);
                    }
                });

                await loadJobs();  // Ensure full sync
            } catch (err) {
                showToast(`Failed to toggle job ${jobId}`, 'error');
                console.error(err);
            }
        }

        async function loadJobs() {
            const jobsRes = await fetch("/jobs");
            const statusRes = await fetch("/jobs/status");
            const exportsRes = await fetch("/dashboard/exports");

            const jobs = await jobsRes.json();
            const statuses = await statusRes.json();
            const exports = (await exportsRes.json()).exports;

            const container = document.getElementById("jobTiles");
            container.innerHTML = "";

            jobs.forEach(job => {
                const tile = document.createElement("div");
                tile.className = "border border-gray-300 p-4 m-2 rounded shadow bg-white w-full max-w-xl";

                const lastRun = statuses[job.job_name] || "never";

                // Filter recent exports for this job
                const recentExports = exports
                    .filter(e => e.job_name === job.job_name)
                    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                    .slice(0, 5);

                const historyHTML = recentExports.map(e => {
                    const date = new Date(e.timestamp).toLocaleString();
                    const result = e.success ? "✅" : "❌";
                    return `<div class="text-sm text-gray-700 ml-2">• ${date} — ${result} ${e.destination}</div>`;
                }).join("");

                tile.innerHTML = `
                    <div class="flex justify-between items-center mb-2">
                        <div>
                            <strong class="text-gray-800">${job.job_name}</strong><br/>
                            <span class="text-sm text-gray-500">Last run: ${lastRun}</span>
                        </div>
                        <div>
                            <button onclick="runJob('${job.job_name}')" class="mr-2 bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700">Run</button>
                            <button onclick="toggleJob('${job.job_id}')" class="bg-${job.active ? 'yellow' : 'blue'}-600 text-white px-3 py-1 rounded hover:bg-${job.active ? 'yellow' : 'blue'}-700">
                                ${job.active ? 'Pause' : 'Resume'}
                            </button>
                        </div>
                    </div>
                    <details class="mt-2">
                        <summary class="cursor-pointer text-sm text-blue-700 hover:underline">Show Last 5 Runs</summary>
                        ${historyHTML || '<div class="ml-2 text-sm text-gray-400">No recent runs.</div>'}
                    </details>
                `;

                container.appendChild(tile);
            });
        }

        async function loadLogs() {
            const res = await fetch("/jobs/logs");
            const data = await res.json();
            const logBox = document.getElementById("logBox");
            if (logBox) logBox.innerText = data.logs.join("\n");
        }

        async function loadLatestDemoExport() {
            try {
                const res = await fetch("/dashboard/latest-demo-export");
                const data = await res.json();
                if (data.status) return;

                document.getElementById("job-id").innerText = data.job_id;
                document.getElementById("timestamp").innerText = data.timestamp;
                document.getElementById("task-count").innerText = data.task_count;
                document.getElementById("success-count").innerText = data.success_count;
                document.getElementById("failure-count").innerText = data.failure_count;
                document.getElementById("pdf-download").href = data.pdf_download_url;
            } catch (err) {
                console.error("Failed to load latest demo export:", err);
            }
        }

        async function loadLatestComplianceExport() {
            const tile = document.getElementById("latest-compliance-export");
            if (!tile) return;

            try {
                const response = await fetch("/dashboard/latest-compliance-export");
                const data = await response.json();

                if (data.status === "no_exports") {
                    tile.innerHTML = "<p class='text-sm'>No exports yet.</p>";
                    return;
                }

                if (data.status === "incomplete") {
                    tile.innerHTML = "<p class='text-sm text-red-500'>Export incomplete or corrupted.</p>";
                    return;
                }

                tile.innerHTML = `
                    <p class="text-xs mb-1 text-gray-400">${data.timestamp}</p>
                    <p class="font-semibold text-sm">${data.job_name}</p>
                    <p class="text-xs text-gray-300 mt-1">Tasks: ${data.tasks.length}</p>
                    <p class="text-xs text-gray-300 mt-1 truncate">Summary: ${data.summary}</p>
                `;
            } catch (e) {
                tile.innerHTML = `<p class="text-sm text-red-500">❌ Failed to load export.</p>`;
            }
        }

        async function loadEmailActivity() {
            try {
                const res = await fetch("/dashboard/email-activity");
                const data = await res.json();

                const container = document.getElementById("emailActivityLog");
                if (!data.email_activity || data.email_activity.length === 0) {
                    container.innerHTML = "<i>No recent email-triggered activity.</i>";
                    return;
                }

                container.innerHTML = data.email_activity.map(entry =>
                    `[${new Date(entry.timestamp).toLocaleString()}] ` +
                    `(${entry.status}) ${entry.job_name} — ${entry.file}`
                ).join("<br>");
            } catch (err) {
                console.error("Failed to load email activity:", err);
                document.getElementById("emailActivityLog").innerText = "❌ Failed to load.";
            }
        }

        async function loadEmailTriggeredJobs() {
            try {
                const res = await fetch('/dashboard/email-jobs');
                const jobs = await res.json();

                const tbody = document.getElementById("email-jobs-list");
                tbody.innerHTML = '';

                const selectedGhost = localStorage.getItem("selectedGhost");

                const filteredJobs = jobs.filter(job => {
                    return !selectedGhost || selectedGhost === "all" || job.job_name === selectedGhost;
                });

                if (filteredJobs.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" class="text-center text-gray-500 py-3">No recent email-triggered jobs.</td></tr>`;
                    return;
                }

                filteredJobs.forEach(job => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${new Date(job.timestamp).toLocaleString()}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${job.sender}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${job.subject}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${job.status}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (err) {
                console.error("Failed to load email jobs:", err);
            }
        }

        async function loadRetryStats() {
            try {
                const selectedGhost = localStorage.getItem("selectedGhost") || "all";
                const res = await fetch("/dashboard/retry-stats");
                const data = await res.json();

                const container = document.getElementById("retryStatsBox");
                if (!container) return;

                if (selectedGhost === "all") {
                    const total = Object.values(data).reduce((sum, job) => sum + (job.total_tasks || 0), 0);
                    const latest = Object.values(data)
                        .map(job => job.last_retry_attempt)
                        .filter(Boolean)
                        .sort()
                        .pop();

                    if (total === 0) {
                        container.innerHTML = `<div class="text-gray-500">No retry stats for all.</div>`;
                    } else {
                        container.innerHTML = `
                            <b>Total retry tasks:</b> ${total}<br/>
                            <b>Latest retry:</b> ${latest || "n/a"}
                        `;
                    }
                    return;
                }

                const stats = data[selectedGhost];
                if (!stats) {
                    container.innerHTML = `<div class="text-gray-500">No retry stats for ${selectedGhost}.</div>`;
                    return;
                }

                container.innerHTML = `
                    <b>Total retry tasks:</b> ${stats.total_tasks}<br/>
                    <b>Last retry attempt:</b> ${stats.last_retry_attempt}
                `;
            } catch (err) {
                console.error("Failed to load retry stats:", err);
                document.getElementById("retryStatsBox").innerText = "❌ Failed to load retry stats.";
            }
        }

        async function fetchEmailActivity() {
            const res = await fetch("/dashboard/email-jobs");
            const data = await res.json();

            const list = document.getElementById("email-activity-list");
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = "<li class='text-gray-400'>No recent email jobs</li>";
                return;
            }

            data.forEach(entry => {
                const item = document.createElement("li");
                item.textContent = `${entry.timestamp} — ${entry.subject}`;
                list.appendChild(item);
            });
        }

        async function loadFailureAlerts() {
            try {
                const res = await fetch("/dashboard/exports");
                const data = await res.json();
                const container = document.getElementById("failure-alerts-box");
                container.innerHTML = "";

                const now = new Date();
                const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

                const failedRecent = data.exports.filter(e =>
                    !e.success && new Date(e.timestamp) >= oneDayAgo
                );

                const failCounts = {};
                failedRecent.forEach(e => {
                    const job = e.job_name || "Unknown Job";
                    failCounts[job] = (failCounts[job] || 0) + 1;
                });

                const flaggedJobs = Object.entries(failCounts)
                    .filter(([_, count]) => count >= 3)
                    .sort((a, b) => b[1] - a[1]);

                if (flaggedJobs.length === 0) {
                    container.innerHTML = `<div class="text-green-700">✅ No jobs with 3+ failures in the past 24 hours.</div>`;
                    return;
                }

                flaggedJobs.forEach(([job, count]) => {
                    container.innerHTML += `
                        <div class="flex justify-between items-center bg-red-100 p-2 rounded mb-1 border border-red-300">
                            <span><strong>${job}</strong></span>
                            <span class="font-bold text-red-700">${count} failures</span>
                        </div>
                    `;
                });
            } catch (err) {
                console.error("Failed to load failure alerts", err);
                document.getElementById("failure-alerts-box").innerHTML =
                    `<div class="text-red-600">❌ Error loading failure alerts.</div>`;
            }
        }

        async function loadExportLogs() {
            try {
                const res = await fetch('/dashboard/exports');
                const data = await res.json();
                const tableBody = document.querySelector('#export-log-table tbody');
                const jobFilter = document.getElementById("exportFilterJob").value;
                const onlyFailed = document.getElementById("exportFilterFailed").checked;

                tableBody.innerHTML = '';

                if (!data.exports || data.exports.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-gray-500 py-4">No exports found.</td></tr>`;
                    return;
                }

                const filtered = data.exports.filter(entry => {
                    const matchJob = !jobFilter || entry.job_name === jobFilter;
                    const matchFailure = !onlyFailed || !entry.success;
                    return matchJob && matchFailure;
                });

                if (filtered.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-gray-500 py-4">No matching exports.</td></tr>`;
                    return;
                }

                filtered.forEach(entry => {
                    const timestamp = new Date(entry.timestamp).toLocaleString();
                    const status = entry.success ? '✅' : '❌';
                    const retryCount = entry.retry_count ?? 0;
                    const retryOrigin = entry.retry_origin ?? '-';
                    const details = JSON.stringify(entry.details, null, 2);
                    const senderRaw = entry.sender || entry.details?.sender || "-";
                    const subjectRaw = entry.subject || entry.details?.subject || "-";
                    const sender = senderRaw.slice(0, 80);
                    const subject = subjectRaw.slice(0, 80);

                    let retryBtn = '';
                    if (!entry.success) {
                        const disabled = entry.retry_count >= 3;
                        retryBtn = `
                            <button onclick="retryExport('${entry.id}')"
                                    class="mt-2 ${disabled ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'} text-white px-3 py-1 rounded"
                                    ${disabled ? 'disabled title="Retry limit reached"' : ''}>
                                Retry Export
                            </button>
                        `;
                    }

                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${timestamp}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${entry.job_name}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${entry.destination}</td>
                        <td class="py-2 px-4 border-b text-sm text-center">${status}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${retryCount}</td>
                        <td class="py-2 px-4 border-b text-sm text-gray-700">${retryOrigin}</td>
                        <td class="py-2 px-4 border-b text-sm">
                            <div class="mb-1" title="${senderRaw}"><strong>Sender:</strong> ${sender}</div>
                            <div class="mb-1" title="${subjectRaw}"><strong>Subject:</strong> ${subject}</div>
                            <pre class="whitespace-pre-wrap text-gray-600">${details}</pre>
                            ${retryBtn}
                        </td>
                    `;
                    tableBody.appendChild(row);
                });

                // 🧠 Populate dropdown with unique jobs
                const jobs = [...new Set(data.exports.map(e => e.job_name))];
                const dropdown = document.getElementById("exportFilterJob");
                dropdown.innerHTML = '<option value="">All Jobs</option>';
                jobs.forEach(job => {
                    const opt = document.createElement("option");
                    opt.value = job;
                    opt.textContent = job;
                    dropdown.appendChild(opt);
                });
            } catch (error) {
                console.error("❌ Failed to load export logs:", error);
            }
        }

        async function loadRecentEmailJobs() {
            try {
                const res = await fetch('/dashboard/exports');
                const data = await res.json();
                const container = document.getElementById("recent-email-jobs");
                container.innerHTML = "";

                const emailExports = data.exports
                    .filter(e => e.destination === "email")
                    .slice(-10)  // show last 10
                    .reverse();

                if (emailExports.length === 0) {
                    container.innerHTML = `<div class="text-gray-500">No recent email jobs found.</div>`;
                    return;
                }

                emailExports.forEach(entry => {
                    const timestamp = new Date(entry.timestamp).toLocaleString();
                    const sender = (entry.sender || entry.details?.sender || "-").slice(0, 80);
                    const subject = (entry.subject || entry.details?.subject || "-").slice(0, 80);
                    const success = entry.success ? "✅" : "❌";

                    const item = document.createElement("div");
                    item.className = "border p-2 rounded bg-gray-50 text-sm shadow-sm";
                    item.innerHTML = `
                        <div><strong>${success}</strong> <span class="text-gray-700">${timestamp}</span></div>
                        <div><strong>From:</strong> <span title="${entry.sender}">${sender}</span></div>
                        <div><strong>Subject:</strong> <span title="${entry.subject}">${subject}</span></div>
                    `;
                    container.appendChild(item);
                });
            } catch (error) {
                console.error("❌ Failed to load recent email jobs:", error);
                document.getElementById("recent-email-jobs").innerHTML = `<div class="text-red-600">Error loading email jobs.</div>`;
            }
        }

        async function populateSummaryFilter() {
            try {
                const res = await fetch("/dashboard/exports");
                const data = await res.json();
                const jobFilter = document.getElementById("summaryJobFilter");
                const jobs = [...new Set(data.exports.map(e => e.job_name))];

                jobFilter.innerHTML = `<option value="">All Jobs</option>`;
                jobs.forEach(job => {
                    const opt = document.createElement("option");
                    opt.value = job;
                    opt.textContent = job;
                    jobFilter.appendChild(opt);
                });

                jobFilter.addEventListener("change", loadExportSummaries);
            } catch (err) {
                console.error("Failed to populate summary filter", err);
            }
        }

        async function loadExportVolume() {
            try {
                const res = await fetch("/dashboard/exports");
                const data = await res.json();
                const container = document.getElementById("export-volume-box");
                container.innerHTML = "";

                const now = new Date();
                const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

                const recent = data.exports.filter(e => new Date(e.timestamp) >= sevenDaysAgo);

                const selectedGhost = localStorage.getItem("selectedGhost");
                const counts = {};

                recent.forEach(e => {
                    const job = e.job_name || "unknown";

                    // 👻 Skip if ghost is selected and doesn't match
                    if (selectedGhost && selectedGhost !== "all" && job !== selectedGhost) return;

                    const type = e.destination || "unknown";
                    counts[type] = (counts[type] || 0) + 1;
                });

                if (Object.keys(counts).length === 0) {
                    container.innerHTML = `<div class="text-gray-500">No exports in the last 7 days.</div>`;
                    return;
                }

                Object.entries(counts).forEach(([type, count]) => {
                    const bar = `<div class="h-2 bg-blue-500 rounded" style="width:${Math.min(100, count * 10)}%"></div>`;
                    container.innerHTML += `
                        <div class="flex justify-between items-center">
                            <span>${type}</span>
                            <span class="ml-auto font-semibold">${count}</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded mb-2">${bar}</div>
                    `;
                });
            } catch (err) {
                console.error("Failed to load export volume", err);
                document.getElementById("export-volume-box").innerHTML =
                    `<div class="text-red-600">Error loading volume data.</div>`;
            }
        }

        async function loadExportSummaries() {
            try {
                const res = await fetch("/dashboard/exports");
                const data = await res.json();
                const container = document.getElementById("export-summaries-list");
                container.innerHTML = "";

                let exportsWithSummary = data.exports.filter(e =>
                    e.summary || (e.details && typeof e.details.summary === "string")
                );

                // Sort by timestamp descending
                exportsWithSummary.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

                // 🌐 Dropdown filter (manual)
                const selectedJob = document.getElementById("summaryJobFilter")?.value;
                if (selectedJob) {
                    exportsWithSummary = exportsWithSummary.filter(e => e.job_name === selectedJob);
                }

                // 👻 Apply selectedGhost filter
                const selectedGhost = localStorage.getItem("selectedGhost");
                if (selectedGhost && selectedGhost !== "all") {
                    exportsWithSummary = exportsWithSummary.filter(e => e.job_name === selectedGhost);
                }

                // Limit to latest 5
                exportsWithSummary = exportsWithSummary.slice(0, 5);

                if (exportsWithSummary.length === 0) {
                    container.innerHTML = `<div class="text-gray-500">No export summaries available.</div>`;
                    return;
                }

                exportsWithSummary.forEach(entry => {
                    const timestamp = new Date(entry.timestamp).toLocaleString();
                    const summaryText = entry.summary || entry.details?.summary || "-";
                    const shortSummary = summaryText.length > 160
                        ? summaryText.slice(0, 160) + "…"
                        : summaryText;
                    const job = entry.job_name;
                    const destination = entry.destination || "-";
                    const badgeColor = {
                        file: 'bg-blue-100 text-blue-800',
                        log: 'bg-green-100 text-green-800',
                        email: 'bg-yellow-100 text-yellow-800'
                    }[destination] || 'bg-gray-100 text-gray-800';

                    const item = document.createElement("div");
                    item.className = "border p-3 rounded bg-gray-50 shadow-sm";

                    item.innerHTML = `
                        <div class="flex justify-between items-center mb-1">
                            <div>
                                <strong>${job}</strong>
                                <span class="text-gray-600 text-xs ml-2">(${timestamp})</span>
                            </div>
                            <span class="text-xs px-2 py-1 rounded-full ${badgeColor}">${destination}</span>
                        </div>
                        <div class="summary-text text-gray-700 cursor-pointer">${shortSummary}</div>
                    `;

                    item.querySelector(".summary-text").addEventListener("click", function () {
                        this.innerText = this.innerText.endsWith("…") ? summaryText : shortSummary;
                    });

                    container.appendChild(item);
                });
            } catch (err) {
                console.error("❌ Failed to load export summaries:", err);
                document.getElementById("export-summaries-list").innerHTML =
                    `<div class="text-red-600">Failed to load export summaries.</div>`;
            }
        }

        async function loadLatestTasks() {
            try {
                const res = await fetch('/dashboard/latest-tasks');
                const tasks = await res.json();

                const container = document.getElementById('latest-tasks');
                container.innerHTML = "";

                if (tasks.length === 0) {
                    container.innerHTML = "<div class='text-gray-500'>No recent tasks.</div>";
                    return;
                }

                const selectedGhost = localStorage.getItem("selectedGhost");

                for (const t of tasks) {
                    if (selectedGhost && selectedGhost !== "all" && t.job_name !== selectedGhost) continue;

                    const time = new Date(t.timestamp).toLocaleTimeString();
                    const statusColour = t.status === "success" ? "text-green-600" : "text-red-600";
                    const line = `
                        <div class="mb-1">
                            <span class="font-medium">${t.job_name}</span>:
                            <span>${t.task}</span>
                            <span class="${statusColour} ml-2">[${t.status}]</span>
                            <span class="text-gray-400 ml-2">${time}</span>
                        </div>
                    `;
                    container.insertAdjacentHTML('beforeend', line);
                }
            } catch (e) {
                document.getElementById('latest-tasks').innerHTML = "<div class='text-red-600'>Error loading tasks</div>";
            }
        }

        async function loadDurationStats() {
            try {
                const res = await fetch("/api/dashboard/job-durations");
                const data = await res.json();
                const container = document.getElementById("duration-stats");
                container.innerHTML = "";

                const entries = Object.entries(data);
                if (entries.length === 0) {
                container.innerHTML = "<li class='text-gray-500'>No data yet.</li>";
                } else {
                for (const [job, seconds] of entries) {
                    const li = document.createElement("li");
                    li.textContent = `${job}: ${seconds}s avg`;
                    container.appendChild(li);
                }
                }
            } catch (e) {
                console.error("Failed to load job durations", e);
            }
        }

        async function loadDurationStats() {
            try {
                const res = await fetch("/api/dashboard/job-durations");
                const data = await res.json();

                const tile = document.getElementById("durationTile");
                tile.innerHTML = "";

                const jobs = Object.entries(data)
                    .sort((a, b) => b[1] - a[1])  // Sort by duration descending

                if (jobs.length === 0) {
                    tile.innerHTML = "<p>No data yet.</p>";
                    return;
                }

                for (const [job, duration] of jobs) {
                    tile.innerHTML += `<p><strong>${job}:</strong> ${duration}s</p>`;
                }
            } catch (e) {
                console.error("Failed to load durations:", e);
                document.getElementById("durationTile").innerHTML = "<p>Error loading data.</p>";
            }
        }

        async function loadLatestDemoExport() {
            try {
                const res = await fetch("/dashboard/latest-demo-export");
                const data = await res.json();
                const tile = document.getElementById("latestDemoExportTile");

                if (data.status === "no exports yet" || data.status === "no metadata") {
                    tile.innerHTML = "<p>No exports available.</p>";
                    return;
                }

                tile.innerHTML = `
                    <p><strong>Folder:</strong> ${data.folder}</p>
                    <p><strong>Job:</strong> ${data.job_id}</p>
                    <p><strong>Timestamp:</strong> ${data.timestamp}</p>
                    <p><strong>Tasks:</strong> ${data.task_count} (${data.success_count}✅ / ${data.failure_count}❌)</p>
                    <a href="${data.pdf_download_url}" class="inline-block mt-2 bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                        Download PDF
                    </a>
                `;
            } catch (e) {
                console.error("Failed to load latest demo export:", e);
                document.getElementById("latestDemoExportTile").innerHTML = "<p>Error loading export.</p>";
            }
        }

        function loadRecentFailures() {
            fetch("/dashboard/recent-failures")
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById("failure-list");
                    list.innerHTML = "";

                    if (!data.failures || data.failures.length === 0) {
                        list.innerHTML = "<li class='text-gray-400'>✅ No recent failures</li>";
                        return;
                    }

                    const selectedGhost = localStorage.getItem("selectedGhost");

                    data.failures.forEach(f => {
                        if (selectedGhost && selectedGhost !== "all" && f.job !== selectedGhost) return;

                        const li = document.createElement("li");
                        li.innerHTML = `
                            <span class="font-semibold">${f.job}</span> →
                            <span class="text-red-600">${f.type}</span> to 
                            <span class="italic">${f.destination}</span> 
                            <span class="text-xs text-gray-400">(${new Date(f.timestamp).toLocaleString()})</span>
                        `;
                        list.appendChild(li);
                    });
                })
                .catch(err => {
                    console.error("Failed to load recent failures:", err);
                });
        }

        function startRefreshLoop(interval = 10000) {
            async function loop() {
                try {
                    await refreshDashboard();
                } catch (err) {
                    console.error("❌ refreshDashboard failed:", err);
                }
                setTimeout(loop, interval);
            }
            loop();
        }

        function showToast(message, type = 'success') {
            const toast = document.getElementById("toast");
            toast.textContent = message;
            toast.className = `fixed bottom-5 right-5 px-4 py-2 rounded shadow-lg z-50 transition-opacity duration-300 ${
                type === 'error' ? 'bg-red-600 text-white' : 'bg-green-600 text-white'
            }`;
            toast.classList.remove("hidden");
            setTimeout(() => {
                toast.classList.add("hidden");
            }, 3000);
        }
       
        window.onload = function () {
            // Initial one-time loads
            populateGhostSelector();
            refreshDashboard();
            loadRetryStats();
            loadJobs();
            loadLogs();
            loadFailureAlerts();
            loadRecentFailures();
            loadJobStats();
            loadActivityLog();
            loadLatestDemoExport(); 
            loadLatestComplianceExport();
            loadEmailActivity();
            loadEmailTriggeredJobs();
            loadRecentEmailJobs();
            populateSummaryFilter();
            loadExportSummaries();
            loadExportVolume();
            loadLatestTasks();
            loadDurationStats();

            // 👇 Ghost filter logic
            const savedGhost = localStorage.getItem("selectedGhost") || "all";
            const ghostSelector = document.getElementById("ghostSelector");
            if (ghostSelector) {
                ghostSelector.value = savedGhost;

                ghostSelector.addEventListener("change", function () {
                    const selected = this.value;
                    localStorage.setItem("selectedGhost", selected);
                    refreshDashboard();  // Re-apply filter
                });
            }

            // Periodic updates
            startRefreshLoop(10000);                      // Refresh general dashboard stats every 10s
            setInterval(loadEmailTriggeredJobs, 30000);   // Email job history every 30s
            setInterval(loadEmailActivity, 10000);        // Email activity tile every 10s
            setInterval(loadLatestTasks, 15000);          // Latest task tile every 15s
            setInterval(loadRecentFailures, 20000);       // Refresh every 20s
            setInterval(loadDurationStats, 20000);        // Duration stats refresh
        };

        // 🆕 Handle Create Job Form Submission
        document.addEventListener("DOMContentLoaded", () => {
        const jobForm = document.getElementById("jobForm");
        const message = document.getElementById("jobFormMessage");

        if (jobForm) {
            jobForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            message.innerText = "Submitting...";

            const formData = new FormData(jobForm);
            const payload = Object.fromEntries(formData.entries());
            payload.run_interval_seconds = parseInt(payload.run_interval_seconds);

            try {
                const res = await fetch("/dashboard/create-job", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
                });

                const data = await res.json();
                if (res.ok) {
                message.innerText = "✅ Job created successfully.";
                jobForm.reset();
                loadJobs();
                } else {
                message.innerText = `❌ ${data.error || "Job creation failed."}`;
                }
            } catch (err) {
                console.error("Job creation failed:", err);
                message.innerText = "❌ Error submitting form.";
            }
            });
        }
        });

        document.addEventListener("DOMContentLoaded", () => {
            const jobSelect = document.getElementById("exportFilterJob");
            const failedCheckbox = document.getElementById("exportFilterFailed");

            if (jobSelect && failedCheckbox) {
                jobSelect.addEventListener("change", loadExportLogs);
                failedCheckbox.addEventListener("change", loadExportLogs);
            }
        });