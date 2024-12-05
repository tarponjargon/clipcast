export default class Home {
  constructor() {}

  init = () => {
    return new Promise((resolve, reject) => {
      resolve("Home controller loaded");
    });
  };
}
