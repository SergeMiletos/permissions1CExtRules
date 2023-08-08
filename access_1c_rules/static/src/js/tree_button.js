odoo.define('access_1c_rules.tree_button', function (require) {
"use strict";

let ListController = require('web.ListController');
let ListView = require('web.ListView');
let viewRegistry = require('web.view_registry');
let rpc = require('web.rpc');
let core = require('web.core');

let TreeButton = ListController.extend({
   buttons_template: 'button_near_create.buttons',
   events: _.extend({}, ListController.prototype.events, {
       'click .open_wizard_action': '_OpenWizard',
   }),

   _OpenWizard: function () {
        let self = this;
        let res;
        rpc.query({
            model: 'acs1crules.usr1crules',
            method: 'buttReport',
            args: [[]],
            }).then(function (res) {
//                console.log("Success");
                self.do_action(res);
    });
    },
    });  

let acs1crulesListView = ListView.extend({
   config: _.extend({}, ListView.prototype.config, {
       Controller: TreeButton,
   }),
});
viewRegistry.add('button_in_tree_new', acs1crulesListView);
});