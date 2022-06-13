import { addFavouriteArtist, findFavouriteArtist, removeFavouriteArtist, findFavouritePost } from "@wp/js/favorites";
import { CardList, PostCard, showTooltip, registerMessage, ButtonArtistBan } from "@wp/components";
import { createComponent } from "@wp/js/component-factory";
import { isLoggedIn } from "@wp/lib/account.js";

/**
 * @param {HTMLElement} section
 */
export async function userPage(section) {
  const artistID = document.head.querySelector("[name='id']").content;
  const artistService = document.head.querySelector("[name='service']").content;
  /**
   * @type {HTMLElement}
   */
  const buttonsPanel = section.querySelector(".user-header__actions");
  const cardListElement = section.querySelector(".card-list");

  await initButtons(buttonsPanel, artistID, artistService);

  if (cardListElement) {
    await initCardList(cardListElement);
  }
}

/**
 * @param {HTMLElement} panelElement
 * @param {string} artistID
 * @param {string} artistService
 */
async function initButtons(panelElement, artistID, artistService) {
  /**
   * @type {HTMLButtonElement}
   */
  const banButtonElem = panelElement.querySelector(".artist-ban");
  const banButton = await ButtonArtistBan({ element: banButtonElem });
  /**
   * @type {HTMLButtonElement}
   */
  const favButton = createComponent("user-header__favourite");
  const favItem = await findFavouriteArtist(artistID, artistService);

  if (localStorage.getItem('logged_in') && favItem) {
    favButton.classList.add("user-header__favourite--unfav");
    const [icon, text] = favButton.children;
    icon.textContent = "★";
    text.textContent = "Unfavorite";
  }

  favButton.addEventListener("click", handleFavouriting(artistID, artistService));

  banButton.insertAdjacentElement("beforebegin", favButton);
}

/**
 * @param {HTMLElement} cardListElement
 */
async function initCardList(cardListElement) {
  const { cardItems } = CardList(cardListElement);

  cardItems.forEach(async (card) => {
    const { postID, userID, service } = PostCard(card);
    const favPost = isLoggedIn && await findFavouritePost(service, userID, postID);

    if (favPost) {
      card.classList.add("post-card--fav");
    }
  });
}

/**
 * @param {string} id
 * @param {string} service
 * @returns {(event: MouseEvent) => Promise<void>}
 */
function handleFavouriting(id, service) {
  return async (event) => {
    /**
     * @type {HTMLButtonElement}
     */
    const button = event.target;

    if (!isLoggedIn) {
      showTooltip(button, registerMessage(null, "Favorites"));
      return;
    }

    const [icon, text] = button.children;
    /**
     * @type {HTMLElement}
     */
    const loadingIcon = createComponent("loading-icon");

    button.disabled = true;
    button.classList.add("user-header__favourite--loading");
    button.insertBefore(loadingIcon, text);

    try {
      if (button.classList.contains("user-header__favourite--unfav")) {
        const isRemoved = await removeFavouriteArtist(id, service);

        if (isRemoved) {
          button.classList.remove("user-header__favourite--unfav");
          icon.textContent = "☆";
          text.textContent = "Favorite";
        }

      } else {
        const isAdded = await addFavouriteArtist(id, service);

        if (isAdded) {
          button.classList.add("user-header__favourite--unfav");
          icon.textContent = "★";
          text.textContent = "Unfavorite";
        }

      }
    } catch (error) {
      console.error(error);

    } finally {
      loadingIcon.remove();
      button.disabled = false;
      button.classList.remove("user-header__favourite--loading");
    }

  };
}
