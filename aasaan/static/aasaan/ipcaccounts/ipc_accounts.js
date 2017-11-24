'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;


(function($) {

    $(function() {

        if($("#id_account_type").find('option')[0].value=='')
            $("#id_account_type").find('option')[0].remove()
        if($("#id_entity_name").find('option')[0].value=='')
            $("#id_entity_name").find('option')[0].remove()


        if($("#id_account_type").val()=='CA'){
            $('.field-teacher').hide()
            $('.field-program_schedule').show()
            $('.field-center').show()
            $('.field-budget_code').show()
            $('.field-ca_head_of_expenses').show()
            $('.field-ta_head_of_expenses').hide()
            $('.field-party_name').show()
        }
        toggleVerified($("#id_account_type").val())

        $("#id_account_type").change(function() {
            toggleVerified($(this).val());
        })

        function toggleVerified(value) {
            if($("#id_account_type").val()=='TA'){
                $('.field-program_schedule').hide()
                $('.field-center').hide()
                $('.field-budget_code').hide()
                $('.field-teacher').show()
                $('.field-ca_head_of_expenses').hide()
                $('.field-ta_head_of_expenses').show()
                $('.field-party_name').hide()
            }
            else if($("#id_account_type").val()=='CA'){
                $('.field-teacher').hide()
                $('.field-program_schedule').show()
                $('.field-center').show()
                $('.field-budget_code').show()
                $('.field-ca_head_of_expenses').show()
                $('.field-ta_head_of_expenses').hide()
                $('.field-party_name').show()
            }
            else {
                $('.field-teacher').hide()
                $('.field-program_schedule').hide()
                $('.field-center').hide()
                $('.field-budget_code').show()
                $('.field-ca_head_of_expenses').show()
                $('.field-ta_head_of_expenses').hide()
                $('.field-party_name').show()
            }
        }

        function validateVoucherInline(){
            var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())
            var item_array = [];
            for (var i=0; i<no_of_item; i++){
                $('.field-ca_head_of_expenses').hide()
            }
        }
    });
}

)(django.jQuery);