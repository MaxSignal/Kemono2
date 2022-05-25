import { isLowerCase } from "@wp/utils";

/**
 * @typedef ValidationResult
 * @property {boolean} isValid
 * @property {string[]} [errors]
 * @property {any} [result] A modified result, if any.
 */

/**
 * @callback KeyValidator
 * @param {string} key
 * @param {string[]} errors
 * @returns {string[]} An array of error messages, if any.
 */

const maxLength = 500;

/**
 * @type {Record<string, KeyValidator>}
 */
const serviceConstraints = {
  patreon: patreonKey,
  fanbox: fanboxKey,
  gumroad: gumroadKey,
  subscribestar: subscribestarKey,
  dlsite: dlsiteKey,
  discord: discordKey,
  fantia: fantiaKey,
}

/**
 * Validates the key according to these rules:
 * - Trim spaces from both sides.
 * @param {string} key
 * @param {string} service
 * @returns {ValidationResult}
 */
export function validateImportKey(key, service) {
  const formattedKey = key.trim();
  const errors = serviceConstraints[service](key, []);

  return {
    isValid: !errors.length,
    errors,
    result: formattedKey
  }
}

/**
 * @type KeyValidator
 */
function patreonKey(key, errors) {
  const reqLength = 43;
  if (key.length !== reqLength) {
    errors.push(`The key length of "${key.length}" is not a valid Patreon key. Required length: "${reqLength}".`)
  }

  return errors
}

/**
 * @type KeyValidator
 */
function fanboxKey(key, errors) {
  const pattern = /^\d+_\w+$/i;

  if (key.length > maxLength) {
    errors.push(`The key length of "${key.length}" is over the maximum of "${maxLength}".`)
  }

  if (!key.match(pattern)) {
    errors.push(`The key doesn't match the required pattern of "${String(pattern)}"`);
  }

  return errors;
}

/**
 * @type KeyValidator
 */
function fantiaKey(key, errors) {
  const reqLengths = [32, 64];

  if (
    reqLengths
      .map(reqLength => key.length !== reqLength)
      .every(v => v === false)
  ) {
    errors.push(
      `The key length of "${key.length}" is not a valid Fantia key. ` +
      `Accepted lengths: ${reqLengths.join(', ')}.`
    )
  }

  if (!isLowerCase(key)) {
    errors.push(`The key is not in lower case.`)
  }

  return errors;
}


/**
 * @type KeyValidator
 */
function gumroadKey(key, errors) {
  const minLength = 200;

  if (key.length < minLength) {
    errors.push(`The key length of "${key.length}" is less than minimum required "${minLength}".`);
  }

  if (key.length > maxLength) {
    errors.push(`The key length of "${key.length}" is over the maximum of "${maxLength}".`)
  }

  return errors;
}

/**
 * @type KeyValidator
 */
function subscribestarKey(key, errors) {

  if (key.length > maxLength) {
    errors.push(`The key length of "${key.length}" is over the maximum of "${maxLength}".`)
  }

  return errors;
}

/**
 * @type KeyValidator
 */
function dlsiteKey(key, errors) {

  if (key.length > maxLength) {
    errors.push(`The key length of "${key.length}" is over the maximum of "${maxLength}".`)
  }

  return errors;
}

/**
 * @type KeyValidator
 */
function discordKey(key, errors) {
  const pattern = /(mfa.[a-z0-9_-]{20,})|([a-z0-9_-]{23,28}.[a-z0-9_-]{6,7}.[a-z0-9_-]{27})/i;

  if (!key.match(pattern)) {
    errors.push(`The key doesn't match the required pattern of "${String(pattern)}".`)
  }

  return errors;
}
