import { fetchAccountInfo } from "@wp/api";
/**
 * @typedef {"consumer"| "moderator"| "administrator"} IAccountRoles
 */

/**
 * @typedef IAccountInfo
 * @property {IAccountRoles} role
 */

const accountRoles = ["consumer", "moderator", "administrator"];
/**
 * @type {IAccountInfo | undefined}
 */
let account = undefined;
export const isLoggedIn = localStorage.getItem("logged_in") === "yes";

/**
 * @returns {Promise<IAccountInfo | undefined>}
 */
export async function getAccount() {
  if (account) {
    return account;
  }

  const isLoggedIn = localStorage.getItem("logged_in") === "yes";

  if (!isLoggedIn) {
    return;
  }

  const accountInfo = localStorage.getItem("accountInfo");

  try {
    account = JSON.parse(accountInfo);

    if (!account) {
      throw new Error("Account is empty")
    }

    return account;
  } catch (error) {
    console.error(error);
  }

  account = await fetchAccountInfo();
  localStorage.setItem("accountInfo", JSON.stringify(account));

  return account;
}

export async function isAdministrator() {
  const account = await getAccount();

  if (!account) {
    return false;
  }

  return true;
}
