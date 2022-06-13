import { CardList } from "@wp/components";
import { isLoggedIn } from "@wp/lib/account.js";
import { findFavouriteArtist } from "@wp/js/favorites";

/**
 * @param {HTMLElement} section
 */
export async function updatedPage(section) {
  const cardListElement = section.querySelector(".card-list");
  const { cardContainer } = CardList(cardListElement);

  for await (const userCard of cardContainer.children ) {
    const { id, service } = userCard.dataset;

    const isFaved = isLoggedIn && await findFavouriteArtist(id, service);

    if (isFaved) {
      userCard.classList.add("user-card--fav");
    }
  }
}
