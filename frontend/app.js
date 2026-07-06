const API_BASE = 'http://127.0.0.1:8000/api/v1';

function getToken() {
  return localStorage.getItem('argus_access_token');
}

function setMessage(text, isError = false) {
  const el = document.getElementById('form-message');
  if (!el) return;
  el.textContent = text;
  el.className = isError ? 'mt-4 text-sm text-rose-400' : 'mt-4 text-sm text-emerald-400';
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
}

async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const payload = await api('/auth/login', {
    method: 'POST',
    body: formData,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  localStorage.setItem('argus_access_token', payload.access_token);
  localStorage.setItem('argus_refresh_token', payload.refresh_token);
  window.location.href = '/dashboard';
}

async function hydrateDashboard() {
  const profile = await api('/users/me');
  document.getElementById('sidebar-username').textContent = profile.username;
  document.getElementById('sidebar-house').textContent = profile.house_name || 'No house';
  document.getElementById('euros-balance').textContent = profile.euros_balance;
  document.getElementById('planet-chip').textContent = profile.current_planet || 'Mercury';
  document.getElementById('streak-value').textContent = profile.current_streak;
  document.getElementById('lifetime-euros').textContent = profile.lifetime_euros;
  document.getElementById('section-value').textContent = profile.section_name || '—';
  await loadSearchResults();
}

async function loadSearchResults() {
  const data = await api('/search?q=math');
  const container = document.getElementById('search-results');
  if (!container) return;
  container.innerHTML = data.results.map((item) => `
    <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p class="text-sm font-semibold text-slate-800">${item.title}</p>
      <p class="mt-2 text-sm text-slate-600">${item.description}</p>
      <p class="mt-3 text-xs uppercase tracking-[0.25em] text-cyan-600">${item.type}</p>
    </div>
  `).join('');
}

async function completeWorksheet() {
  const payload = await api('/activities/complete', {
    method: 'POST',
    body: JSON.stringify({
      resource_id: '123e4567-e89b-12d3-a456-426614174000',
      activity_type: 'worksheet',
    }),
  });
  await hydrateDashboard();
  alert(`Completed worksheet and earned ${payload.euros_awarded} euros.`);
}

function logout() {
  localStorage.removeItem('argus_access_token');
  localStorage.removeItem('argus_refresh_token');
  window.location.href = '/';
}

window.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value;
      try {
        await login(username, password);
      } catch (error) {
        setMessage(error.message, true);
      }
    });
  }

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }

  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('hidden');
    });
  }

  const worksheetBtn = document.getElementById('complete-worksheet');
  if (worksheetBtn) {
    worksheetBtn.addEventListener('click', completeWorksheet);
  }

  if (window.location.pathname === '/dashboard' && getToken()) {
    hydrateDashboard().catch(() => logout());
  }
});
