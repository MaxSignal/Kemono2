const antiscraperHost = "anti-scraper.herokuapp.com";

/**
 * @param {string} urlString
 */
export function isAntiscraperLink(urlString) {
  const url = new URL(urlString);

  if (url.hostname.includes(antiscraperHost)) {
    return true;
  }

  return false;
}
