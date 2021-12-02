const { ENV_VARS } = require("./vars.js");

class DERIVED_VARS {
  static IS_DEVELOPMENT = ENV_VARS.NODE_ENV === "development"
}

module.exports = { DERIVED_VARS }
