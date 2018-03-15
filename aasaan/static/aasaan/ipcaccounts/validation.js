'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var $ = django.jQuery;

aasaan.submit_dispatch = function (e) {        
    e.preventDefault();

    var account_type = $("#id_account_type option:selected").text()
    if(account_type == 'Class Accounts'){
        if($("#id_program_schedule").val()==''){
                return addErrorMessage('Program schedule can not be empty')
        }
    }
    else if(account_type == 'Teacher Accounts'){
        if($("#id_teacher").val()==''){
            return addErrorMessage('Teacher can not be empty')
        }
        if($("#id_zone").val()==''){
            return addErrorMessage('Zone can not be empty')
        }
    }
    else {

        if($("#id_zone").val()==''){
            return addErrorMessage('Zone can not be empty')
        }
    }

//    if($("#id_budget_code").val()==''){
//        return addErrorMessage('Budget Code can not be empty')
//    }

    var no_of_item = parseInt($('#id_voucherdetails_set-TOTAL_FORMS').val())
    var item_array = [];
    for (var i=0; i<no_of_item; i++){
        var voucher_nature = $($('.field-nature_of_voucher').find('select')[i]).val()
        if(voucher_nature == ''){
            return addErrorMessage('Nature of voucher can not be empty')
        }

        voucher_nature = $('#'+$($('.field-nature_of_voucher').find('select')[i]).attr('id')+' option:selected').text()
        var voucher_date = $($('.field-voucher_date').find('input')[i]).val()
        if(voucher_date == ''){
            return addErrorMessage('Voucher Date can not be empty')
        }
        if(voucher_nature!='Reimbursement Payment'){
            if($($('.field-head_of_expenses').find('select')[i]).val() == ''){
                return addErrorMessage('Head of expenses can not be empty')
            }
        }

        var amount = $($('.field-amount').find('input')[i]).val()
        if(amount == ''){
            return addErrorMessage('Please enter amount')
        }

        if($('#id_voucherdetails_set-'+i+'-cheque').is(":checked")==false){
            $('#id_voucherdetails_set-'+i+'-address1').val('')
            $('#id_voucherdetails_set-'+i+'-address2').val('')
        }
    }

    $('.form-row.field-payment_date.field-utr_no.field-amount_after_tds').remove()
    $('.form-row.field-np_voucher_status.field-finance_submission_date.field-movement_sheet_no').remove()



    //Adds validation error message
    function addErrorMessage(message) {
        removeErrorMessage();
        $($('.submit-row')[0]).after('<p class="errornote">Please correct the error below. </p> <ul class="errorlist nonfield"><li>'+message+'</li></ul>');
        custom_error = true
        return false;
    }

    //Removes all validation error message
    function removeErrorMessage() {
        $(".errorlist").remove();
        $(".errornote").remove();
    }
    // this section disables the submit buttons after the form has been submitted
    // to avoid multi-clicks

    for (var i=0; i < aasaan.submit_elements.length; i++) {
        aasaan.submit_elements[i].disabled = true;
    }



    // the following section is needed for very precarious reasons.
    // because we are preventing default event process, the default
    // form submission doesn't happen. Along with it is lost
    // which button was clicked (it is important as django admin
    // uses that to dispatch the appropriate HTTPResponseRedirect)
    // so we are recreating the 'click' below by adding a new
    // hidden element

    var submit_element = document.createElement('input');
    submit_element.type = "hidden";
    submit_element.name = aasaan.submit_clicked_value;
    submit_element.value = aasaan.submit_clicked_value;
    aasaan.base_form.appendChild(submit_element);

    aasaan.base_form.submit();
}

// next three functions capture which button was clicked
// submit, submit and continue, submit and add new
aasaan.submit_clicked_save = function (e) {
    aasaan.submit_clicked_value = '_save';
}

aasaan.submit_clicked_addanother = function (e) {
    aasaan.submit_clicked_value = '_addanother';
}

aasaan.submit_clicked_continue = function (e) {
    aasaan.submit_clicked_value = '_continue';
}

window.addEventListener("load", function (e) {
    aasaan.input_div = document.getElementsByClassName('submit-row')[0];
    aasaan.submit_elements = aasaan.input_div.getElementsByTagName('input');

    for (var i=0; i < aasaan.submit_elements.length; i++) {
        aasaan.submit_elements[i].addEventListener('click', aasaan["submit_clicked" + aasaan.submit_elements[i].name], true);
    }
    aasaan.base_form = document.forms[0];
    aasaan.base_form.addEventListener('submit', aasaan.submit_dispatch, false);    
});