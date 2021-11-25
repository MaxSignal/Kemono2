import { isLoggedIn } from "@wp/js/account";

/**
 * @param {HTMLElement} sidebar
 */
export function initShell(sidebar) {
  document.body.classList.remove('transition-preload');
  setTimeout(() => {
    sidebar.classList.remove('sidebar-hidden');
  }, 250);
  const burgor = document.getElementById('burgor');
  const backdrop = document.querySelector('.backdrop');
  const closeButton = sidebar.querySelector('.close-sidebar');
  const closeSidebar = () => {
    sidebar.classList.toggle('expanded');
    backdrop.classList.toggle('backdrop-hidden');
  };
  burgor.addEventListener('click', closeSidebar);
  backdrop.addEventListener('click', closeSidebar);
  closeButton.addEventListener('click', closeSidebar);
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
  if (!isLoggedIn) return;
  const accountList = sidebar.querySelector('.account');
  const logout = accountList.querySelector('.logout');
  if (!logout) return;
  logout.addEventListener('click', e => {
    e.preventDefault();
    localStorage.removeItem('logged_in');
    localStorage.removeItem('favs');
    localStorage.removeItem('post_favs');
    location.href = '/account/logout';
  });
}
