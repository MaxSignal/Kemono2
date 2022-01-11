import { NODE_ENV, KEMONO_SITE } from "./env-vars.js";

export const IS_DEVELOPMENT = NODE_ENV === "development";
export const SITE_HOSTNAME = new URL(KEMONO_SITE).hostname;
