import { KemonoAPIError } from "@wp/utils";
import { kemonoFetch, defaultHeaders } from "./kemono-fetch";

/**
 *
 * @returns {Promise<import("@wp/lib/account.js").IAccountInfo>}
 */
export async function fetchAccountInfo() {
  try {
    const response = await kemonoFetch(
      "/api/v1/account",
      {
        headers: defaultHeaders,
        method: "GET",
      }
    );

    if (!response || !response.ok) {
      alert(new KemonoAPIError(12));
      return null;
    }

    /**
     * @type {import("./kemono-fetch").IAPIResponse<import("@wp/lib/account.js").IAccountInfo>}
     */
    const apiResponse = await response.json();

    return apiResponse.data;
  } catch (error) {
    console.error(error);
  }
  try {

  } catch (error) {
    console.error(error)
  }
}
