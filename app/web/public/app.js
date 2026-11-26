"use strict";

const list = document.getElementById("tasks");
const form = document.getElementById("new-task");
const input = document.getElementById("title");
const statusEl = document.getElementById("status");

async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${options.method || "GET"} ${path} failed: ${res.status}`);
  return res.status === 204 ? null : res.json();
}

function render(tasks) {
  list.replaceChildren(
    ...tasks.map((t) => {
      const li = document.createElement("li");
      const box = document.createElement("input");
      box.type = "checkbox";
      box.checked = t.done;
      box.setAttribute("aria-label", `Mark "${t.title}" as done`);
      box.addEventListener("change", () => run(() => api(`/tasks/${t.id}`, { method: "PATCH", body: JSON.stringify({ done: box.checked }) })));
      const span = document.createElement("span");
      span.textContent = t.title; // textContent, never innerHTML: no XSS from task titles
      if (t.done) span.className = "done";
      const del = document.createElement("button");
      del.textContent = "Delete";
      del.className = "link";
      del.addEventListener("click", () => run(() => api(`/tasks/${t.id}`, { method: "DELETE" })));
      li.append(box, span, del);
      return li;
    }),
  );
}

async function refresh() {
  render(await api("/tasks"));
  const health = await api("/health");
  statusEl.textContent = `API ${health.version}, database ${health.database}`;
}

async function run(action) {
  try {
    await action();
    await refresh();
  } catch (err) {
    statusEl.textContent = err.message;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const title = input.value.trim();
  if (!title) return;
  run(async () => {
    await api("/tasks", { method: "POST", body: JSON.stringify({ title }) });
    input.value = "";
  });
});

run(async () => {});
