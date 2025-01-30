const webpack = require("webpack");
const fs = require("fs");
const del = require("del");
const path = require("path");
const config = require("config");
const glob = require("glob-all");
const BundleAnalyzerPlugin = require("webpack-bundle-analyzer").BundleAnalyzerPlugin;

const TerserPlugin = require("terser-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { PurgeCSSPlugin } = require("purgecss-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const { getIfUtils, removeEmpty } = require("webpack-config-utils");
const { ifProduction, ifNotProduction } = getIfUtils(process.argv[3]);
const basicAuth = require("express-basic-auth");

// path variables
const root = path.resolve(__dirname, "../");
const src = path.resolve(root, "./src");
const flask_app = path.resolve(root, "./flask_app");
const public_html = path.resolve(root, "./public_html");
const assets = path.resolve(public_html, "assets");
const img = path.resolve(assets, "img");
const audio = path.resolve(assets, "audio");
const templates = path.resolve(flask_app, "templates");
const includes = path.resolve(templates, "includes");
const assetsFile = `${includes}/assets.inc`;
const footerAssetsFile = `${includes}/footer_assets.inc`;

// delete prior webpack assets in the public path's /assets/ before webpack starts processing
del.sync([path.resolve(assets, "*.(js|br|css|gif|gz|svg|json|LICENSE|txt|map)")]);

module.exports = (env, argv) => {
  // console.log("ENVIRONMENT: " + process.env.ENV);
  // console.log(config);

  const devMode = argv.mode !== "production";
  const environment = argv.mode;
  return {
    context: root,
    devtool: "source-map",
    entry: {
      //  webpack's starting point
      app: "./src/index.js",
    },
    output: {
      // where the output files are deposited post-processing
      path: assets,
      filename: devMode ? "[name].js" : "[name].[fullhash].js", // do not use fingerprinting in dev mode, it screws up dev server
      publicPath: "/assets/",
    },
    resolve: {
      // where webpack is going to look for imported modules when it starts processing the entry files
      modules: ["node_modules", "src"],
      extensions: ["*", ".js"],
    },
    devServer: {
      devMiddleware: {
        publicPath: "/assets/",
        writeToDisk: true, // apparently HtmlWebpackPlugin doesn't actually write the assets html file if false
      },
      setupMiddlewares: (middlewares, devServer) => {
        devServer.app.use((req, res, next) => {
          if (req.path === "/app/subscription-webhook") {
            return next();
          }
          basicAuth({
            users: { misc: "misc" }, // Replace with your username/password
            challenge: true,
          })(req, res, next);
        });

        return middlewares;
      },
      client: {
        overlay: false,
        progress: false,
        webSocketURL: {
          hostname: process.env.SERVER_HOST,
          port: 443, // Secure WebSocket port
          protocol: "wss", // Use secure WebSocket protocol
          pathname: "/ws", // Optional: WebSocket path
        },
      },
      headers: {
        "Access-Control-Allow-Origin": "*", // Allow all origins for testing
      },
      static: false,
      watchFiles: {
        paths: [src, templates, `${flask_app}/**/*.py`],
        options: {},
      },
      host: process.env.RUN_HOST,
      allowedHosts: "all",
      hot: true,
      port: process.env.DEVSERVER_PORT,
      proxy: [
        {
          context: ["**", "!/assets/**"],
          target: `http://${process.env.WEB_HOST}`,
          secure: false,
          changeOrigin: true,
        },
      ],
      server: {
        type: "https",
        options: {
          key: path.resolve(root, "dev-ssl/privkey.pem"),
          cert: path.resolve(root, "dev-ssl/fullchain.pem"),
        },
      },
    },
    module: {
      // "loaders" process entry file and dependencies
      rules: [
        {
          test: /\.js$/,
          exclude: /(node_modules)/,
          use: {
            loader: "babel-loader",
            options: {
              cacheDirectory: true,
              presets: ["@babel/preset-env"],
              plugins: [
                "@babel/plugin-proposal-class-properties",
                "@babel/plugin-syntax-dynamic-import",
                "@babel/plugin-transform-template-literals",
                "@babel/plugin-transform-runtime",
              ],
            },
          },
        },
        {
          test: /\.(sa|sc|c)ss$/,
          use: [
            // MiniCssExtractPlugin extracts all the css from the JS and puts it in a single bundled file
            {
              loader: MiniCssExtractPlugin.loader,
              options: {
                esModule: false,
              },
            },
            {
              // This loader resolves url() and @imports inside CSS
              loader: "css-loader",
              options: {
                sourceMap: ifNotProduction(),
              },
            },
            {
              // Run postcss actions
              loader: "postcss-loader",
              options: {
                // `postcssOptions` is needed for postcss 8.x;
                // if you use postcss 7.x skip the key
                postcssOptions: {
                  // postcss plugins, can be exported to postcss.config.js
                  plugins: function () {
                    return [require("autoprefixer")];
                  },
                },
              },
            },
            {
              // transform SASS to standard CSS
              loader: "sass-loader",
              options: {
                implementation: require("sass"),
                sourceMap: ifNotProduction(),
              },
            },
          ],
        },
        // handles images
        {
          test: /\.(gif|jpg|png|jpeg|ico)$/, // notably, svg is missing.  I don't know why but when added it causes the svg to be empty
          type: "asset/resource",
          generator: {
            filename: "img/[name][ext]",
          },
        },
        {
          // handles any fonts in /src
          test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
          exclude: ["/img/", "/assets/img/", `${assets}/img/`], // this is because svg can be both fonts and images.  Don't process svg images as fonts
          type: "asset/resource",
          generator: {
            filename: "fonts/[name][ext]",
          },
        },
      ],
    },
    optimization: {
      minimize: !devMode,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            output: {
              comments: false,
            },
          },
          extractComments: false,
        }),
      ],
    },
    plugins: removeEmpty([
      // new BundleAnalyzerPlugin(),
      ifProduction(
        // analyzes the files matching the pattern, and REMOVES any css from the main css chunk that is
        // NOT used in the code.  Have to be careful with this because it can create issues where some styles
        // don't work in production.  i.e. if a style is added via javascript and it's not on the whitelist
        new PurgeCSSPlugin({
          paths: glob.sync(["./src/**/*", `${templates}/**/*.{j2,html,inc}`], { nodir: true }),
          safelist: {
            standard: [
              /data-v-.*/,
              /^btn-/,
              /modal/,
              /autosuggest/,
              /autocomplete/,
              /alert/,
              /fade/,
              /valid/,
              /spinner/,
              /carousel/,
              /account/,
              /tooltip/,
              /main/,
              /^fa-/,
              /icon/,
              /^alert/,
              /fadeIn/,
              /fadeOut/,
              /glide/,
              /fancybox/,
              /ms-fullscreen/,
              /bcFloat/,
              /triangle/,
              /blue-link/,
              /root/,
              /^filter/,
              /^item-count/,
              /^search/,
              /^facet/,
              /^grid/,
              /^hierarchy/,
              /^ss-/,
              /^list-/,
              /^clear-filters/,
              /^negative-margin/,
              /slideout/,
              /slick/,
              /certona/,
              /product__/,
              /products-/,
              /facets-/,
              /treeview/,
              /^ss-/,
              /bcText/,
              /vertical-products/,
              /cart-/,
              /avg-score/,
              /bottom-line/,
              /^badge/,
              /.*ss-autocomplete.*/,
              /video/,
              /ss-*/,
              /ss_*/,
              /top-panel/,
              /selects-wrapper/,
              /pagination*/,
              /data-desktop-visible/,
              /data-level/,
              /data-page-path/,
              /addbtn-divider/,
              /product-buttons/,
              /product-wrapper/,
              /cloudzoom-blank/,
              /style/,
              /mobile-minicart/,
              /mobile-popcart/,
              /^sticky/,
              /total-line/,
              /summary-/,
              /vertical-carousel/,
              /pdp-carousel-container/,
              /uwy/,
              /select-options-reminder/,
              /product-title/,
              /H2/,
              /shk*/,
              /img-overlay-wrap/,
              /progress/,
              /pie/,
              /hourglasss/,
              /shk/,
              /shikwasa/,
              /shk-*/,
              /podcast-*/,
              /podcast/,
              /data-value/,
              /data-theme/,
              /player/,
              /data-fixed-type/,
              /data-bs-popper/,
            ],
            deep: [
              /^shk/, // Matches all classes starting with "shk"
            ],
            verbose: true,
          },
        })
      ),
      // important.  extracts all css from the main JS bundle into a single file
      new MiniCssExtractPlugin({
        filename: devMode ? "[name].css" : "[name].[fullhash].css",
      }),
      // exposes config variables globally to the application as `CFG`
      new webpack.DefinePlugin({
        CFG: JSON.stringify(config),
      }),
      ifProduction(
        // pre-compresses css/js chunks with gzip and adds a .gz extension.  Needs to be config'd with prof webserver too
        new CompressionPlugin({
          filename: "[path][base].gz[query]",
          algorithm: "gzip",
          test: /\.(js|css|svg)$/,
          compressionOptions: { level: 9 },
          threshold: 5000,
          minRatio: 0.8,
          deleteOriginalAssets: false,
        })
      ),
      ifProduction(
        // pre-compresses css/js chunks with brotli and adds a .br extension.  Needs to be config'd with prof webserver too
        new CompressionPlugin({
          filename: "[path][base].br[query]",
          algorithm: "brotliCompress",
          test: /\.(js|css|svg)$/,
          compressionOptions: { level: 11 },
          threshold: 5000,
          minRatio: 0.8,
          deleteOriginalAssets: false,
        })
      ),
      // literally just copies non-webpack assets to public path
      new CopyWebpackPlugin({
        patterns: [{ from: "src/audio", to: audio }],
      }),
      new CopyWebpackPlugin({
        patterns: [
          { from: "src/img", to: "../assets/img" },
          { from: "node_modules/bootstrap-icons/font/fonts", to: "../assets/css/fonts" },
          { from: "node_modules/@fortawesome/fontawesome-free/webfonts", to: "../assets/webfonts" },
        ],
      }),
      // custom "plugin" for preloading assets
      {
        apply(compiler) {
          compiler.hooks.afterEmit.tap("Custom Chunk Processor", (compilation) => {
            // if assets files do not exist, create them
            try {
              fs.writeFileSync(assetsFile, "", { flag: "wx" }, function (err) {
                if (err) console.log("assets file doesn't exist, creating");
              });
              fs.writeFileSync(footerAssetsFile, "", { flag: "wx" }, function (err) {
                if (err) console.log("assets file doesn't exist, creating");
              });
            } catch (e) {
              console.log("assets files exist");
            }

            let headerAssets = fs.readFileSync(assetsFile, "utf8");
            let footerAssets = fs.readFileSync(footerAssetsFile, "utf8");
            headerAssets = "\n";
            footerAssets = "\n";

            compilation.chunks.forEach((chunk) => {
              //console.log("CHUNK", chunk);
              chunk.files.forEach((filename) => {
                console.log("CHUNKFILE", `${filename}`);
                if (/^app\./.test(filename)) {
                  if (/\.css/.test(filename)) {
                    headerAssets += `<link href="/assets/${filename}" rel="stylesheet">\n`;
                    //headerAssets += `<style><hazel-slurp src="/assets/${filename}"></style>\n`;
                  } else {
                    headerAssets += `<script type="application/javascript" src="/assets/${filename}" defer></script>\n`;
                  }
                } else {
                  // set hints to prefetch everything else, and put them in the footer
                  footerAssets += `<link href="/assets/${filename}" rel="prefetch">\n`;
                }
              });
            });
            //console.log(headerAssets);
            let pattern = "</?head>";
            let re = new RegExp(pattern, "gi");
            headerAssets = headerAssets.replace(re, ""); // something is (was?) adding <head> tags to my include
            fs.writeFileSync(assetsFile, headerAssets);
            fs.writeFileSync(footerAssetsFile, footerAssets);
          });
        },
      },
    ]),
  };
};
