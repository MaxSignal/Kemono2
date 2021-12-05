import { createComponent } from "@wp/js/component-factory";
import { isLoggedIn } from "@wp/js/account";

window.addEventListener('load', () => {
  document.body.classList.remove('transition-preload');
});

/**
 * @param {HTMLElement} sidebar
 */
export function initShell(sidebar) {
  const burgor = document.getElementById('burgor');
  const header = burgor.parentElement;
  const backdrop = document.querySelector('.backdrop');
  const closeButton = sidebar.querySelector('.close-sidebar');
  const closeSidebar = (_, setState = true) => {
    sidebar.classList.toggle('expanded');
    sidebar.classList.toggle('retracted');
    backdrop.classList.toggle('backdrop-hidden');
    const retracted = header.classList.toggle('sidebar-retracted');
    if (setState && window.innerWidth > 1020) localStorage.setItem('sidebar_state', retracted);
  };
  if (typeof localStorage.getItem('sidebar_state') === 'string') {
    const sidebarState = localStorage.getItem('sidebar_state') === 'true';
    if (window.innerWidth > 1020 && sidebarState) closeSidebar();
  }
  window.addEventListener('resize', () => {
    if (typeof localStorage.getItem('sidebar_state') !== 'string') return;
    const sidebarState = localStorage.getItem('sidebar_state') === 'true';
    const realState = header.classList.contains('sidebar-retracted');
    const killAnimations = () => {
      document.body.classList.add('transition-preload');
      requestAnimationFrame(() => setInterval(() => document.body.classList.remove('transition-preload')));
    }
    if (window.innerWidth <= 1020) {
      if (sidebarState && realState) {
        killAnimations();
        closeSidebar(null, false);
      }
    } else if (sidebarState && !realState) {
      killAnimations();
      closeSidebar();
    }
  });
  burgor.addEventListener('click', closeSidebar);
  backdrop.addEventListener('click', closeSidebar);
  closeButton.addEventListener('click', closeSidebar);
  if (isLoggedIn) {
    const accountList = sidebar.querySelector('.account');
    const login = accountList.querySelector('.login');
    const register = accountList.querySelector('.register');
    const favorites = accountList.querySelector('.favorites');
    login.classList.remove('login');
    register.classList.remove('register');
    favorites.classList.remove('hidden');
    login.innerText = 'Logout';
    login.href = '/account/logout';
    register.innerText = 'Keys';
    register.href = '/account/keys';
    login.addEventListener('click', e => {
      e.preventDefault();
      localStorage.removeItem('logged_in');
      localStorage.removeItem('favs');
      localStorage.removeItem('post_favs');
      location.href = '/account/logout';
    })
  } else {
    const accountHeader = sidebar.querySelector('.account-header');
    const newHeader = document.createElement('div');
    newHeader.className = 'global-sidebar-entry-item header';
    newHeader.innerText = 'Account';
    accountHeader.parentElement.replaceChild(newHeader, accountHeader);
  }
  // questionable? close sidebar on tap of an item,
  // delay loading of page until animation is done
  // uncomment to close on tap
  // uncomment the items commented with // to add a delay so it finishes animating
  /* sidebar.querySelectorAll('.global-sidebar-entry-item').forEach(e => {
    e.addEventListener('click', ev => {
      //ev.preventDefault();
      sidebar.classList.remove('expanded');
      backdrop.classList.add('backdrop-hidden');
      // setTimeout(() => {
      //   location.href = e.href;
      // }, 250);
    })
  }) */
}
