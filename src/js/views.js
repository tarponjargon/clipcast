/*

this is how code splitting is achieved when routes are handled on the server.
You add a block for each route (tho you can use any condition, like
existence of a DOM element), and it will dynamically load the corresponding
module.  the webpackPrefetch magic comments handle adding
the "prefetch" resource hints to the DOM, so it should lazily cache the entire
app on the first load

webpackChunkName magic comments are not required, I use them so I can easily see and
understand the chunk sizes in the outputted files.  Uncommenting BundleAnalyzerPlugin lines
in the webpack config and doing 'npm run build' is also a good way to visualize

Note I use multiple "if" rather than switch or else if, because it allows for multiple views
to be loaded on a single page.

*/

const views = async () => {
  const pathname = window.location.pathname;

  if (pathname.startsWith("/app")) {
    const mod = await import(
      /* webpackChunkName: "dashboard" */
      "./views/ClipCast"
    );
    await new mod.default().init();
  }

  // if (pathname === "/") {
  //   const mod = await import(
  //     /* webpackChunkName: "home" */
  //     "./views/Home"
  //   );
  //   await new mod.default().init();
  // }

  // if (pathname === "/signup") {
  //   const mod = await import(
  //     /* webpackChunkName: "signup" */
  //     "./views/Signup"
  //   );
  //   await new mod.default().init();
  // }

  // if (pathname === "/login") {
  //   const mod = await import(
  //     /* webpackChunkName: "login" */
  //     "./views/Login"
  //   );
  //   await new mod.default().init();
  // }

  // if (pathname === "/contact") {
  //   const mod = await import(
  //     /* webpackChunkName: "contactform" */
  //     "./views/Contact"
  //   );
  //   await new mod.default().init();
  // }

  // if (pathname === "/unsubscribe") {
  //   const mod = await import(
  //     /* webpackChunkName: "unsubscribe" */
  //     "./views/Unsubscribe"
  //   );
  //   await new mod.default().init();
  // }

  // if (pathname === "/forgotpassword") {
  //   const mod = await import(
  //     /* webpackChunkName: "forgotpassword" */
  //     "./views/ForgotPassword"
  //   );
  //   await new mod.default().init();
  // }

  // if (pathname === "/resetpassword") {
  //   const mod = await import(
  //     /* webpackChunkName: "resetpassword" */
  //     "./views/ResetPassword"
  //   );
  //   await new mod.default().init();
  // }

  // if (document.querySelector('[data-js="subscribe-form"]')) {
  //   const mod = await import(
  //     /* webpackChunkName: "subscribe" */
  //     "./views/Subscribe"
  //   );
  //   await new mod.default().init();
  // }
};
export default views;
