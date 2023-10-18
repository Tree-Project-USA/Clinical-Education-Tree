odoo.define('website_base.location_student', function(require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    publicWidget.registry.generic_form_data = publicWidget.Widget.extend({
        selector: '#form_template',
        events: {
            'click .add_total_project': '_onClickAdd_total_project',
            'click .remove_line': '_onClickRemove_line',
            'click .custom_create': '_onClickSubmit',
            'change input[name="zip"]': "_onZipCodeChanges",
        },
        _onZipCodeChanges: function() {
            var self = this
            var zip = $('.total_project_costs > tbody > tr.project_cost_line div > input[name="zip"]');
            var State = $('.total_project_costs > tbody > tr.project_cost_line div > input[name="state"]');
            var City = $('.total_project_costs > tbody > tr.project_cost_line div > input[name="city"]');
            var zip_code_error = $('.zip_code_error');
            var bk_loader = $('#bk_n_res_loader');
            _.each(zip, function(value, index) {
                    zip[index].onblur = function() {
                        if (this.value) {
                            bk_loader.show();
                            self._rpc({
                                model: 'location.setting',
                                method: 'get_locstion_infor',
                                args: [, this.value]
                            }).then(function(data) {
                                if (data) {
                                    State[index].value = data['state']
                                    City[index].value = data['city']
                                } else {
                                    // zip[index].value = ''
                                    // zip_code_error.html('ooooooooooo').show();
                                    // setTimeout(function() {
                                    //     zip_code_error.empty().hide()
                                    // }, 6000);
                                }
                                bk_loader.hide();

                            })
                        }
                    }
                })
        },
        _onClickSubmit: async function(ev) {
            var self = this;
            var locations_data = [];
            var rows = $('.total_project_costs > tbody > tr.project_cost_line');
            _.each(rows, function(row) {
                let state = $(row).find('input[name="state"]').val();
                let city = $(row).find('input[name="city"]').val();
                let zip = $(row).find('input[name="zip"]').val();
                locations_data.push({
                    'state': state,
                    'city': city,
                    'zip': zip,
                });
            });
            $('textarea[name="data_line_ids"]').val(JSON.stringify(locations_data));

        },

        _onClickRemove_line: function(ev) {
            var el = $(ev.target);
            el.closest('tr').remove();
        },

        _onClickAdd_total_project: function(ev) {
            var $new_row = $('.add_extra_project').clone(true);
            $new_row.removeClass('d-none');
            $new_row.removeClass('add_extra_project');
            $new_row.addClass('project_cost_line');
            $new_row.insertBefore($('.add_extra_project'));
            _.each($new_row.find('td'), function(val) {
                $(val).find('input').attr('required', 'required');
            });
        },

    });
});