odoo.define("website_base.departments", function(require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

    publicWidget.registry.Departments = publicWidget.Widget.extend({
        selector: ".availability",
        events: {
            // 'click #add_departments': '_onClickDepartment',
            // 'input .number': '_onInputNumber',
            'change #company_id': '_onChangeCompany',
            'change #year_term, #placement_term': '_onChangeYearTerm',
            'click #submit-offers, #placement_term': '_onClickSubmitOffers',
        },

        /**
         * @class
         */
        init: function() {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
            // this._onClickDepartment();
        },

        start: function () {
            this.$(".custom-select").select2();
            $('.availability').removeClass('d-none')
            $('.loading-indicator').addClass('d-none')
        },

        _onChangeCompany: function(ev) {
            var CompanyId = $("#company_id").val()
            var TableBody = $("#table_body")
            var LineDepartment = 1
            ajax.jsonRpc("/inforamtion/company", 'call', { 'company_id': CompanyId }).then(function(data) {
                $(TableBody).empty();
                var LineDepartmentList = []
                _.each(data["department_ids"], function(value){
                    console.log(value,'value')
                    const row = `<tr value="${value.id}">
                                    <td>${value.name}</td>
                                    <td>${value.street}</td>
                                    <td>${value.city}</td>
                                    <td>${value.state}</td>
                                    <td>
                                        <input
                                            type="text"
                                            id="number_${LineDepartment}"
                                            class="form-control number"
                                            name="number_${LineDepartment}"
                                            required="required"
                                            value=""
                                        />
                                    </td>
                                </tr>`;
                    $(TableBody).append(row);
                    LineDepartmentList.push(value.id)
                    $('input[name="line_department_list"]').attr('value', LineDepartmentList)
                    LineDepartment ++
                })
            })
        },
        _onChangeYearTerm: function(ev) {
            var YearTerm = $("#year_term").val()
            var PlacementTerm = $("#placement_term").val()
            if(PlacementTerm && YearTerm){
                
                ajax.jsonRpc("/clinical/experience/dates", 'call', {
                    "year_term" :  YearTerm,
                    "placement_term" :  PlacementTerm
                }).then(function(result) {
                    $("#experience_id").empty();
                    $("#select2-chosen-3").html("<span>Select ...</span>");
                    $("#experience_id").html("<option>Select ...</option>");
                    var cont_ce = 0
                    _.each(result["clinical_experience_ids"], function(value){
                        const startDate = new Date(value.start_date);
                        const endDate = new Date(value.end_date);
                        const startDateString = startDate.toLocaleDateString('en', { month: 'long', day: 'numeric', year: 'numeric' });
                        const endDateString = endDate.toLocaleDateString('en', { month: 'long', day: 'numeric', year: 'numeric' });
                        // console.log(value.indexOf(), '<<<<<<<result')
                       
                        $("#experience_id").append($('<option>', {
                            value: value.term + '_' + value.id ,
                            text: value.name + ' [ ' +startDateString +' - '+ endDateString + ' ]',
                        }));
                        cont_ce ++
                    });
                })
            }
        },
          /**
         * @private
         * @override
         * @param {event} ev
         */
          _onClickSubmitOffers: function (ev) { 
            if(!this.el.checkValidity()){
                this.el.classList.add('was-validated');
            }else{
                var PlacementTerm = $("#placement_term").val()
                var ExperienceID = $("#experience_id").val()
                $('input[name="placement_term_list"]').attr('value', PlacementTerm)
                $('input[name="experience_id_list"]').attr('value', ExperienceID)
                this.el.submit()
            }
            
        },
    })

})