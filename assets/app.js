(() => {
  "use strict";

  const state = { occupations: [], scores: new Map() };
  const search = document.getElementById("search");
  const results = document.getElementById("results");
  const count = document.getElementById("count");
  const scored = document.getElementById("scored");
  const average = document.getElementById("avg");
  const SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

  function isSafeSlug(value) {
    return typeof value === "string" && SLUG_PATTERN.test(value);
  }

  function safeBlsUrl(value) {
    if (typeof value !== "string" || !value) return null;
    try {
      const url = new URL(value);
      return url.protocol === "https:" && url.hostname === "www.bls.gov" ? url.href : null;
    } catch {
      return null;
    }
  }

  function addCell(row, text, link, external = false) {
    const cell = document.createElement("td");
    if (link) {
      const anchor = document.createElement("a");
      anchor.href = link;
      anchor.textContent = text;
      if (external) {
        anchor.target = "_blank";
        anchor.rel = "noopener noreferrer";
      }
      cell.appendChild(anchor);
    } else {
      cell.textContent = text;
    }
    row.appendChild(cell);
  }

  function renderMessage(message) {
    results.replaceChildren();
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = message;
    row.appendChild(cell);
    results.appendChild(row);
  }

  function render() {
    const query = search.value.trim().toLocaleLowerCase();
    const matches = state.occupations
      .filter((item) => {
        const title = typeof item.title === "string" ? item.title : "";
        const category = typeof item.category === "string" ? item.category : "";
        return !query ||
          title.toLocaleLowerCase().includes(query) ||
          category.toLocaleLowerCase().includes(query);
      })
      .slice(0, 200);

    results.replaceChildren();
    if (!matches.length) {
      renderMessage("No matching occupations.");
      return;
    }

    for (const item of matches) {
      const row = document.createElement("tr");
      const title = typeof item.title === "string" ? item.title : "Untitled occupation";
      const slug = isSafeSlug(item.slug) ? item.slug : null;
      const category = typeof item.category === "string"
        ? item.category.replaceAll("-", " ")
        : "Uncategorized";
      const score = state.scores.get(item.slug);
      addCell(row, title, slug ? `${slug}.html` : null);
      addCell(row, category);
      addCell(row, Number.isInteger(score) && score >= 0 && score <= 10 ? `${score}/10` : "—");
      const sourceUrl = safeBlsUrl(item.url);
      addCell(row, sourceUrl ? "BLS" : "—", sourceUrl, true);
      results.appendChild(row);
    }
  }

  async function loadJson(path) {
    const response = await fetch(path, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Unable to load ${path} (HTTP ${response.status}).`);
    return response.json();
  }

  async function init() {
    try {
      const [occupations, scores] = await Promise.all([
        loadJson("occupations.json"),
        loadJson("scores.json")
      ]);
      if (!Array.isArray(occupations) || !Array.isArray(scores)) {
        throw new TypeError("The occupation or score dataset has an invalid format.");
      }

      state.occupations = occupations.filter((item) =>
        item && typeof item === "object" &&
        typeof item.title === "string" &&
        isSafeSlug(item.slug) &&
        typeof item.category === "string"
      );
      state.scores = new Map(scores
        .filter((item) => item && isSafeSlug(item.slug) &&
          Number.isInteger(item.exposure) && item.exposure >= 0 && item.exposure <= 10)
        .map((item) => [item.slug, item.exposure]));

      count.textContent = state.occupations.length.toLocaleString();
      scored.textContent = state.scores.size.toLocaleString();
      const values = [...state.scores.values()];
      average.textContent = values.length
        ? `${(values.reduce((sum, value) => sum + value, 0) / values.length).toFixed(1)}/10`
        : "—";
      render();
    } catch (error) {
      count.textContent = "—";
      scored.textContent = "—";
      average.textContent = "—";
      renderMessage("Could not load the dataset. Serve this repository over HTTP (not file://) and check that occupations.json and scores.json are available.");
      console.error("CareerHub initialization failed:", error);
    }
  }

  search.addEventListener("input", render);
  init();
})();
