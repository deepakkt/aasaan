'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;
var eeeee;

(function($) {

    $(function() {


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
            $('#voucherdetails_set-group').find('.add-row').hide()
            $('.form-row.field-np_voucher_status.field-finance_submission_date.field-movement_sheet_no').show()
            $('.form-row.field-payment_date.field-utr_no.field-amount_after_tds').show()
            $('#id_voucherdetails_set-0-copy_voucher').parent().parent().show()
            $('#id_voucherdetails_set-0-copy_voucher').next().html('Copy All')

            var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())

            for (var i=1; i<no_of_item; i++){
                if($($('.field-tracking_no').find('input')).val() !='')
                    $($('.field-copy_voucher')[i]).hide()
            }

            for (var i=0; i<=no_of_item-1; i++){
                $('#id_voucherdetails_set-'+i+'-nature_of_voucher').change(function () {
                    if($(this).find('option:selected').text()!='Expenses'){
                        $(this).parent().parent().parent().parent().parent().find('.form-row.field-payment_date.field-utr_no.field-amount_after_tds').show()
                    }
                    else{
                        $(this).parent().parent().parent().parent().parent().find('.form-row.field-payment_date.field-utr_no.field-amount_after_tds').hide()
                    }
                });
            }
            $($('.checkbox-row').find('input')[0]).change(function () {
                if($(this).is(":checked")){
                    var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())
                    for (var i=1; i<no_of_item; i++){
                        $('#id_voucherdetails_set-'+i+'-np_voucher_status').val($('#id_voucherdetails_set-0-np_voucher_status').val())
                        $('#id_voucherdetails_set-'+i+'-finance_submission_date').val($('#id_voucherdetails_set-0-finance_submission_date').val())
                        $('#id_voucherdetails_set-'+i+'-movement_sheet_no').val($('#id_voucherdetails_set-0-movement_sheet_no').val())
                        $('#id_voucherdetails_set-'+i+'-payment_date').val($('#id_voucherdetails_set-0-payment_date').val())
                        $('#id_voucherdetails_set-'+i+'-utr_no').val($('#id_voucherdetails_set-0-utr_no').val())
                        $('#id_voucherdetails_set-'+i+'-amount_after_tds').val($('#id_voucherdetails_set-0-amount_after_tds').val())
                    }
//                    $(window).setInterval(resetCopy, 1000);
//resetCopy()
                }
            });
        }
        else{
            $('.form-row.field-np_voucher_status.field-finance_submission_date.field-movement_sheet_no').hide()
            $('.form-row.field-payment_date.field-utr_no.field-amount_after_tds').hide()
            $('#id_voucherdetails_set-0-copy_voucher').parent().parent().hide()
        }

        function strStartsWith(str, prefix) {
            return str.indexOf(prefix) === 0;
        }

        function resetCopy() {
            $('#id_voucherdetails_set-0-copy_voucher').prop('checked', false).removeAttr('checked')
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

        if($("#id_account_type option:selected").text()=='Class Accounts'){
            $('.field-teacher').hide()
            $('.field-program_schedule').show()
            $('.field-zone').hide()
            $('.field-budget_code').show()
            $('.field-box.field-party_name').show()
        }
        toggleVerified()

        $("#id_account_type").change(function() {
            toggleVerified();
        })

        function toggleVerified() {
            if($("#id_account_type option:selected").text()=='Teachers Accounts'){
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
                $('.field-box.field-party_name').show()
            }
            else {
                $('.field-teacher').hide()
                $('.field-program_schedule').hide()
                $('.field-zone').show()
                $('.field-budget_code').show()
                $('.field-box.field-party_name').show()
            }
        }

        });



        django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
            if(formsetName == 'voucherdetails_set'){
                $($row.find('.field-tracking_no')).hide()
                $('#id_voucherdetails_set-0-copy_voucher').parent().parent().hide()
                var line_no = $row.find('.inline_label').html()
                line_no = line_no.split('#')[1]
                $($('.form-row.field-cheque.field-address1.field-address2')[line_no-1]).hide()
                if(document.URL.indexOf('rcoaccountsmaster')>-1){
                    $($('.checkbox-row').find('input')[line_no-1]).change(function () {
                        var id = $(this).parent().parent().parent().parent().attr('id')
                        var vid = id.split('-')[1]
                        if($(this).is(":checked")){
                            $('#id_voucherdetails_set-'+vid+'-nature_of_voucher').val($('#id_voucherdetails_set-'+(vid-1)+'-nature_of_voucher').val())
                            $('#id_voucherdetails_set-'+vid+'-voucher_status').val($('#id_voucherdetails_set-'+(vid-1)+'-voucher_status').val())
                            $('#id_voucherdetails_set-'+vid+'-voucher_date').val($('#id_voucherdetails_set-'+(vid-1)+'-voucher_date').val())
                            $('#id_voucherdetails_set-'+vid+'-head_of_expenses').val($('#id_voucherdetails_set-'+(vid-1)+'-head_of_expenses').val())
                            $('#id_voucherdetails_set-'+vid+'-party_name').val($('#id_voucherdetails_set-'+(vid-1)+'-party_name').val())
                            $('#id_voucherdetails_set-'+vid+'-expenses_description').val($('#id_voucherdetails_set-'+(vid-1)+'-expenses_description').val())
                            $('#id_voucherdetails_set-'+vid+'-amount').val($('#id_voucherdetails_set-'+(vid-1)+'-amount').val())
                            $('#id_voucherdetails_set-'+vid+'-approval_sent_date').val($('#id_voucherdetails_set-'+(vid-1)+'-approval_sent_date').val())
                            $('#id_voucherdetails_set-'+vid+'-approved_date').val($('#id_voucherdetails_set-'+(vid-1)+'-approved_date').val())
                            $('#id_voucherdetails_set-'+vid+'-nature_of_voucher').change();
                        }
                    });

                    var check_box = $(this).parent().parent().parent().parent().parent().find('.field-box.field-cheque').parent()
                    $(check_box).hide()

                    $('#id_voucherdetails_set-'+(line_no-1)+'-nature_of_voucher').change(function () {
                        var cbox = $(this).parent().parent().parent().parent().parent().find('.field-box.field-cheque').parent()
                        if($(this).find('option:selected').text() == 'Expenses' || $(this).val() == ''){
                            $(cbox).hide()
                            $($(cbox).find('input')).prop('checked', false)
                            var i = $($(cbox).find('input')).attr('id').split('-')[1]
                            $($('.field-box.field-address1')[i]).hide()
                            $($('.field-box.field-address2')[i]).hide()
                        }
                        else{
                            $(cbox).show()
                            $($(cbox).find('input')).change(function () {
                                var i = $(this).attr('id').split('-')[1]
                                if($(this).is(":checked")){
                                   $($('.field-box.field-address1')[i]).show()
                                   $($('.field-box.field-address2')[i]).show()
                                }
                                else{

                                    $($('.field-box.field-address1')[i]).hide()
                                    $($('.field-box.field-address2')[i]).hide()
                                }
                            });
                        }
                    });

                    $($('.field-box.field-address1')[line_no-1]).hide()
                    $($('.field-box.field-address2')[line_no-1]).hide()

                }

            }
    });
}

)(django.jQuery);