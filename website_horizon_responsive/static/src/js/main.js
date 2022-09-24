import { App } from "./app";
import { utils } from "owl";

(async () => {
  const app = new App();
  await utils.whenReady();
  await app.mount(document.body);
})();