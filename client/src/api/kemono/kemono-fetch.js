import { isLoggedIn } from "@wp/lib/account.js";

/**
 * @template {unknown} DataType
 * @typedef IAPIRequest
 * @property {DataType} data
 */

/**
 * @template {unknown} DataType
 * @typedef IAPIResponse
 * @property {boolean} is_successful
 * @property {DataType} data
 */

export const defaultHeaders = new Headers([
  ["Content-Type", "application/json"],
  ["Accept", "application/json"]
]);

/**
 * @param {Record<string, unknown>} body
 */
export function createRequestBody(body) {
  return JSON.stringify({ data: body })
}

/**
 * Generic request for Kemono API.
 * @param {RequestInfo} endpoint
 * @param {RequestInit} [options]
 * @returns {Promise<Response>}
 */
export async function kemonoFetch(endpoint, options) {

  try {
    const response = await fetch(endpoint, options);

    // doing this because the server returns `401` before redirecting
    // in case of favs
    if (response.status === 401) {
      // server logged the account out
      if (isLoggedIn) {
        localStorage.removeItem('logged_in');
        localStorage.removeItem('favs');
        localStorage.removeItem('post_favs');
        location.href = '/account/logout';
        return;
      }
      const loginURL = new URL("/account/login", location.origin).toString();
      location = addURLParam(loginURL, "redir", location.pathname);
      return;
    }

    return response;

  } catch (error) {
    console.error(`Kemono request error: ${error}`);
  }
}

/**
 * @param {string} url
 * @param {string} paramName
 * @param {string} paramValue
 * @returns {string}
 */
function addURLParam(url, paramName, paramValue) {
  var newURL = new URL(url);
  newURL.searchParams.set(paramName, paramValue);
  return newURL.toString();
}
