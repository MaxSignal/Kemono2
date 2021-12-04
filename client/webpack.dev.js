// const FaviconsWebpackPlugin = require("favicons-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");
const { merge } = require("webpack-merge");

const baseConfig = require("./webpack.config");
const { ENV_VARS } = require("./configs/env-vars/_index.js");

const projectPath = path.resolve(__dirname, "src");

/**
 * @type {import("webpack-dev-server").Configuration}
 */
const devServer = {
  host: "0.0.0.0",
  port: 3450,
  writeToDisk: true,
  watchOptions: {
    poll: 500,
    aggregateTimeout: 500
  },
  contentBase: path.resolve(__dirname, "static"),
  watchContentBase: true,
  hot: false,
  liveReload: true,
  overlay: true
}

/**
 * @type import("webpack").Configuration
 */
const webpackConfigDev = {
  mode: "development",
  devtool: "eval-source-map",
  devServer: devServer,
  entry: {
    'development': path.join(projectPath, "development", "entry.js")
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "static/bundle/css/[name].css",
      chunkFilename: "static/bundle/css/[id].chunk.css"
    }),
    // new FaviconsWebpackPlugin({
    //   logo:"./src/assets/logo/kemono-logo.svg",
    //   inject: htmlPlugin => path.basename(htmlPlugin.options.filename) === "shell.html",
    //   prefix: "static/assets/logo"
    // })
  ],
  module: {
    rules: [
      {
        test: /\.s[ac]ss$/i,
        exclude: /\.module.s[ac]ss$/i,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
            }
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
              // TODO: find how to prepend data properly
              additionalData: `$kemono-site: '${ENV_VARS.SITE_ORIGIN}';`
            }
          }

        ],
      },
      {
        test: /\.(png|jpg|jpeg|gif|webp)$/i,
        type: 'asset/resource',
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
      {
        test: /\.svg$/i,
        type: 'asset/resource',
      }
    ]
  },
  output: {
    path: path.resolve(__dirname, "dev"),
    filename: "static/bundle/js/[name].bundle.js",
    assetModuleFilename: "static/bundle/assets/[name][ext][query]",
    publicPath: "/",
    clean: true,
  }
}

module.exports = merge(baseConfig, webpackConfigDev);
