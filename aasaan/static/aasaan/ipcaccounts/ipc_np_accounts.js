'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;


(function($) {

    $(function() {

        function strStartsWith(str, prefix) {
            return str.indexOf(prefix) === 0;
        }

        var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())
        if(no_of_item >0){
            $($('.field-copy_voucher')[0]).hide()
        }

        for (var i=1; i<no_of_item; i++){
            if($($('.field-tracking_no').find('input')).val() !='')
                $($('.field-copy_voucher')[i]).hide()
        }
        if($('#id_transactionnotes_set-TOTAL_FORMS').val()==0){
            $('#transactionnotes_set-group').hide()
        }



        if($("#id_account_type").find('option')[0].value=='')
            $("#id_account_type").find('option')[0].remove()
        if($("#id_entity_name").find('option')[0].value=='')
            $("#id_entity_name").find('option')[0].remove()

        if (document.URL.endsWith('/change/')) {
            $('.field-tracking_no').show()
            $('.field-tracking_no').find('input').prop("readonly", true);
        }
        else{
            $('.field-tracking_no').hide()
            $('.field-tracking_no').find('input').prop("readonly", false);
        }


        if($("#id_account_type").val()=='CA'){
            $('.field-teacher').hide()
            $('.field-program_schedule').show()
            $('.field-zone').hide()
            $('.field-budget_code').show()
            $('.field-ta_head_of_expenses.field-expenses_description.field-party_name').hide()
            $('.field-ca_head_of_expenses.field-expenses_description.field-party_name').show()
            $('.field-oa_head_of_expenses.field-expenses_description.field-party_name').hide()
        }
        $('#id_account_type option:not(:selected)').prop('disabled', true);
        $('#id_program_schedule option:not(:selected)').prop('disabled', true);
        $('#id_entity_name option:not(:selected)').prop('disabled', true);
        $('#id_budget_code').prop("readonly", true);
        toggleVerified($("#id_account_type").val())

        $("#id_account_type").change(function() {
            toggleVerified($(this).val());
        })

        function toggleVerified(value) {
            if($("#id_account_type").val()=='TA'){
                $('.field-program_schedule').hide()
                $('.field-zone').show()
                $('.field-budget_code').show()
                $('.field-teacher').show()
                $('.field-ta_head_of_expenses.field-expenses_description.field-party_name').show()
                $('.field-ca_head_of_expenses.field-expenses_description.field-party_name').hide()
                $('.field-oa_head_of_expenses.field-expenses_description.field-party_name').hide()
            }
            else if($("#id_account_type").val()=='CA'){
                $('.field-teacher').hide()
                $('.field-program_schedule').show()
                $('.field-zone').hide()
                $('.field-budget_code').show()
                $('.field-ta_head_of_expenses.field-expenses_description.field-party_name').hide()
                $('.field-ca_head_of_expenses.field-expenses_description.field-party_name').show()
                $('.field-oa_head_of_expenses.field-expenses_description.field-party_name').hide()
            }
            else {
                $('.field-teacher').hide()
                $('.field-program_schedule').hide()
                $('.field-zone').show()
                $('.field-budget_code').show()
                $('.field-ta_head_of_expenses.field-expenses_description.field-party_name').hide()
                $('.field-ca_head_of_expenses.field-expenses_description.field-party_name').hide()
                $('.field-oa_head_of_expenses.field-expenses_description.field-party_name').show()
            }
        }
    });

    django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
            if(formsetName == 'voucherdetails_set'){
               $($row.find('.field-tracking_no')).hide()
               $('#id_voucherdetails_set-0-copy_voucher').parent().parent().hide()
                $('.checkbox-row').find('input').change(function () {
                if($(this).is(":checked")){
                    var id = $(this).parent().parent().parent().parent().attr('id')
                    var vid = id.split('-')[1]
                    if(vid >=1){
                        $('#id_voucherdetails_set-'+vid+'-copy_voucher').parent().parent().hide()
                        $('#id_voucherdetails_set-'+vid+'-np_voucher_status').val($('#id_voucherdetails_set-'+(vid-1)+'-np_voucher_status').val())
                        $('#id_voucherdetails_set-'+vid+'-finance_submission_date').val($('#id_voucherdetails_set-'+(vid-1)+'-finance_submission_date').val())
                        $('#id_voucherdetails_set-'+vid+'-movement_sheet_no').val($('#id_voucherdetails_set-'+(vid-1)+'-movement_sheet_no').val())
                        $('#id_voucherdetails_set-'+vid+'-payment_date').val($('#id_voucherdetails_set-'+(vid-1)+'-payment_date').val())
                        $('#id_voucherdetails_set-'+vid+'-utr_no').val($('#id_voucherdetails_set-'+(vid-1)+'-utr_no').val())
                        $('#id_voucherdetails_set-'+vid+'-amount_after_tds').val($('#id_voucherdetails_set-'+(vid-1)+'-amount_after_tds').val())
                    }
                }
               });
            }

    });
}

)(django.jQuery);