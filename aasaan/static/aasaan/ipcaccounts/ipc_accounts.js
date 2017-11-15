'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;


(function($) {

    $(function() {
        $('#id_tracking_no').prop("readonly", true);
        if($("#id_account_type").find('option')[0].value=='')
            $("#id_account_type").find('option')[0].remove()
        if($("#id_entity_name").find('option')[0].value=='')
            $("#id_entity_name").find('option')[0].remove()
        if($("#id_voucher_status").find('option')[0].value=='')
            $("#id_voucher_status").find('option')[0].remove()
        if($("#id_nature_of_voucher").find('option')[0].value=='')
            $("#id_nature_of_voucher").find('option')[0].remove()

        if ($('#id_voucher_date').val()!=''){
            $("#id_account_type").prop("disabled", true);
        }

        $("form").submit(function( event ) {
            $("#id_account_type").prop("disabled", false);
        });

        if($("#id_account_type").val()=='CLASS'){
                $('.field-teacher').hide()
                $('.field-head_of_expenses').hide()
                $('.field-program_schedule').show()
                $('.field-center').show()
                $('.field-budget_code').show()
                $('.field-party_name').show()
        }
        toggleVerified($("#id_account_type").val())

        $("#id_account_type").change(function() {
            toggleVerified($(this).val());
        })
        function toggleVerified(value) {
            if($("#id_account_type").val()=='TEACH'){
                $('.field-program_schedule').hide()
                $('.field-center').hide()
                $('.field-budget_code').hide()
                $('.field-party_name').hide()
                $('.field-teacher').show()
                $('.field-head_of_expenses').show()
            }
            else if($("#id_account_type").val()=='CLASS'){
                $('.field-teacher').hide()
                $('.field-head_of_expenses').hide()
                $('.field-program_schedule').show()
                $('.field-center').show()
                $('.field-budget_code').show()
                $('.field-party_name').show()
            }
            else {
                $('.field-teacher').hide()
                $('.field-head_of_expenses').hide()
                $('.field-program_schedule').hide()
                $('.field-center').show()
                $('.field-budget_code').show()
                $('.field-party_name').show()
            }
        }
    });
}

)(django.jQuery);