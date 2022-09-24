import { Component, tags } from "@odoo/owl";

const APP_TEMPLATE = tags.xml/*xml*/ `
<main t-name="App" class="" t-on-click="update">
  <h1>My OWL App</h1>
</main>
`;

export class App extends Component {
  static template = APP_TEMPLATE;
}