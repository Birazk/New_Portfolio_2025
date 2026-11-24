// Live-app launcher: builds the Fusion-style shell and runs the Streamlit app in the browser with stlite (Pyodide).
import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@1.12.3/build/stlite.js";

const b = document.body.dataset;              // data-title, data-project, data-repo
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

document.body.insertAdjacentHTML("afterbegin", `
<header class="app-head">
  <a class="logo" href="../../index.html" title="Biraj Kharel · Home">BK</a>
  <nav class="crumbs">
    <a class="hide-s" href="../../projects.html">Components</a><span class="hide-s">/</span>
    <a href="${esc(b.project)}">${esc(b.title)}</a><span>/</span><b>Live app</b>
  </nav>
  <span class="live">Running in your browser</span>
  <span class="sp"></span>
  <a class="btn" href="${esc(b.project)}"><i class="ti ti-file-description"></i><span>Project details</span></a>
  <a class="btn" href="${esc(b.repo)}" target="_blank" rel="noopener"><i class="ti ti-brand-github"></i><span>Source code</span></a>
</header>
<div id="loader">
  <div class="ld-card">
    <div class="ld-title"><i class="ti ti-player-play"></i> Starting simulation</div>
    <div class="ld-body">
      <h1>${esc(b.title)}</h1>
      <p>This is the real Python / Streamlit app, running entirely in your browser. No server and no sign-up needed.</p>
      <div class="ld-bar"><span id="ld-bar"></span></div>
      <ul class="ld-steps" id="ld-steps">
        <li>Loading the Python runtime (Pyodide)</li>
        <li>Installing packages</li>
        <li>Mounting app source files</li>
        <li>Starting Streamlit</li>
      </ul>
      <div class="ld-note">The first visit takes about 20–60 s while Python downloads; later visits are faster (cached).</div>
      <div class="ld-err" id="ld-err"></div>
    </div>
  </div>
</div>
<div id="root"></div>`);

const steps = [...document.querySelectorAll("#ld-steps li")];
const bar = document.getElementById("ld-bar");
const setStep = i => {
  steps.forEach((li, k) => li.className = k < i ? "ok" : k === i ? "on" : "");
  bar.style.width = Math.min(95, 8 + i * 25) + "%";
};
const fail = msg => { const e = document.getElementById("ld-err"); e.textContent = msg; e.classList.add("show"); };

async function start() {
  setStep(0);
  const cfg = await fetch("app.json", { cache: "no-cache" }).then(r => r.json());
  steps[1].textContent = "Installing packages: " + cfg.requirements.join(", ");
  const files = {};
  for (const [vfs, url] of Object.entries(cfg.files)) files[vfs] = { url: encodeURI(url) + "?v=" + (cfg.version || "1") };

  mount({
    entrypoint: cfg.entrypoint,
    requirements: cfg.requirements,
    files,
    streamlitConfig: {
      "theme.base": "light",
      "theme.primaryColor": "#0696d7",
      "client.toolbarMode": "viewer",
      "client.showErrorDetails": true,
    },
  }, document.getElementById("root"));

  // advance the progress list on a rough clock, finish when Streamlit has drawn content
  const t0 = Date.now();
  const timer = setInterval(() => {
    const s = (Date.now() - t0) / 1000;
    const root = document.getElementById("root");
    const drawn = root.querySelector(['stHeading', 'stMarkdown', 'stException', 'stAlert', 'stPlotlyChart']
      .map(t => `[data-testid="stMain"] [data-testid="${t}"]`).join(","));
    if (drawn) {
      setStep(4); bar.style.width = "100%";
      document.getElementById("loader").classList.add("done");
      clearInterval(timer);
      return;
    }
    if (root.innerText.includes("Error during booting up")) {   // stlite shows its own error toast
      document.getElementById("loader").classList.add("done");
      clearInterval(timer);
      return;
    }
    setStep(s < 6 ? 0 : s < 20 ? 1 : s < 26 ? 2 : 3);
    if (s > 150) { fail("This is taking longer than usual. Check your connection, or refresh the page."); clearInterval(timer); }
  }, 500);
}

start().catch(err => fail("Could not start the app: " + err.message));
