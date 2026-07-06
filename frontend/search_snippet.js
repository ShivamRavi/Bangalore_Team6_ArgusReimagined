// JavaScript fetch snippet for the Tailwind sidebar search integration
// Usage: include this script in the sidebar HTML and call loadSearch(term)

async function loadSearch(term) {
  const query = encodeURIComponent(term.trim());
  const response = await fetch(`/api/v1/search?q=${query}`);
  if (!response.ok) {
    console.error('Search request failed', response.status);
    return [];
  }
  const data = await response.json();
  // Render results – adapt to your sidebar markup
  const container = document.getElementById('search-results');
  if (!container) return;
  container.innerHTML = data.results.map(item => `
    <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p class="text-sm font-semibold text-slate-800">${item.title}</p>
      <p class="mt-2 text-sm text-slate-600">${item.description}</p>
      <p class="mt-3 text-xs uppercase tracking-[0.25em] text-cyan-600">${item.type}</p>
    </div>
  `).join('');
}
