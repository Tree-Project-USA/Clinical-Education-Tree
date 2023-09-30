odoo.define('website_base.location_student', function(require){
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
   	},

   	_onClickSubmit: async function(ev){
        	var self = this;
        	var locations_data = [];
        	var rows = $('.total_project_costs > tbody > tr.project_cost_line');
        	_.each(rows, function(row) {
            	let state_id = $(row).find('select[name="state_id"]').val();
            	let city_id = $(row).find('select[name="city_id"]').val();
            	let zip = $(row).find('input[name="zip"]').val();
            	console.log(state_id, city_id, zip)
            	locations_data.push({
                	'state_id': state_id,
                	'city_id': city_id,
                	'zip': zip,
            	});
        	});
        	$('textarea[name="data_line_ids"]').val(JSON.stringify(locations_data));

   	},

   	_onClickRemove_line: function(ev){
		var el = $(ev.target);
		el.closest('tr').remove();
    	},

   	_onClickAdd_total_project: function(ev){
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