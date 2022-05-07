import { KemonoError } from "@wp/utils";
import { kemonoFetch } from "./kemono-fetch";

export const api = {
  bans,
  bannedArtist,
  creators,
  logs
};

async function bans() {
  try {
    const response = await kemonoFetch('/api/bans', { method: "GET" });

    if (!response || !response.ok) {

      alert(new KemonoError(6));
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
    ["service", service ],
  ]).toString();

  try {
    const response = await kemonoFetch(`/api/lookup/cache/${id}?${params}`);

    if (!response || !response.ok) {
      alert(new KemonoError(7));
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

async function creators() {
  try {
    const response = await kemonoFetch('/api/creators', { method: "GET" });

    if (!response || !response.ok) {

      alert(new KemonoError(8));
      return null;
    }

    /**
     * @type {KemonoAPI.User[]}
     */
    const artists = await response.json();

    return artists;

  } catch (error) {
    console.error(error);
  }
}

async function logs(importID) {
  try {
    const response = await kemonoFetch(`/api/logs/${importID}`, { method: "GET" });

    if (!response || !response.ok) {
      alert(`Error 009 - ${errorList.get("009")}`);
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