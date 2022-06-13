import { KemonoAPIError } from "@wp/utils";
import { kemonoFetch } from "./kemono-fetch";

/**
 * @typedef IPagination
 * @property {number} total_count
 * @property {number} total_pages
 * @property {number} current_page
 * @property {number} limit
 */



/**
 * @typedef {"updated"| "added"| "name"| "service"} IArtistsSort
 */

/**
 * @typedef IArtistsParams
 * @property {string} [service]
 * @property {string} [name] Assumed to be stripped and formatted already.
 * @property {IArtistsSort} [sort_by]
 */

/**
 * @typedef IArtistsAPIBody
 * @property {IPagination} pagination
 * @property {import("@wp/lib/artists.js").IArtist[]} artists
 */

/**
 * @typedef IArtistsAPIResponse
 * @property {boolean} is_successful
 * @property {IArtistsAPIBody} data
 */

const DEFAULT_PAGE_LIMIT = 25;
const defaultSort = "updated";
/**
 * @type {Set<IArtistsSort>}
 */
const sortFields = new Set([
  defaultSort,
  "added",
  "name",
  "service"
]);

/**
 * @type {IArtistsParams}
 */
const defaultParams = {
  name: undefined,
  service: undefined,
  sort_by: defaultSort
};

/**
 * @type {import("@wp/lib/artists.js").IArtist[]}
 */
 let artistList = undefined;

/**
 * @param  {...keyof import("@wp/lib/artists.js").IArtist} fields
 * @returns {(prev: import("@wp/lib/artists.js").IArtist, next: import("@wp/lib/artists.js").IArtist) => -1 | 0 | 1} A comparator function which can be fed to `Array.sort()`.
 */
function createArtistComparator(...fields) {
  return (prev, next) => {
    const result = fields.map((field) => {
      const prevField = prev[field];
      const nextField = next[field];

      const result = prevField === nextField
        ? undefined
        : prevField < nextField
          ? -1
          : 1;

      return result;
    }).find((result) => result);

    return result ? result : 0;
  };
};

/**
 * @param {number} [page]
 * @param {IArtistsParams} [params]
 * @returns {Promise<IArtistsAPIResponse>}
 */
export async function fetchArtists(page, params) {
  const finalParams = params
    ? { ...defaultParams, ...params }
    : defaultParams;
  const { name, service, sort_by } = finalParams;

  if (!name && !artistList) {
    const response = await artists(page, service, sort_by);
    return response;
  }

  if (!artistList) {
    artistList = await creators();
  }

  const filteredArtists = service || name
    ? artistList.filter(
      (artist) => {
        const isService = service
          ? artist.service === service
          : true;
        const isName = name
          ? artist.name.toLowerCase().includes(name) || artist.id.toLowerCase().includes(name)
          : true;
        const isEligible = isService && isName;
        return isEligible;
      }
    )
    : artistList;

  switch (sort_by) {
    case "updated": {
      filteredArtists.sort(
        createArtistComparator("updated", "name", "service")
      );
      break;
    }

    case "added": {
      filteredArtists.sort(
        createArtistComparator("indexed", "name", "service")
      );
      break;
    }

    case "name": {
      filteredArtists.sort(
        createArtistComparator("name", "service", "indexed")
      );
      break;
    }

    case "service": {
      filteredArtists.sort(
        createArtistComparator("service", "name", "indexed")
      );
      break;
    }

    default: {
      const fieldsList = Array.from(sortFields.keys()).join(", ");
      const message = [
        `Sorting ${sort_by} is not a valid value`,
        `Allowed values: ${fieldsList}`
      ].join("\n");
      throw new Error(message);
    };
  }
  const limit = DEFAULT_PAGE_LIMIT;
  const totalCount = filteredArtists.length;
  const totalPages = Math.floor(totalCount / limit) + 1;
  const currentPage = page ? page : totalPages;
  const offset = (currentPage - 1) * limit;
  /**
   * @type {IPagination}
   */
  const pagination = {
    current_page: currentPage,
    limit: limit,
    total_count: totalCount,
    total_pages: totalPages
  };
  const artistsPage = filteredArtists.slice(offset, offset + limit);

  /**
   * @type {IArtistsAPIResponse}
   */
  const response = {
    is_successful: true,
    data: {
      pagination,
      artists: artistsPage
    }
  };

  return response;
}

/**
 * @param {number} [page]
 * @param {string} [service]
 * @param {IArtistsSort} [sortBy]
 * @returns {Promise<IArtistsAPIResponse>}
 */
export async function artists(page, service, sortBy) {
  const path = page
    ? `/api/v1/artists/${page}`
    : "/api/v1/artists";

  const searchParams = new URLSearchParams();

  searchParams.set("sort_by", sortBy ? sortBy : defaultSort);

  if (service) {
    searchParams.set("service", service);
  }

  const url = Array.from(searchParams.keys()).length
    ? `${path}?${searchParams.toString()}`
    : path;

  try {
    const response = await kemonoFetch(url, { method: "GET" });
    if (!response || !response.ok) {

      alert(new KemonoAPIError(8));
      return null;
    }

    const apiResponse = await response.json();

    return apiResponse;
  } catch (error) {

  }
}

export async function creators() {
  try {
    const response = await kemonoFetch('/api/creators', { method: "GET" });

    if (!response || !response.ok) {

      alert(new KemonoAPIError(8));
      return null;
    }

    /**
     * @type {KemonoAPI.Artist[]}
     */
    const artists = await response.json();

    return artists;

  } catch (error) {
    console.error(error);
  }
}
