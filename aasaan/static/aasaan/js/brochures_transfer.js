'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;


(function($) {
    //Validation on Submit
    $(document).on("submit", "form", function (e) {
        //enable all disabled input fields otherwise values will not be passed in request
        $("#id_transfer_type").prop("disabled", false);
        $("#id_source_stock_point").prop("disabled", false);
        $("#id_destination_stock_point").prop("disabled", false);
        $("#id_source_program_schedule").prop("disabled", false);
        $("#id_destination_program_schedule").prop("disabled", false);
        $('#id_status').prop("disabled", false);
        $('.field-sent_quantity').find('input').prop("readonly", false);
        $('.field-received_quantity').find('input').prop("readonly", false);
        $('.field-brochures').find('select').prop("disabled", false);

        var transaction_type = $('#id_transfer_type');
        if(transaction_type.val() == 'SPSP'){
            if($("#id_source_stock_point").val()==''){
                return addErrorMessage('Source stock point can not be empty')
            }
            if($("#id_destination_stock_point").val()==''){
                return addErrorMessage('Destination stock point can not be empty')
            }
            if($("#id_source_stock_point").val()==$("#id_destination_stock_point").val()){
               return addErrorMessage('Source stock point and destination stock point can not be same.')
            }
        }
        // if not even single brochures added/selected, throws validation error
        if(parseInt($('#id_brochurestransactionitem_set-TOTAL_FORMS').val())==0){
            return addErrorMessage('Please add brochures and quantity.')
        }
        // Checks for the entered quantity vs available qty in source stock point
        var no_of_item = parseInt($('#id_brochurestransactionitem_set-TOTAL_FORMS').val())
        var item_array = [];
        for (var i=0; i<no_of_item; i++){
            var f_brochure = $('.field-brochures').find('select')[i]
            var quantity = $('.field-sent_quantity').find('input')[i]
            var key = $(f_brochure).val()
            var qty = $(quantity).val()
            if ($('#id_transaction_status').val()=='NEW'){
                if(qty=='' || key==''){
                    return addErrorMessage('Brochures and quantity can not be empty')
                }
                if(item_array.length>0 && $.inArray(parseInt(key), item_array)>=0){
                    return addErrorMessage('Selected '+$(f_brochure.selectedOptions).text() +' multiple times')
                }
                item_array.push(parseInt(key))
                if(transaction_type.val() == 'BLSP' || transaction_type.val() == 'SPSC' || transaction_type.val() == 'SPSP' || transaction_type.val() == 'SPGT'){
                    if(brochure_list[key]==undefined || brochure_list[key]=='undefined'){
                        return addErrorMessage('Selected '+$(f_brochure.selectedOptions).text() +' brochure in the source stock point is not available.')
                    }
                    if(parseInt(qty) > parseInt(brochure_list[key])){
                        return addErrorMessage('Selected '+$(f_brochure.selectedOptions).text() +' quantity in the source stock point is not available.')
                    }
                }
            }
            if($('#id_status').val()=='DD'){
                var r_quantity = $('.field-received_quantity').find('input')[i]
                var r_qty = $(r_quantity).val()
                if(r_qty!='' && parseInt(r_qty)>parseInt(qty)){
                    return addErrorMessage('Entered '+ $(f_brochure.selectedOptions).text() +' received quantity is more than sent quantity')
                }else if(r_qty==''){
                    $(r_quantity).val(qty)
                }
            }
        }

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
    });

    $(function() {
        //hide all brochures transaction item select field add and change icon
         $('.change-related').hide()
         $('.add-related').hide()
        //based on New entry or old entry, disable brochures transaction item
        if ($('#id_transaction_status').val()=='NEW'){
            $('.field-received_quantity').find('input').prop("readonly", true);
        }
        else{
            //for OLD entry, hide/disable/readonly
            $('.add-row').hide()
            $('.form-row field-brochure_set').hide()
            $("#id_transfer_type").prop("disabled", true);
            $("#id_source_stock_point").prop("disabled", true);
            $("#id_destination_stock_point").prop("disabled", true);
            $("#id_source_program_schedule").prop("disabled", true);
            $("#id_destination_program_schedule").prop("disabled", true);
            $("#id_source_printer").prop("readonly", true);
            $("#id_guest_name").prop("readonly", true);
            $("#id_guest_phone").prop("readonly", true);
            $("#id_guest_email").prop("readonly", true);

            var status = $('#id_status').val()
            if(status=='DD' || status=='TC' || status=='LOST' || status=='CLS'){
                $('.field-sent_quantity').find('input').prop("readonly", true);
                $('.field-received_quantity').find('input').prop("readonly", true);
                $('.field-brochures').find('select').prop("disabled", true);
                $('#id_status').prop("disabled", true);
            }
            else if(status=='NEW' || status=='IT'){
                $('.field-sent_quantity').find('input').prop("readonly", true);
                $('.field-received_quantity').find('input').prop("readonly", false);
                $('.field-brochures').find('select').prop("disabled", true);
            }
        }

        var transaction_type = $('#id_transfer_type');
        function toggleVerified(value) {

            if(value == 'ABSP' || value == 'BLSP') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').hide()
                $('.field-source_program_schedule').hide()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').hide()
                $('.field-status').hide()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Stock Point:');
                $("#brochuresshipment_set-group").hide()
            }
            else if(value == 'PRSP') {
                $('.field-source_printer').show()
                $('.field-source_stock_point').hide()
                $('.field-destination_stock_point').show()
                $('.field-source_program_schedule').hide()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').show()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SPSC') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').hide()
                $('.field-source_program_schedule').hide()
                $('.field-destination_program_schedule').show()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').show()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SCSP') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').hide()
                $('.field-destination_stock_point').show()
                $('.field-source_program_schedule').show()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').show()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SPSP') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').show()
                $('.field-source_program_schedule').hide()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').show()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SPGT') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').hide()
                $('.field-source_program_schedule').hide()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').show()
                $('.field-guest_phone').show()
                $('.field-guest_email').show()
                $('.field-brochure_set').show()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            //necessary here since in toggle it may show up.
            if ($('#id_transaction_status').val()!='NEW'){
                $('.field-brochure_set').hide()
            }
        }

        function removeErrorMessage() {
            $(".errorlist").remove();
            $(".errornote").remove();
        }

        // show/hide on load based on pervious value of transaction_type
        toggleVerified(transaction_type.val());

        // show/hide on change
        transaction_type.change(function() {
            toggleVerified($(this).val());
            clearBrochureSet()
            $("#id_brochure_set").val('')
            if(custom_error){
                removeErrorMessage();
                custom_error = false
            }
        });
        //retrieves source stock point item and quantity for validation in form submit
        $("#id_source_stock_point").change(function() {
            $.ajax({
                type: 'GET',
                url: '/admin/brochures/get_brochure_list/',
                data: {
                        'source_stock_point': $(this).val()
                        },
                contentType: 'application/json; charset=utf-8',
                cache: false,
                success: function(data) {
                    var blist = $.parseJSON(data)
                    $.each(blist, function(key, value){
                        brochure_list[value[0]] = value[1];
                     });
                }
            });

        });

        function clearBrochureSet(){
            $('.inline-deletelink').trigger("click");
            $($('.field-brochures').find('select')[0]).val('')
            $($('.field-sent_quantity').find('input')[0]).val('')
            $($('.field-received_quantity').find('input')[0]).val('')
        }

        function createBrochureSet(transset) {
            clearBrochureSet()
            var addRow = $(".add-row", "#brochurestransactionitem_set-group");
            var transset = $.parseJSON(transset)
            var i = 0;
            $.each(transset , function( key, value ) {
                addRow.find('a').trigger("click");
                var f_brochure = $('.field-brochures').find('select')[i]
                var f_sent_quantity = $('.field-sent_quantity').find('input')[i]
                $(f_brochure).val(value[0])
                $(f_sent_quantity).val(value[1])
                i++;
            });
        }

        //populate brochure set using ajax
        $("#id_brochure_set").change(function() {
            if ($(this).val()!=''){
                $.ajax({
                    type: 'GET',
                    url: '/admin/brochures/get_brochure_set',
                    data: {
                            'brochure_set': $(this).val()
                            },
                    contentType: 'application/json; charset=utf-8',
                    cache: false,
                    success: function(data) {
                        createBrochureSet(data)
                        if(custom_error){
                            removeErrorMessage();
                            custom_error = false
                        }
                    }
                });
            }
            else{
                //if brochure set is not selected or empty, delete all iteam and empty first item
                $('.inline-deletelink').trigger("click");
                $($('.field-brochures').find('select')[0]).val('')
                $($('.field-sent_quantity').find('input')[0]).val('')
                $($('.field-received_quantity').find('input')[0]).val('')
            }
        });
    });
}

)(django.jQuery);