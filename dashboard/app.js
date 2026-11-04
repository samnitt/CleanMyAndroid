// OnePlus 10R Battery Command Center Application Logic

const wakelockData = [
  {
    id: 1,
    name: "Google Play Store (PhoneskyJobServiceBackground)",
    pkg: "com.android.vending",
    duration: "1h 28m 34s",
    count: "22 events",
    type: "system",
    severity: "critical",
    desc: "Background package updater scheduler looping while staging post-update caches."
  },
  {
    id: 2,
    name: "ReVanced YouTube (AudioMix)",
    pkg: "app.rvx.android.youtube",
    duration: "13m 23s",
    count: "Continuous",
    type: "apps",
    severity: "warning",
    desc: "Active background audio decoding service holding audio suspend blocker."
  },
  {
    id: 3,
    name: "SystemUI Always-On Display (AODDisplayUtil)",
    pkg: "com.android.systemui",
    duration: "8m 11s",
    count: "233 wakeups",
    type: "system",
    severity: "warning",
    desc: "AMOLED panel controller repeatedly waking up the CPU to draw clock & notification icons."
  },
  {
    id: 4,
    name: "WhatsApp Background Sync (SystemJobService)",
    pkg: "com.whatsapp",
    duration: "7m 20s",
    count: "76 events",
    type: "apps",
    severity: "normal",
    desc: "Periodic push notifications and background message queue verification."
  },
  {
    id: 5,
    name: "Microsoft Outlook (SystemJobService)",
    pkg: "com.microsoft.office.outlook",
    duration: "3m 24s",
    count: "27 events",
    type: "apps",
    severity: "normal",
    desc: "Exchange ActiveSync mail synchronization background check."
  },
  {
    id: 6,
    name: "WhatsApp Database Backup (backupdb)",
    pkg: "com.whatsapp",
    duration: "3m 04s",
    count: "21 events",
    type: "apps",
    severity: "normal",
    desc: "Local SQLite database encryption and auto-backup routine."
  },
  {
    id: 7,
    name: "Android System (deviceidle_maint)",
    pkg: "android (UID 1000)",
    duration: "2m 14s",
    count: "24 events",
    type: "system",
    severity: "normal",
    desc: "Native Doze maintenance window briefly unblocking alarms."
  }
];

function renderWakeLocks(filter = "all") {
  const container = document.getElementById("wakelockList");
  container.innerHTML = "";

  const filtered = wakelockData.filter(item => {
    if (filter === "all") return true;
    return item.type === filter;
  });

  filtered.forEach(wl => {
    const itemEl = document.createElement("div");
    itemEl.className = "wakelock-item";

    const tagClass = wl.severity === "critical" ? "tag-critical" : (wl.severity === "warning" ? "tag-warning" : "tag-normal");

    itemEl.innerHTML = `
      <div class="wl-top">
        <div class="wl-name-group">
          <span class="wl-tag-pill ${tagClass}">${wl.severity.toUpperCase()}</span>
          <span class="wl-title">${wl.name}</span>
        </div>
        <span class="wl-duration">${wl.duration}</span>
      </div>
      <div class="wl-subtext">
        <span>${wl.pkg}</span> · <span>${wl.count}</span> — ${wl.desc}
      </div>
    `;

    container.appendChild(itemEl);
  });
}

// Tab Switching
function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetId = `tab-${btn.dataset.tab}`;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

// Filter pills
function setupFilters() {
  const pills = document.querySelectorAll(".pill");
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      renderWakeLocks(pill.dataset.filter);
    });
  });
}

// Clipboard Copy
window.copyCode = function(elementId) {
  const text = document.getElementById(elementId).innerText;
  navigator.clipboard.writeText(text).then(() => {
    const btn = event.target;
    const orig = btn.innerText;
    btn.innerText = "Copied!";
    btn.style.background = "#00e676";
    btn.style.color = "#000";
    setTimeout(() => {
      btn.innerText = orig;
      btn.style.background = "";
      btn.style.color = "";
    }, 1800);
  });
};

document.addEventListener("DOMContentLoaded", () => {
  renderWakeLocks("all");
  setupTabs();
  setupFilters();

  document.getElementById("btnRefreshDiagnostics").addEventListener("click", () => {
    const btn = document.getElementById("btnRefreshDiagnostics");
    btn.innerHTML = `<span class="status-dot"></span> Syncing...`;
    setTimeout(() => {
      btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Synced (Live)`;
      setTimeout(() => {
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Sync Data`;
      }, 2000);
    }, 800);
  });
});
