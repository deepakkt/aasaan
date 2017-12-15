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
             var select1 = $('#id_voucherdetails_set-__prefix__-voucher_status').clone()
             var select = $('#id_voucherdetails_set-__prefix__-voucher_status')
             var optGroupRC = $('<optgroup>').attr('label', 'RCO');
             var optGroupNP = $('<optgroup>').attr('label', 'Nodal Point');
             var optGroupFI = $('<optgroup>').attr('label', 'Finance');
             select.empty()
             select.append(select1.children()[0])
             var options = select1.children()

         for (var i = 0; i < options.length; i++){
            var option = options[i];


            if(strStartsWith(option.text, 'RC'))
            {
                option.text = option.text.substr(5);
                optGroupRC.append(option);
            }
            if(strStartsWith(option.text, 'NP'))
            {
                option.text = option.text.substr(5);
                optGroupNP.append(option);
            }
            if(strStartsWith(option.text, 'FI'))
            {
                option.text = option.text.substr(5);
                optGroupFI.append(option);
            }

          }
          select.append(optGroupRC)
          select.append(optGroupNP)
          select.append(optGroupFI)

})

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
            $('.field-ca_head_of_expenses').show()
            $('.field-ta_head_of_expenses').hide()
            $('.field-oa_head_of_expenses').hide()
            $('.field-party_name').show()
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
                $('.field-ca_head_of_expenses').hide()
                $('.field-ta_head_of_expenses').show()
                $('.field-oa_head_of_expenses').hide()
                $('.field-party_name').hide()
            }
            else if($("#id_account_type").val()=='CA'){
                $('.field-teacher').hide()
                $('.field-program_schedule').show()
                $('.field-zone').hide()
                $('.field-budget_code').show()
                $('.field-ca_head_of_expenses').show()
                $('.field-ta_head_of_expenses').hide()
                $('.field-oa_head_of_expenses').hide()
                $('.field-party_name').show()
            }
            else {
                $('.field-teacher').hide()
                $('.field-program_schedule').hide()
                $('.field-zone').show()
                $('.field-budget_code').show()
                $('.field-ca_head_of_expenses').hide()
                $('.field-ta_head_of_expenses').hide()
                $('.field-oa_head_of_expenses').show()
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