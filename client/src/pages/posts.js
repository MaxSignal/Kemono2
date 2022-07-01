import { CardList, PostCard } from "@wp/components";
import { isLoggedIn } from "@wp/lib/account.js";
import { findFavouritePost, findFavouriteArtist } from "@wp/js/favorites";

/**
 * @param {HTMLElement} section
 */
export function postsPage(section) {
  const cardListElement = section.querySelector(".card-list");
  const { cardList, cardItems } = CardList(cardListElement);

  cardItems.forEach(async (card) => {
    const { postID, userID, service } = PostCard(card);
    const favPost = isLoggedIn && await findFavouritePost(service, userID, postID);
    const favUser = isLoggedIn && await findFavouriteArtist(userID, service);

    if (favPost) {
      card.classList.add("post-card--fav");
    };

    if (favUser) {
      const user = card.querySelector(".post-card__user");
      const userName = card.querySelector(".post-card__name");

      user.classList.add("post-card__user--fav");
      userName.textContent = favUser.name;
    };

  });
}
