// Tiny API client. Every backend call goes through here. See API-CONTRACT.md for the shapes.
(function () {
  const base = () => (window.SHORTLIST && window.SHORTLIST.API_BASE) || "";
  const KEY = "shortlist_reviewer_key";

  const getKey = () => { try { return sessionStorage.getItem(KEY) || ""; } catch (e) { return ""; } };
  const setKey = (k) => { try { sessionStorage.setItem(KEY, k); } catch (e) {} };

  // Reviewer auth: a Supabase access token (window.SHORTLIST_TOKEN) wins, else the shared reviewer key.
  function authHeaders(extra) {
    const h = Object.assign({}, extra);
    if (window.SHORTLIST_TOKEN) h["Authorization"] = "Bearer " + window.SHORTLIST_TOKEN;
    else if (getKey()) h["X-Reviewer-Key"] = getKey();
    return h;
  }

  async function raw(method, path, opts) {
    opts = opts || {};
    const res = await fetch(base() + path, { method, headers: authHeaders(opts.headers), body: opts.body });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const j = await res.json();
        detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
      } catch (e) {}
      const err = new Error(detail);
      err.status = res.status;
      throw err;
    }
    return res;
  }

  async function request(method, path, opts) {
    const res = await raw(method, path, opts);
    const type = res.headers.get("content-type") || "";
    return type.includes("application/json") ? res.json() : res.text();
  }

  const jsonBody = (obj) => ({ headers: { "Content-Type": "application/json" }, body: JSON.stringify(obj) });

  // Fetch a protected file with auth headers and open/download it (plain <a href> cannot send headers).
  async function openBlob(path, filename, download) {
    const res = await raw("GET", path);
    const url = URL.createObjectURL(await res.blob());
    if (download) {
      const a = document.createElement("a");
      a.href = url; a.download = filename; a.click();
    } else {
      window.open(url, "_blank");
    }
  }

  window.api = {
    getKey, setKey,
    health: () => request("GET", "/api/health"),
    rubric: () => request("GET", "/api/rubric"),
    // payload = object with the form fields; file = optional File (PDF)
    submit: (payload, file) => {
      const fd = new FormData();
      fd.append("payload", JSON.stringify(payload));
      if (file) fd.append("deck", file);
      return request("POST", "/api/applications", { body: fd });
    },
    list: (params) => request("GET", "/api/applications?" + new URLSearchParams(params || {})),
    get: (id, blind) => request("GET", "/api/applications/" + encodeURIComponent(id) + "?blind=" + !!blind),
    reanalyze: (id) => request("POST", "/api/applications/" + encodeURIComponent(id) + "/analyze"),
    decide: (id, body) => request("PUT", "/api/applications/" + encodeURIComponent(id) + "/decision", jsonBody(body)),
    stats: () => request("GET", "/api/stats"),
    seed: (reset) => request("POST", "/api/dev/seed?reset=" + !!reset),
    openDeck: (id) => openBlob("/api/applications/" + encodeURIComponent(id) + "/deck", id + ".pdf", false),
    downloadCsv: (blind) => openBlob("/api/export.csv?blind=" + !!blind, "shortlist-export.csv", true),
  };
})();
