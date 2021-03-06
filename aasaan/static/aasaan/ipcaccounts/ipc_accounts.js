'use strict';

(function($) {

    $(document).ready(function() {

        //logic to run on change list to send email
         $('.actions').find('button').click(function(event) {
            if($('.actions').find('select').val() == 'make_email'){
                var favorite = [];
                $.each($("input[name='_selected_action']:checked"), function(){
                    favorite.push($(this).val());
                });
                if(favorite.length==1){
                    document.getElementById('send_email').href = document.getElementById('send_email').href+'?account_id='+favorite.join(", ")
                    document.getElementById('send_email').click();
                }
                else if(favorite.length>1){
                    addErrorMessage('Only one item must be selected in order to perform actions on them.')
                    event.preventDefault()
                }
                else if(favorite.length==0){
                    addErrorMessage('One item must be selected in order to perform actions on them.')
                    event.preventDefault()
                }
            }
         })

         //Adds validation error message
        function addErrorMessage(message) {
            removeErrorMessage();
            $($('.breadcrumbs')[0]).after('<ul class="messagelist"><li class="warning">'+message+'</li></ul>');
//            custom_error = true
            return false;
        }

        //Removes all validation error message
        function removeErrorMessage() {
            $(".messagelist").remove();
        }

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
                    url: '/admin/ipcaccounts/get_budget_code',
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
        handle_hoe_select()
        //Show Head Of Expenses options based on account type selection
        $("#id_account_type").change(function () {
            handle_hoe_select()
        });

        function handle_hoe_select(){
            var hoe = $('.field-box.field-head_of_expenses').find('select')
            var options = $('#id_account_type option');
            for (var i = 0;i<options.length;i++){
                if(options[i].selected)
                    $(hoe).children("optgroup[label='"+options[i].text+"']").show();
                else
                    $(hoe).children("optgroup[label='"+options[i].text+"']").hide();
            }
        }

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

        $("#id_zone").click(function() {
        if($(this).val()=='' || $("#id_program_type").val()==''){
                return
            }
            refresh_Programs()
         });

         $("#id_program_type").click(function() {
            if($(this).val()=='' || $("#id_zone").val()==''){
                    return
                }
                refresh_Programs()

         });
    });

    function toggleVerified() {
        var account_type = $("#id_account_type option:selected").text()
        if(account_type == 'Teacher Accounts'){
            $('.field-program_schedule').hide()
            $('.form-row.field-program_type').hide()
            $('.field-budget_code').show()
            $('.field-teacher').show()
            $('.form-row.field-budget_code').find('label').html('Budget code:')
            if ($("#id_entity_name option:contains('Isha Foundation')").length ==0)
                $("#id_entity_name").append('<option value="2">Isha Foundation</option>');
            if($('.field-box.field-voucher_type').find('select option:contains("Cash Voucher")').length==0)
                $('.field-box.field-voucher_type').find('select').append('<option value="CV">Cash Voucher</option>');
            if($('.field-box.field-nature_of_voucher').find('select option:contains("Refund")').length==0)
                $('.field-box.field-nature_of_voucher').find('select').append('<option value="5">Refund</option>');
        }
        else if(account_type == 'Class Accounts'){
            $('.field-teacher').hide()
            $('.field-program_schedule').show()
            $('.form-row.field-program_type').show()
            $('.field-budget_code').show()
            $('.form-row.field-budget_code').find('label').html('Budget code:')
            if ($("#id_entity_name option:contains('Isha Foundation')").length ==0)
                $("#id_entity_name").append('<option value="2">Isha Foundation</option>');
            if($('.field-box.field-voucher_type').find('select option:contains("Cash Voucher")').length==0)
                $('.field-box.field-voucher_type').find('select').append('<option value="CV">Cash Voucher</option>');
            if($('.field-box.field-nature_of_voucher').find('select option:contains("Refund")').length==0)
                $('.field-box.field-nature_of_voucher').find('select').append('<option value="5">Refund</option>');
        }
        else if(account_type == 'Other Accounts' || account_type == 'RCO Accounts'){
            $('.field-teacher').hide()
            $('.field-program_schedule').hide()
            $('.form-row.field-program_type').hide()
            $('.field-budget_code').show()
            $('.form-row.field-budget_code').find('label').html('Budget code:')
            if ($("#id_entity_name option:contains('Isha Foundation')").length ==0)
                $("#id_entity_name").append('<option value="2">Isha Foundation</option>');
            if($('.field-box.field-voucher_type').find('select option:contains("Cash Voucher")').length==0)
                $('.field-box.field-voucher_type').find('select').append('<option value="CV">Cash Voucher</option>');
            if($('.field-box.field-nature_of_voucher').find('select option:contains("Refund")').length==0)
                $('.field-box.field-nature_of_voucher').find('select').append('<option value="5">Refund</option>');
        }
        else if(account_type == 'Fixed Asset'){
            $('.field-teacher').hide()
            $('.field-program_schedule').hide()
            $('.form-row.field-program_type').hide()
            $('.field-budget_code').show()
            $('.form-row.field-budget_code').find('label').html('Fixed Asset No:')
            $("#id_entity_name option:contains('Isha Foundation')").remove();
            $('.field-box.field-voucher_type').find('select option:contains("Cash Voucher")').remove()
            $('.field-box.field-nature_of_voucher').find('select option:contains("Refund")').remove()
        }
    }

     function refresh_Programs(){
        $.ajax({
            type: 'GET',
            url: '/admin/ipcaccounts/get_program_schedules',
            data: {
                    'zone': $(id_zone).val(),
                    'program_type': $(id_program_type).val()
                    },
            contentType: 'application/json; charset=utf-8',
            cache: false,
            success: function(data) {
                var listitems = '<option value="" selected="selected">---------</option>';
                $.each(data, function(key, value){
                    listitems += '<option value=' + value[0] + '>' + value[1] + '</option>';
                });
                $("#id_program_schedule").find('option').remove()
                $("#id_program_schedule").append(listitems);
                $("#id_budget_code").val('')
            }
        });
     }
}

)(django.jQuery);