'use strict';

(function($) {

    $(document).ready(function() {
        $('.form-row.field-np_voucher_status.field-finance_submission_date.field-movement_sheet_no').parent().hide()
        toggleVerified();

        $("#id_account_type").change(function() {
            toggleVerified();
        })

        $("#id_account_type").click(function () {
             $("#id_budget_code").val('')
             $("#id_program_schedule").val('')
        });

        $("#id_program_schedule").click(function() {
            if($(this).val()==''){
                $("#id_budget_code").val('')
                return
            }
             $.ajax({
                    type: 'GET',
                    url: '/admin/ipcaccounts/get_budget_code/',
                    data: {
                            'program_schedule': $(this).val()
                            },
                    contentType: 'application/json; charset=utf-8',
                    cache: false,
                    success: function(data) {
                       $("#id_budget_code").val(data)
                    }
                });
        })

        //hide one transaction set for new voucher
        if($('#id_transactionnotes_set-TOTAL_FORMS').val()==0){
            $('#transactionnotes_set-group').hide()
        }

        //Hide Tracking Number for new vouchers
        $('.form-row.field-tracking_no.field-voucher_type.field-nature_of_voucher').show()
        if (document.URL.indexOf('change')>-1){
            $('.field-tracking_no').show()
            $('.field-tracking_no').find('input').prop("readonly", true);
        }
        else{
            $('.field-tracking_no').hide()
            $('.field-tracking_no').find('input').prop("readonly", false);
        }

        django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
            if(formsetName == 'voucherdetails_set'){
                $($row.find('.field-tracking_no')).hide()
                 $('.form-row.field-tracking_no.field-voucher_type.field-nature_of_voucher').show()
            }
        });

        //Show Head Of Expenses options based on account type selection
        $("#id_account_type").change(function () {
            var hoe = $('.field-box.field-head_of_expenses').find('select')
            var options = $('#id_account_type option');
            for (var i = 0;i<options.length;i++){
                if(options[i].selected)
                    $(hoe).children("optgroup[label='"+options[i].text+"']").show();
                else
                    $(hoe).children("optgroup[label='"+options[i].text+"']").hide();
            }

        });

        if(document.URL.indexOf('npaccountsmaster')>-1){
            $('.form-row.field-np_voucher_status.field-finance_submission_date.field-movement_sheet_no').parent().show()
            var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())
            for (var i=0; i<=no_of_item-1; i++){
                $('#id_voucherdetails_set-'+i+'-nature_of_voucher').change(function () {
                    if($(this).find('option:selected').text()!='Expenses'){
                        $(this).parent().parent().parent().parent().parent().find('.form-row.field-payment_date.field-utr_no.field-tds_amount').show()
                    }
                    else{
                        $(this).parent().parent().parent().parent().parent().find('.form-row.field-payment_date.field-utr_no.field-tds_amount').hide()
                    }
                });
            }
        }
        else{
            $('.form-row.field-payment_date.field-utr_no.field-tds_amount').hide()
        }


    });

    function toggleVerified() {
        if($("#id_account_type option:selected").text()=='Teacher Accounts'){
            $('.field-program_schedule').hide()
            $('.field-zone').show()
            $('.field-budget_code').show()
            $('.field-teacher').show()
            $('.field-box.field-party_name').hide()
        }
        else if($("#id_account_type option:selected").text()=='Class Accounts'){
            $('.field-teacher').hide()
            $('.field-program_schedule').show()
            $('.field-zone').hide()
            $('.field-budget_code').show()
        }
        else {
            $('.field-teacher').hide()
            $('.field-program_schedule').hide()
            $('.field-zone').show()
            $('.field-budget_code').show()
            $('.field-box.field-party_name').show()
        }
    }
}

)(django.jQuery);