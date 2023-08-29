/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

import { DeliberationController } from "./deliberation_controller.esm";
import { DeliberationRenderer } from "./deliberation_renderer.esm";
import { DeliberationModel } from "./deliberation_model.esm";

const viewRegistry = registry.category("views");

export const deliberationView = {
    type: "deliberation",
    display_name: _lt("Deliberation"),
    icon: "fa-pagelines",
    multiRecord: false,
    Controller: DeliberationController,
    Renderer: DeliberationRenderer,
    Model: DeliberationModel,
    //ArchParser: GraphArchParser,
    //SearchModel: GraphSearchModel,
    
    withControlPanel: false,
    groupable: false,
    
    props: (genericProps, view) => {
        return {
            ...genericProps,
            Renderer: view.Renderer,
            Model: view.Model,
        };
    }
};
    
viewRegistry.add("deliberation", deliberationView);