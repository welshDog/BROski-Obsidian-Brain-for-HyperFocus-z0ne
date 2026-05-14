const ACTIVE_SESSION_KEY = "hyper_brain_active_session_id";

function $(id) {
  return document.getElementById(id);
}

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    const err = new Error("Request failed");
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function setConnection(online, version) {
  const pill = $("connectionPill");
  pill.classList.toggle("pill--online", online);
  pill.classList.toggle("pill--offline", !online);
  pill.textContent = online ? `ONLINE v${version || "?"}` : "OFFLINE";
}

function renderTiles(services) {
  const root = $("tiles");
  root.innerHTML = "";
  const entries = Object.entries(services || {});
  for (const [name, ok] of entries) {
    const el = document.createElement("div");
    el.className = `tile ${ok ? "tile--on" : "tile--off"}`;
    el.innerHTML = `<div class="tile__name">${name}</div><div class="tile__state">${ok ? "online" : "offline"}</div>`;
    root.appendChild(el);
  }
}

function renderEvents(events) {
  const root = $("events");
  root.innerHTML = "";
  for (const e of events || []) {
    const el = document.createElement("div");
    el.className = "event";
    el.innerHTML = `
      <div class="event__top">
        <div class="event__type">${e.type || "event"}</div>
        <div class="event__ts">${e.ts || ""}</div>
      </div>
      <div class="event__summary">${e.summary || ""}</div>
    `;
    root.appendChild(el);
  }
}

function renderAchievements(summary) {
  const root = $("achievements");
  root.innerHTML = "";

  const streak = summary?.streaks?.current_streak || 0;
  const sessions7d = summary?.sessions_7d || 0;

  const badges = [
    { name: "First Focus", on: sessions7d >= 1, state: sessions7d >= 1 ? "unlocked" : "locked" },
    { name: "3 Sessions / 7d", on: sessions7d >= 3, state: sessions7d >= 3 ? "unlocked" : "locked" },
    { name: "7 Sessions / 7d", on: sessions7d >= 7, state: sessions7d >= 7 ? "unlocked" : "locked" },
    { name: "Streak 3", on: streak >= 3, state: streak >= 3 ? "unlocked" : "locked" },
    { name: "Streak 7", on: streak >= 7, state: streak >= 7 ? "unlocked" : "locked" },
    { name: "Recovery Token", on: (summary?.streaks?.recovery_tokens || 0) > 0, state: "available" },
  ];

  while (badges.length < 12) badges.push({ name: `Badge ${badges.length + 1}`, on: false, state: "locked" });

  for (const b of badges.slice(0, 12)) {
    const el = document.createElement("div");
    el.className = `badge ${b.on ? "badge--on" : "badge--off"}`;
    el.innerHTML = `<div class="badge__name">${b.name}</div><div class="badge__state">${b.state}</div>`;
    root.appendChild(el);
  }
}

function setHud(health, summary) {
  $("hudLevel").textContent = health?.level ?? "—";
  $("hudXp").textContent = summary?.xp_total_7d ?? "—";
  $("hudCoins").textContent = summary?.coins_total_7d ?? "—";
  $("hudStreak").textContent = summary?.streaks?.current_streak ?? "—";
}

function setActiveSessionId(id) {
  if (id) localStorage.setItem(ACTIVE_SESSION_KEY, id);
  else localStorage.removeItem(ACTIVE_SESSION_KEY);
  $("sessionIdInput").value = localStorage.getItem(ACTIVE_SESSION_KEY) || "";
}

async function refreshAll() {
  try {
    const [health, focus, events, game] = await Promise.all([
      fetchJson("/health"),
      fetchJson("/focus/status"),
      fetchJson("/events?limit=10"),
      fetchJson("/gamification/summary"),
    ]);

    setConnection(true, health.version);
    renderTiles(health.services);
    setHud(health, game);
    renderAchievements(game);
    renderEvents(events.events);

    const store = { health, focus, game };
    window.__jsonStore = store;

    const activeTab = document.querySelector(".tab.is-active")?.dataset?.json || "health";
    if (activeTab === "health") $("jsonPanel").textContent = pretty(health);
    if (activeTab === "focus") $("jsonPanel").textContent = pretty(focus);
    if (activeTab === "game") $("jsonPanel").textContent = pretty(game);
  } catch (e) {
    setConnection(false);
    $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
  }
}

function setJsonTab(tab) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("is-active", b.dataset.json === tab));
  const store = window.__jsonStore || {};
  if (tab === "health") $("jsonPanel").textContent = pretty(store.health || {});
  if (tab === "focus") $("jsonPanel").textContent = pretty(store.focus || {});
  if (tab === "game") $("jsonPanel").textContent = pretty(store.game || {});
}

function wire() {
  document.querySelectorAll(".tab").forEach((b) => {
    b.addEventListener("click", () => setJsonTab(b.dataset.json));
  });
  setJsonTab("health");

  $("btnBriefing").addEventListener("click", async () => {
    try {
      const data = await fetchJson("/briefing/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("btnSnapshot").addEventListener("click", async () => {
    try {
      const data = await fetchJson("/focus/snapshot", { method: "POST" });
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("startForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.currentTarget);
    const tags = String(fd.get("tags") || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const payload = {
      intent: String(fd.get("intent") || ""),
      estimated_minutes: Number(fd.get("estimated_minutes") || 25),
      project: String(fd.get("project") || "") || null,
      tags,
      difficulty_preference: String(fd.get("difficulty_preference") || "auto"),
    };

    try {
      const data = await fetchJson("/focus/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const id = data?.session?.id;
      if (id) setActiveSessionId(id);
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("endForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.currentTarget);
    const payload = {
      session_id: String(fd.get("session_id") || ""),
      actual_minutes: Number(fd.get("actual_minutes") || 0),
      mood: Number(fd.get("mood") || 5),
      notes: String(fd.get("notes") || ""),
    };

    try {
      const data = await fetchJson("/focus/end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setActiveSessionId(null);
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("btnClearSession").addEventListener("click", () => setActiveSessionId(null));

  setActiveSessionId(localStorage.getItem(ACTIVE_SESSION_KEY));
}

wire();
refreshAll();
setInterval(refreshAll, 5000);
