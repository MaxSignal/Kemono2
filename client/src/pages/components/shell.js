import { isLoggedIn } from "@wp/lib/account.js";
import { createComponent } from "@wp/js/component-factory";

/**
 * @param {HTMLElement} header
 */
export function initShell(header) {
  /**
   * @type {HTMLDivElement}
   */
  const accountNavList = document.getElementById("account-buttons");

  if (isLoggedIn) {
    const items = [
      GlobalNavigationItem({ link: "/account", text: "[Account]" }),
      GlobalNavigationItem({ link: "/favorites", text: "[Favorites]" }),
      (() => {
        const item = GlobalNavigationItem({ link: "/account/logout", text: "[Logout]"});
        item.addEventListener("click", (event) => {
          event.preventDefault();
          localStorage.removeItem('logged_in');
          localStorage.removeItem('favs');
          localStorage.removeItem('post_favs');
          location.href = '/account/logout';
        })

        return item;
      })(),
    ];

    accountNavList.append(...items);

  } else {
    const items = [
      GlobalNavigationItem({ link: "/account/login", text: "[Login]" }),
      GlobalNavigationItem({ link: "/account/register", text: "[Register]" }),
    ];

    accountNavList.append(...items);
  }

}

/**
 * @type {Component.GlobalNavigation.Item.Callback}
 */
function GlobalNavigationItem({ element, ...props }) {
  const component = element
    ? element
    : initFromScratch(props)
  ;

  return component;
}

/**
 * TODO: rewrite init as a proper component
 * @type {Component.GlobalNavigation.Item.InitFromScratch}
 */
function initFromScratch({ link, text = link, className }) {
  const component = document.createElement('li');
  const anchour = document.createElement('a');

  if (className) {
    component.classList.add(className);
  }

  anchour.href = link;
  anchour.textContent = text;

  component.appendChild(anchour);

  return component;
}
