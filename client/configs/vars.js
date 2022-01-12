const path = require("path");

require('dotenv').config({ 
  path: path.resolve(__dirname, "..", "..")
});

const kemonoSite = process.env.KEMONO_SITE || "http://localhost:5000";
const nodeEnv = process.env.NODE_ENV || "production"

module.exports = {
  kemonoSite,
  nodeEnv
}
