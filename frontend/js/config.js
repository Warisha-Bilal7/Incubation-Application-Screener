// The backend serves this folder, so the API is on the SAME origin: leave API_BASE empty.
// Only if the frontend is hosted somewhere else (VS Code Live Server on :5500, Hostinger, Netlify),
// set it to the backend URL, e.g. "http://localhost:8000" or "https://shortlist-api.onrender.com".
window.SHORTLIST = {
  API_BASE: "",
  APP_NAME: "Shortlist",
};
