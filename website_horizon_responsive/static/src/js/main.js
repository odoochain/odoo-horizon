import { App } from "./App";

const { utils } = owl;

(async () => {
  const app = new App();
  await utils.whenReady();
  await app.mount(document.body);
})();