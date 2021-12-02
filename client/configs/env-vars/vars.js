const { CONSTANTS } = require("./constants.js");

require('dotenv').config({
  path: CONSTANTS.PROJECT_ROOT
});

const kemonoEnvValues = ['production', 'development']

//  TODO: use it later
const envFilename = {
  development: '.env.dev',
  production: '.env.prod'
}

class ENV_VARS {
  static NODE_ENV = process.env.NODE_ENV || "development"
  static KEMONO_SITE = process.env.KEMONO_SITE || "http://localhost:5000"
}

const criticalVars = [];
validateVars(criticalVars);

/**
 * @param {string[]} varList
 */
function validateVars(varList) {
  /**
   * @type {string[]}
   */
  const missingVars = varList.reduce(
    (missingVars, envVar) => {
      if (!ENV_VARS[envVar]) {
        missingVars.push(envVar);
      }

      return missingVars;
    },
    []
  );

  if (missingVars.length) {
    const varString = missingVars.join(", ");
    throw Error(`These environment variables are not set: ${varString}`);
  }
}

module.exports = { ENV_VARS };
