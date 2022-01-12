const path = require("path");
const { DefinePlugin } = require("webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const { buildHTMLWebpackPluginsRecursive } = require("./configs/build-templates");
const { kemonoSite, nodeEnv } = require("./configs/vars");

const projectPath = path.resolve(__dirname, "src");
const pagesPath = path.join(projectPath, "pages");
const pagePlugins = buildHTMLWebpackPluginsRecursive(pagesPath, {
  fileExtension: "html",
  pluginOptions: {
    inject: false,
    minify: false,
  }
});

/**
 * TODO: make separate entries for `admin` and `moderator`
 * @type import("webpack").Configuration
 */
const webpackConfig = {
  entry: {
    global: path.join(projectPath, "js", "global.js"),
    admin: path.join(projectPath, "js", "admin.js"),
    // moderator: path.join(projectPath, "js", "moderator.js"),
  },
  plugins: [
    ...pagePlugins,
    new DefinePlugin({
      "BUNDLER_ENV_KEMONO_SITE": JSON.stringify(kemonoSite),
      "BUNDLER_ENV_NODE_ENV": JSON.stringify(nodeEnv),
    }),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: "static",
          to: "static"
        }
      ]
    }),
  ],
  resolve: {
    extensions: [".js"],
    alias: {
      ["@wp/pages"]: path.join(projectPath, "pages", "_index.js"),
      ["@wp/components"]: path.join(projectPath, "pages", "components", "_index.js"),
      ["@wp/js"]: path.join(projectPath, "js"),
      ["@wp/css"]: path.join(projectPath, "css"),
      ["@wp/assets"]: path.join(projectPath, "assets"),
      ["@wp/api"]: path.join(projectPath, "api", "_index.js"),
      ["@wp/utils"]: path.join(projectPath, "utils", "_index.js"),
    }
  }
}

module.exports = webpackConfig;
