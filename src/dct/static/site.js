(() => {
  const search = document.querySelector(".company-search");
  const input = document.querySelector("#company-query");
  const rows = [...document.querySelectorAll("#company-list tbody tr")];
  if (search && input && rows.length) {
    const results = document.querySelector("#company-results");
    const noMatch = document.querySelector("#company-no-match");
    const filter = () => {
      const query = input.value.trim().toLocaleLowerCase();
      let count = 0;
      for (const row of rows) {
        row.hidden = !row.dataset.companyNames.toLocaleLowerCase().includes(query);
        if (!row.hidden) count += 1;
      }
      results.textContent = `${count} of ${rows.length} verified companies`;
      noMatch.hidden = count !== 0;
      for (const context of document.querySelectorAll(".stats, .hub-nav")) {
        context.hidden = query.length !== 0;
      }
    };
    input.addEventListener("input", filter);
    filter();
    search.hidden = false;
  }

  const share = document.querySelector("[data-share-page]");
  if (share && (navigator.share || navigator.clipboard?.writeText)) {
    const tools = share.closest(".share-tools");
    const status = tools.querySelector("[data-share-status]");
    tools.hidden = false;
    share.addEventListener("click", async () => {
      const url = document.querySelector('link[rel="canonical"]')?.href || location.href;
      try {
        if (navigator.share) {
          await navigator.share({ title: document.title, url });
          status.textContent = "Shared";
        } else {
          await navigator.clipboard.writeText(url);
          status.textContent = "Link copied";
        }
      } catch (error) {
        status.textContent = error.name === "AbortError" ? "Sharing canceled" : "Couldn't share. Copy the address from your browser.";
      }
    });
  }
})();
