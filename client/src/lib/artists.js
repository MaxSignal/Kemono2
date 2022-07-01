import { fetchAllBannedArtists } from "@wp/api";

/**
 * @typedef IArtist
 * @property {string} id
 * @property {string} indexed
 * @property {string} name
 * @property {string} service
 * @property {string} updated
 */


/**
 * @type {IArtist[] | undefined}
 */
let bannedArtists = undefined;

/**
 * @param {string} id
 * @param {string} service
 */
export async function isArtistBanned(id, service) {
  if (!bannedArtists) {
    bannedArtists = await fetchAllBannedArtists();
  }

  const bannedArtist = bannedArtists.find((artist) => {
    return artist.id === id && artist.service === service;
  });

  if (!bannedArtist) {
    return false;
  }

  return true;
}
