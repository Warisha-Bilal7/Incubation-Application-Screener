// Small shared helpers. RULE: applicant text is untrusted. Never put it into innerHTML without esc().
(function () {
  const esc = (s) =>
    String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const priorityBadge = (p) =>
    p ? `<span class="badge badge-${esc(p)}">${esc(p)} priority</span>` : `<span class="badge badge-none">pending</span>`;

  const statusLabel = { pending: "Queued", analyzing: "Analyzing…", done: "Ready", failed: "Failed" };

  // If the API says 401/403, ask for the reviewer key once and retry.
  async function withAuth(fn) {
    try {
      return await fn();
    } catch (e) {
      if (e.status === 401 || e.status === 403) {
        const k = window.prompt("Reviewer key (ask the team lead):");
        if (k) {
          window.api.setKey(k.trim());
          return fn();
        }
      }
      throw e;
    }
  }

  function showError(el, err) {
    el.textContent = err && err.message ? err.message : String(err);
    el.hidden = false;
  }

  window.ui = { esc, $, $$, priorityBadge, statusLabel, withAuth, showError };
})();
