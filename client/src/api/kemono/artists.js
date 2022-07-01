import { KemonoAPIError } from "@wp/utils";
import { kemonoFetch, defaultHeaders, createRequestBody } from "./kemono-fetch";

/**
 * @typedef IBannedInfo
 * @property {string} id
 * @property {string} service
 */

/**
 * @param {string} id
 * @param {string} service
 * @returns {Promise<IBannedInfo>}
 */
export async function banArtist(id, service) {
  const body = createRequestBody({ id, service });

  try {
    const response = await kemonoFetch(
      "/api/v1/account/administrator/bans",
      {
        headers: defaultHeaders,
        method: "PUT",
        body
      }
    );

    if (!response || !response.ok) {
      alert(new KemonoAPIError(10));
      return null;
    }

    /**
     * @type {import("./kemono-fetch").IAPIResponse<IBannedInfo>}
     */
    const apiResponse = await response.json();

    return apiResponse.data;
  } catch (error) {
    console.error(error);
  }

}

/**
 * @param {string} id
 * @param {string} service
 * @returns {Promise<IBannedInfo>}
 */
export async function unbanArtist(id, service) {
  const body = createRequestBody({ id, service });

  try {
    const response = await kemonoFetch(
      "/api/v1/account/administrator/bans",
      {
        headers: defaultHeaders,
        method: "DELETE",
        body
      }
    );

    if (!response || !response.ok) {
      alert(new KemonoAPIError(11));
      return null;
    }

    /**
     * @type {import("./kemono-fetch").IAPIResponse<IBannedInfo>}
     */
    const apiResponse = await response.json();

    return apiResponse.data;
  } catch (error) {
    console.error(error);
  }

}

/**
 * @returns {Promise<import("@wp/lib/artists.js").IArtist[]>}
 */
 export async function fetchAllBannedArtists() {
  let currentPage = undefined;
  const bannedArtists = [];

  while (true) {
    const { banned_artists, pagination } = await fetchBannedArtists(currentPage);
    bannedArtists.push(...banned_artists);
    const { current_page, total_count } = pagination;

    if (bannedArtists.length === total_count) {
      break;
    }

    currentPage = current_page;
  }

  return bannedArtists;
}

/**
 * @typedef IBannedArtists
 * @property {import("./fetch-artists.js").IPagination} pagination
 * @property {import("@wp/lib/artists.js").IArtist[]} banned_artists
 */

/**
 * @param {number} page
 * @returns {Promise<import("./kemono-fetch").IAPIResponse<IBannedArtists>["data"]>}
 */
export async function fetchBannedArtists(page) {
  const path = page
    ? `/api/v1/banned-artists/${page}`
    : "/api/v1/banned-artists";

  try {
    const response = await kemonoFetch(
      path,
      {
        headers: defaultHeaders,
        method: "GET",
      }
    );

    if (!response || !response.ok) {
      alert(new KemonoAPIError(6));
      return null;
    }

    /**
     * @type {import("./kemono-fetch").IAPIResponse<IBannedArtists>}
     */
    const apiResponse = await response.json();

    return apiResponse.data;
  } catch (error) {
    console.error(error);
  }
}
