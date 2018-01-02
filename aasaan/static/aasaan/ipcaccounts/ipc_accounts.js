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

         $(document).ready(function () {

            if($('#id_transactionnotes_set-TOTAL_FORMS').val()==0){
                $('#transactionnotes_set-group').hide()
            }
         })

        if($("#id_account_type").find('option')[0].value=='')
            $("#id_account_type").find('option')[0].remove()
        if($("#id_entity_name").find('option')[0].value=='')
            $("#id_entity_name").find('option')[0].remove()

        if (document.URL.endsWith('/change/')) {
            $('.field-tracking_no').show()
            $('.field-tracking_no').find('input').prop("readonly", true);
            var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())
            for (var i=0; i<no_of_item; i++){
                $($('.field-copy_voucher')[i]).hide()
            }
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
        $('.form-row.field-np_voucher_status.field-finance_submission_date.field-movement_sheet_no').hide()
        $('.form-row.field-payment_date.field-utr_no.field-amount_after_tds').hide()
        });



        django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
            if(formsetName == 'voucherdetails_set'){
               $($row.find('.field-tracking_no')).hide()
               $('#id_voucherdetails_set-0-copy_voucher').parent().parent().hide()
               var line_no = $row.find('.inline_label').html()
               line_no = line_no.split('#')
               if(line_no[1] == 1){

               }
               else if(line_no[1] > 1){
                $($('.checkbox-row').find('input')[line_no[1]-1]).change(function () {
                if($(this).is(":checked")){
                    var id = $(this).parent().parent().parent().parent().attr('id')
                    var vid = id.split('-')[1]
                    if(vid >=1){
                        $('#id_voucherdetails_set-'+vid+'-nature_of_voucher').val($('#id_voucherdetails_set-'+(vid-1)+'-nature_of_voucher').val())
                        $('#id_voucherdetails_set-'+vid+'-voucher_status').val($('#id_voucherdetails_set-'+(vid-1)+'-voucher_status').val())
                        $('#id_voucherdetails_set-'+vid+'-voucher_date').val($('#id_voucherdetails_set-'+(vid-1)+'-voucher_date').val())
                        var account_type = $("#id_account_type").val()
                        if(account_type == 'OA'){
                            $('#id_voucherdetails_set-'+vid+'-oa_head_of_expenses').val($('#id_voucherdetails_set-'+(vid-1)+'-oa_head_of_expenses').val())
                            $('#id_voucherdetails_set-'+vid+'-party_name').val($('#id_voucherdetails_set-'+(vid-1)+'-party_name').val())
                        }
                        if(account_type == 'CA'){
                            $('#id_voucherdetails_set-'+vid+'-ca_head_of_expenses').val($('#id_voucherdetails_set-'+(vid-1)+'-ca_head_of_expenses').val())
                            $('#id_voucherdetails_set-'+vid+'-party_name').val($('#id_voucherdetails_set-'+(vid-1)+'-party_name').val())
                        }
                        if(account_type == 'TA'){
                            $('#id_voucherdetails_set-'+vid+'-ta_head_of_expenses').val($('#id_voucherdetails_set-'+(vid-1)+'-ta_head_of_expenses').val())
                        }
                        $('#id_voucherdetails_set-'+vid+'-expenses_description').val($('#id_voucherdetails_set-'+(vid-1)+'-expenses_description').val())
                        $('#id_voucherdetails_set-'+vid+'-amount').val($('#id_voucherdetails_set-'+(vid-1)+'-amount').val())
                        $('#id_voucherdetails_set-'+vid+'-approval_sent_date').val($('#id_voucherdetails_set-'+(vid-1)+'-approval_sent_date').val())
                        $('#id_voucherdetails_set-'+vid+'-approved_date').val($('#id_voucherdetails_set-'+(vid-1)+'-approved_date').val())
                        $('#id_voucherdetails_set-'+vid+'-copy_voucher').parent().parent().hide()
                    }
                }
               });

               }


            }

    });
}

)(django.jQuery);