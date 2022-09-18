import { kemonoAPI } from "@wp/api";
import { CardList, UserCard } from "@wp/components";
import { isLoggedIn } from "@wp/js/account";
import { findFavouriteArtist } from "@wp/js/favorites";

/**
 * @type {KemonoAPI.User[]}
 */
let creators;
/**
 * @type {KemonoAPI.User[]}
 */
let filteredCreators;
let skip = 0;
let limit = 25;

// generic debounce function, idk jsdoc, figure it out :)
function debounce(func, timeout = 300){
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => { func.apply(this, args); }, timeout);
  };
}

/**
 * @param {HTMLElement} section
 */
export async function artistsPage(section) {
  /**
   * @type {HTMLHeadingElement}
   */
  const displayStatus = document.getElementById("display-status");
  /**
   * @type {HTMLDivElement}
   */
  const loadingStatus = document.getElementById("loading");
  /**
   * @type {HTMLFormElement}
   */
  const searchForm = document.forms["search-form"];
  /**
   * @type {HTMLSelectElement}
   */
  const orderSelect = searchForm.elements["order"];
  /**
   * @type {HTMLSelectElement}
   */
  const serviceSelect = searchForm.elements["service"];
  /**
   * @type {HTMLSelectElement}
   */
  const sortSelect = searchForm.elements["sort_by"];
  /**
   * @type {HTMLInputElement}
   */
  const queryInput = searchForm.elements["q"];
  /**
   * @type {HTMLDivElement}
   */
  const cardListElement = section.querySelector(".card-list");
  const { cardList, cardContainer } = CardList(cardListElement);
  const pagination = {
    top: document.getElementById("paginator-top"),
    bottom: document.getElementById("paginator-bottom")
  }

  Array.from(cardContainer.children).forEach(async (userCard) => {
    const { id, service } = userCard.dataset;
    const isFav = isLoggedIn && await findFavouriteArtist(id, service);

    if (isFav) {
      userCard.classList.add("user-card--fav");
    }
  })
  section.addEventListener("click", async (event) => {
    /**
     * @type {HTMLAnchorElement}
     */
    const button = event.target;

    if (
      button.classList.contains("paginator-button")
      && button.dataset
      && button.dataset.value
    ) {
      skip = Number(button.dataset.value);
      filterCards(
        orderSelect.value,
        serviceSelect.value,
        sortSelect.value,
        queryInput.value
      );
      await loadCards(displayStatus, cardContainer, pagination, sortSelect.value);
    }
  });

  searchForm.addEventListener("submit", (event) => event.preventDefault());
  queryInput.addEventListener("change", handleSearch(orderSelect, serviceSelect, sortSelect, queryInput, displayStatus, cardContainer, pagination));
  // 300 ms delay between each keystroke, trigger a new search on each new letter added or removed
  // debounce lets you do this by waiting for the user to stop typing first
  queryInput.addEventListener("keydown", debounce(handleSearch(orderSelect, serviceSelect, sortSelect, queryInput, displayStatus, cardContainer, pagination), 300));
  serviceSelect.addEventListener("change", handleSearch(orderSelect, serviceSelect, sortSelect, queryInput, displayStatus, cardContainer, pagination));
  sortSelect.addEventListener("change", handleSearch(orderSelect, serviceSelect, sortSelect, queryInput, displayStatus, cardContainer, pagination));
  orderSelect.addEventListener("change", handleSearch(orderSelect, serviceSelect, sortSelect, queryInput, displayStatus, cardContainer, pagination));

  await retrieveArtists(loadingStatus);
  handleSearch(orderSelect, serviceSelect, sortSelect, queryInput, displayStatus, cardContainer, pagination)(null);
}

/**
 * @param {HTMLSelectElement} orderSelect
 * @param {HTMLSelectElement} serviceSelect
 * @param {HTMLSelectElement} sortSelect
 * @param {HTMLInputElement} queryInput
 * @param {HTMLDivElement} displayStatus
 * @param {HTMLDivElement} cardContainer
 * @param {{ top: HTMLElement, bottom: HTMLElement }} pagination
 * @return {(event: Event) => void}
 */
function handleSearch(
  orderSelect,
  serviceSelect,
  sortSelect,
  queryInput,
  displayStatus,
  cardContainer,
  pagination
) {
  return async (event) => {
    filterCards(
      orderSelect.value,
      serviceSelect.value,
      sortSelect.value,
      queryInput.value
    );
    await loadCards(displayStatus, cardContainer, pagination, sortSelect.value);
  }
}

// localeCompare isn't slow itself, but this is still faster and we're processing a LOT of data here!
// better get any speed gains we can
function fastCompare(a, b) {
  return a < b ? -1 : (a > b ? 1 : 0);
}

/**
 * @param {string} order
 * @param {string} service
 * @param {string} sortBy
 * @param {string} query
 */
function filterCards(order, service, sortBy, query) {
  filteredCreators = creators.slice(0);

  if (order === 'desc') {
    filteredCreators.reverse()
  }

  filteredCreators = filteredCreators.filter(
    creator => creator.service === (service || creator.service)
  ).sort((a, b) => {

    if (order === 'desc') {
      return sortBy === 'indexed'
        ? a.parsedIndexed - b.parsedIndexed
        : fastCompare(a[sortBy], b[sortBy]);

    } else {
      return sortBy === 'indexed'
        ? b.parsedIndexed - a.parsedIndexed
        : fastCompare(b[sortBy], a[sortBy]);
    }
  }).filter(creator => {
    return creator.name.match(
      new RegExp(
        query.replace(
          /[-\/\\^$*+?.()|[\]{}]/g,
          '\\$&'
        ),
        'i'
      )
    )
  })
}

function createPaginator() {
  let currentPage = Math.ceil(skip / limit);
  let maxPages = Math.ceil(filteredCreators.length / limit);
  const range = skip >= 100
    ? createRange(currentPage - 2, currentPage + 3)
    : createRange(0, 7);

  const paginator = `
    <small>Showing ${ skip + 1 } - ${ skip + limit } of ${ filteredCreators.length }</small>
    <menu>
      ${skip >= limit
        ? `<li>
            <a href="#" class="paginator-button" data-value="${skip - limit}" title="Previous page">
              &lt;
            </a>
          </li>`
        : '<li class="subtitle">&lt;</li>'
      }
      ${skip >= 100
        ? `
        <li>
          <a href="#" class="paginator-button" data-value="0">
            1
          </a>
        </li>
        <li>...</li>
      ` : ''
      }
      ${range.map(page => {
        if (filteredCreators.length > page * limit) {
          if (page * limit == skip) {
            return `<li>${page + 1}</li>`
          } else {
            return `
              <li>
                <a href="#" class="paginator-button" data-value="${page * limit}">
                  ${page + 1}
                </a>
              </li>
            `
          }
        }
      }).join('')}
      ${createRange(0, maxPages).map((page, index, arr) => {
        if (index === arr.length - 1 && filteredCreators.length - skip >= 100 && filteredCreators.length > 175) {
          return `
            <li>...</li>
            <li>
              <a href="#" class="paginator-button" data-value="${page * limit}">
                ${maxPages}
              </a>
            </li>
          `
        }
      }).join('')}
      ${filteredCreators.length - skip > limit ? `
        <li><a href="#" class="paginator-button" data-value="${skip + limit}" title="Next page">&gt;</a></li>
      ` : `
        <li class="subtitle">&gt;</li>
      `}
    </menu>`

  return paginator;
}

/**
 * @param {HTMLDivElement} displayStatus
 * @param {HTMLDivElement} cardContainer
 * @param {{ top: HTMLElement, bottom: HTMLElement }} pagination
 * @param {String} sortBy
 */
async function loadCards(displayStatus, cardContainer, pagination, sortBy) {
  displayStatus.textContent = 'Displaying search results';
  pagination.top.innerHTML = createPaginator();
  pagination.bottom.innerHTML = createPaginator();
  /**
   * @type {[ HTMLDivElement, HTMLElement ]}
   */
  const [header, ...cards] = cardContainer.children;
  cards.forEach((card) => {
    card.remove();
  });

  if (filteredCreators.length === 0) {
    const paragraph = document.createElement("p");

    paragraph.classList.add("subtitle", "card-list__item--no-results");
    paragraph.textContent = "No artists found for your query.";
    cardContainer.appendChild(paragraph);
    return;
  } else {
    const fragment = document.createDocumentFragment();

    for await (const user of filteredCreators.slice(skip, skip + 25)) {
      const userIsCount = sortBy === 'favorited';
      const userIsIndexed = sortBy === 'indexed';
      const userIsUpdated = sortBy === 'updated';
      const userCard = UserCard(null, user, userIsCount, userIsUpdated, userIsIndexed);
      const isFaved = isLoggedIn && await findFavouriteArtist(user.id, user.service);

      if (isFaved) {
        userCard.classList.add("user-card--fav");
      }

      fragment.appendChild(userCard);
    };

    cardContainer.appendChild(fragment);
  }
}

/**
 * @param {HTMLDivElement} loadingStatus
 */
async function retrieveArtists(loadingStatus) {
  try {
    const artists = await kemonoAPI.api.creators();

    if (!artists) {
      return null;
    }

    for (const artist of artists) {
      // preemptively do it here, it's taxing to parse a date string then convert it to a unix timestamp in milliseconds
      // this way we only have to do it once after fetching and none for sorting
      artist.parsedIndexed = artist.indexed * 1000;
      artist.parsedUpdated = artist.updated * 1000;
      artist.indexed = new Date(artist.parsedIndexed).toISOString();
      artist.updated = new Date(artist.parsedUpdated).toISOString();
    }

    loadingStatus.innerHTML = '';
    creators = artists;
    filteredCreators = artists;

  } catch (error) {
    console.error(error);
  }
}

/**
 * @param {number} start
 * @param {number} end
 */
function createRange(start, end) {
  const length = end - start;
  const range = Array.from({ length }, (_, index) => start + index);

  return range;
}