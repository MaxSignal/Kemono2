import { KemonoAPIError } from "@wp/utils";
import { artists, creators } from "./fetch-artists.js";
import { defaultHeaders, kemonoFetch } from "./kemono-fetch";

export const api = {
  bannedArtist,
  creators,
  logs,
  artists,
};


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
