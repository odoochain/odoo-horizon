/** @odoo-module **/

const { Component, tags, hooks } = owl;

import {
    makeLegacyCrashManagerService,
    makeLegacyDialogMappingService,
    makeLegacyNotificationService,
    makeLegacyRpcService,
    makeLegacySessionService,
    mapLegacyEnvToWowlEnv,
} from '@web/legacy/utils';
import * as legacySession from 'web.session';

owl.Component.env = legacyEnv;

const APP_TEMPLATE = tags.xml/*xml*/ `
<main t-name="App" class="" t-on-click="update">
  <h1>My OWL App</h1>
</main>
`;

export class App extends Component {
  static template = APP_TEMPLATE;
}