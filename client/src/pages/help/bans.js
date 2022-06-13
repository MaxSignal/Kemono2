import { fetchBannedArtists } from "@wp/api";
import { PaginatorClient, UserCard } from "@wp/components";
import { findFavouriteArtist } from "@wp/js/favorites";

/**
 * @typedef IState
 * @property {boolean} isLoading
 * @property {number} [currentPage]
 */

/**
 * @typedef IRenderPageProps
 * @property {import("api/kemono/artists").IBannedArtists} data
 * @property {HTMLUListElement} artistList
 * @property {IState} state
 */

/**
 * @param {HTMLElement} section
 */
export async function bansPage(section) {
  /**
   * @type {IState}
   */
  const state = {
    isLoading: false,
    currentPage: undefined,
  };

  /**
   * @type {HTMLDivElement}
   */
  const cardList = section.querySelector(".card-list");
  /**
   * @type {HTMLUListElement}
   */
  const artistList = cardList.querySelector(".card-list__items");

  const data = await fetchBannedArtists(state.currentPage);

  await renderPage({ state, data, artistList })
}

/**
 * @param {IRenderPageProps} props
 */
async function renderPage({ state, data, artistList }) {
  const { banned_artists, pagination } = data;
  const paginatorTop = PaginatorClient({
    pagination,
    onPageChange: async (page) => {
      if (state.isLoading) {
        return;
      }

      try {
        state.isLoading = true;

        const data = await fetchBannedArtists(page);
        paginatorTop.remove();
        paginatorBottom.remove();
        renderPage({ data, artistList, state });
      } catch (error) {
        alert(error);
      } finally {
        state.isLoading = false;
      }
    }
  });
  const paginatorBottom = PaginatorClient({
    pagination,
    onPageChange: async (page) => {
      if (state.isLoading) {
        return;
      }

      try {
        state.isLoading = true;

        const data = await fetchBannedArtists(page);
        paginatorTop.remove();
        paginatorBottom.remove();
        const { left, top } = artistList.getBoundingClientRect();
        scrollTo({ left, top });
        renderPage({ data, artistList, state });
      } catch (error) {
        alert(error);
      } finally {
        state.isLoading = false;
      }

    }
  });
  const artistCards = document.createDocumentFragment();
  const oldPaginatorTop =
    artistList.previousElementSibling
      && artistList.previousElementSibling.classList.contains("paginator-client")
      ? artistList.previousElementSibling
      : undefined;
  const oldPaginatorBottom = artistList.nextElementSibling;

  for await (const artist of banned_artists) {
    const card = UserCard(null, artist);
    const isFavArtist = await findFavouriteArtist(artist.id, artist.service);

    if (isFavArtist) {
      card.classList.add("user-card--fav");
    }

    artistCards.appendChild(card);
  }


  artistList.replaceChildren(artistCards);

  if (oldPaginatorTop) {
    oldPaginatorTop.replaceWith(paginatorTop);
    oldPaginatorBottom.replaceWith(paginatorBottom);
    return;
  }

  artistList.insertAdjacentElement("beforebegin", paginatorTop);
  artistList.insertAdjacentElement("afterend", paginatorBottom);
}
