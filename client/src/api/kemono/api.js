import { KemonoAPIError } from "@wp/utils";
import { kemonoFetch } from "./kemono-fetch";

export const api = {
  bans,
  bannedArtist,
  creators,
  logs,
  artists,
};

async function bans() {
  try {
    const response = await kemonoFetch('/api/bans', { method: "GET" });

    if (!response || !response.ok) {

      alert(new KemonoAPIError(6));
      return null;
    }

    /**
     * @type {KemonoAPI.API.BanItem[]}
     */
    const banItems = await response.json();

    return banItems;

  } catch (error) {
    console.error(error);
  }
}

/**
 * @param {string} id
 * @param {string} service
 */
async function bannedArtist(id, service) {
  const params = new URLSearchParams([
    ["service", service],
  ]).toString();

  try {
    const response = await kemonoFetch(`/api/lookup/cache/${id}?${params}`);

    if (!response || !response.ok) {
      alert(new KemonoAPIError(7));
      return null;
    }

    /**
     * @type {KemonoAPI.API.BannedArtist}
     */
    const artist = await response.json();

    return artist;

  } catch (error) {
    console.error(error);
  }
}

/**
 * @typedef IPagination
 * @property {number} total_count
 * @property {number} total_pages
 * @property {number} current_page
 * @property {number} limit
 */

/**
 * @typedef IArtist
 * @property {string} id
 * @property {string} indexed
 * @property {string} name
 * @property {string} service
 * @property {string} updated
 */

/**
 * @typedef IArtistsAPIBody
 * @property {IPagination} pagination
 * @property {IArtist[]} artists
 */

/**
 * @typedef IArtistsAPIResponse
 * @property {boolean} is_successful
 * @property {IArtistsAPIBody} data
 */

const DEFAULT_PAGE_LIMIT = 25;
/**
 * @type {IArtist[]}
 */
let artistList = undefined;

/**
 * @param {number} [page]
 * @param {string} [service]
 * @param {string} [name] Assumed to be stripped and formatted already.
 * @returns {Promise<IArtistsAPIResponse>}
 */
export async function fetchArtists(page, service, name) {
  if (!name && !artistList) {
    const response = await artists(page, service);
    return response;
  }

  if (!artistList) {
    artistList = await creators();
  }
  console.log(service, name);
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
  const limit = DEFAULT_PAGE_LIMIT;
  const totalCount = filteredArtists.length;
  const totalPages = Math.floor(totalCount / limit) + 1;
  const currentPage = page ? page : totalPages;
  const offset = (currentPage - 1) * DEFAULT_PAGE_LIMIT;
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
 * @returns {Promise<IArtistsAPIResponse>}
 */
async function artists(page, service,) {
  const path = page
    ? `/api/v1/artists/${page}`
    : "/api/v1/artists";

  const searchParams = new URLSearchParams();

  if (service) {
    searchParams.set("service", service);
  }

  const url = Array.from(searchParams.keys()).length
    ? `${path}?${searchParams.toString()}`
    : path;

  try {
    const response = await kemonoFetch(url, { method: "GET" });
    if (!response || !response.ok) {

      alert(new KemonoError(8));
      return null;
    }

    const apiResponse = await response.json();

    return apiResponse;
  } catch (error) {

  }
}

async function creators() {
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

/**
 * @param {string} importID
 */
async function logs(importID) {
  try {
    const response = await kemonoFetch(`/api/logs/${importID}`, { method: "GET" });

    if (!response || !response.ok) {
      alert(new KemonoAPIError(9));
      return null;
    }

    /**
     * @type {KemonoAPI.API.LogItem[]}
     */
    const logs = await response.json();

    return logs;

  } catch (error) {
    console.error(error);
  }
}
