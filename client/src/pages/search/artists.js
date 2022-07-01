import { fetchArtists } from "@wp/api";
import { PaginatorClient, UserCard } from "@wp/components";
import { findFavouriteArtist } from "@wp/js/favorites";

/**
 * @typedef IState
 * @property {boolean} isLoading
 * @property {number} [currentPage]
 * @property {string} [service]
 * @property {string} [name]
 * @property {import("api/kemono/fetch-artists.js").IArtistsSort} [sort_by]
 */

/**
 * @typedef IRenderPageProps
 * @property {import("api/kemono/fetch-artists.js").IArtistsAPIResponse["data"]} data
 * @property {HTMLUListElement} artistList
 * @property {IState} state
 */

/**
 * @param {HTMLElement} section
 */
export async function searchArtistsPage(section) {
  /**
   * @type {IState}
   */
  const state = {
    isLoading: false,
    currentPage: undefined,
    name: undefined,
    service: undefined,
    sort_by: undefined
  };
  /**
   * @type {HTMLFormElement}
   */
  const searchForm = document.forms["artist-search"];

  /**
   * @type {HTMLDivElement}
   */
  const cardList = section.querySelector(".card-list");
  /**
   * @type {HTMLUListElement}
   */
  const artistList = cardList.querySelector(".card-list__items");

  initSearchForm(searchForm, artistList, state);
}

/**
 * @param {HTMLFormElement} form
 * @param {HTMLUListElement} artistList
 * @param {IState} state
 */
function initSearchForm(form, artistList, state) {
  const optionalFieldset = form.querySelector(".form__fieldset--optional");

  optionalFieldset.addEventListener("click", (event) => {
    /**
     * @type {HTMLButtonElement}
     */
    const button = event.target;
    const more = button.closest(".form__more");
    const less = button.closest(".form__less");

    if (!more && !less) {
      return;
    }

    if (more) {
      optionalFieldset.classList.toggle("form__fieldset--more", true);

      return;
    }

    optionalFieldset.classList.toggle("form__fieldset--more", false);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (state.isLoading) {
      return;
    }

    try {
      state.isLoading = true;
      form.classList.add("form--submitting");
      /**
       * @type {HTMLSelectElement}
       */
      const serviceSelect = form.elements["service"];
      const service = serviceSelect.value;
      /**
       * @type {HTMLSelectElement}
       */
      const sortSelect = form.elements["sort_by"];
      /**
       * @type {import("api/kemono/fetch-artists.js").IArtistsSort}
       */
      const sort_by = sortSelect.value;

      /**
       * @type {HTMLInputElement}
       */
      const nameInput = form.elements["name"];
      const name = nameInput.value.trim().toLowerCase();

      const { data } = await fetchArtists(state.currentPage, {
        name,
        service,
        sort_by
      });
      state.service = service;
      state.name = name;
      state.sort_by = sort_by;

      await renderPage({ data, artistList, state });
    } catch (error) {
      alert(error);
    } finally {
      state.isLoading = false;
      form.classList.remove("form--submitting");
    }
  });
}

/**
 * @param {IRenderPageProps} props
 */
async function renderPage({ data, artistList, state }) {
  const { artists, pagination } = data;
  const paginatorTop = PaginatorClient({
    pagination,
    onPageChange: async (page) => {
      if (state.isLoading) {
        return;
      }

      try {
        state.isLoading = true;

        const { data } = await fetchArtists(page, state);
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

        const { data } = await fetchArtists(page, state);
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

  for await (const artist of artists) {
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
