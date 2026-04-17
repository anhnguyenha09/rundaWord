function openAuth(tab) {
  var overlay = document.getElementById('authOverlay');
  if (!overlay) return;
  overlay.classList.add('open');
  switchTab(tab || 'login');
}

function closeAuth() {
  var overlay = document.getElementById('authOverlay');
  if (!overlay) return;
  overlay.classList.remove('open');
}

function closeAuthOnBg(e) {
  if (e.target === document.getElementById('authOverlay')) closeAuth();
}

function switchTab(tab) {
  var loginTab = document.getElementById('tabLogin');
  var regTab = document.getElementById('tabRegister');
  var loginPanel = document.getElementById('panelLogin');
  var regPanel = document.getElementById('panelRegister');
  if (!loginTab || !regTab || !loginPanel || !regPanel) return;

  if (tab === 'register') {
    loginTab.classList.remove('active'); regTab.classList.add('active');
    loginPanel.classList.remove('active'); regPanel.classList.add('active');
  } else {
    regTab.classList.remove('active'); loginTab.classList.add('active');
    regPanel.classList.remove('active'); loginPanel.classList.add('active');
  }
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeAuth();
});

