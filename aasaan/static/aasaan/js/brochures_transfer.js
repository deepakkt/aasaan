'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;

(function($) {

    $(document).on("submit", "form", function (e) {
        $("#id_transfer_type").prop("disabled", false);
        $("#id_source_stock_point").prop("disabled", false);
        $("#id_destination_stock_point").prop("disabled", false);
        $("#id_source_program_schedule").prop("disabled", false);
        $("#id_destination_program_schedule").prop("disabled", false);
        $('#id_status').prop("disabled", false);
        var selectField = $('#id_transfer_type');
        if(selectField.val( ) == 'SPSP'){
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
        if(parseInt($('#id_brochurestransactionitem_set-TOTAL_FORMS').val())==0){
            return addErrorMessage('Please add brochures and quantity.')
        }
        if(selectField.val( ) == 'SPSC' || selectField.val( ) == 'SPSP' || selectField.val( ) == 'SPGT'){
            var item_array = [];
            var no_of_item = parseInt($('#id_brochurestransactionitem_set-TOTAL_FORMS').val())
            for (var i=0; i<no_of_item; i++){
                var f_brochure = $('.field-brochures').children().children()[i*3]
                var quantity = $('.field-sent_quantity').children()[i]
                var key = $(f_brochure).val()
                var qty = $(quantity).val()
                if(qty=='' || key==''){
                    return addErrorMessage('Brochures and quantity can not be empty')
                }
                if(item_array.length>0 && $.inArray(parseInt(key), item_array)>=0){
                    return addErrorMessage('Selected '+$(f_brochure.selectedOptions).text() +' multiple times')
                }
                item_array.push(parseInt(key))
                if(parseInt(qty) > parseInt(brochure_list[key])){
                    return addErrorMessage('Selected '+$(f_brochure.selectedOptions).text() +' quantity in the source stock point is not available.')
                }
            }
        }

        function addErrorMessage(message) {
            removeErrorMessage();
            $($('.submit-row')[0]).after('<p class="errornote">Please correct the error below. </p> <ul class="errorlist nonfield"><li>'+message+'</li></ul>');
            custom_error = true
            return false;
        }

        function removeErrorMessage() {
            $(".errorlist").remove();
            $(".errornote").remove();
        }
    });

    $(function() {
        var received_quantity_innerHTML = $('.field-received_quantity').html()
        var selectField = $('#id_transfer_type');
        if ($('#id_transaction_status').val()=='OLD'){
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
            if(status=='DD' || status=='TC' || status=='LOST'){
                $('#id_status').prop("disabled", true);
                $('.vIntegerField').attr("readonly", true)
            }
            $('.add-row').hide()
        }

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
                if ($('#id_transaction_status').val()=='NEW'){
                    $('.field-received_quantity').html('')
                }
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
                if ($('#id_transaction_status').val()=='NEW'){
                    $('.field-received_quantity').html(received_quantity_innerHTML)
                }
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
                if ($('#id_transaction_status').val()=='NEW'){
                    $('.field-received_quantity').html(received_quantity_innerHTML)
                }
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
                if ($('#id_transaction_status').val()=='NEW'){
                    $('.field-received_quantity').html(received_quantity_innerHTML)
                }
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
                if ($('#id_transaction_status').val()=='NEW'){
                    $('.field-received_quantity').html(received_quantity_innerHTML)
                }
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
                if ($('#id_transaction_status').val()=='NEW'){
                    $('.field-received_quantity').html(received_quantity_innerHTML)
                }
            }

            if ($('#id_transaction_status').val()=='OLD'){
                $('.field-brochure_set').hide()
            }
        }

        function createBrochureSet(transset) {
            $('.inline-deletelink').trigger("click");
            $($('.field-brochures').children().children()[0]).val('')
            $($('.field-sent_quantity').children()[0]).val('')
            $($('.field-received_quantity').children()[0]).val('')
            var addRow = $(".add-row", "#brochurestransactionitem_set-group");
            var transset = $.parseJSON(transset)
            var i = 0;
            $.each(transset , function( key, value ) {
                addRow.children().children().trigger("click");
                var f_brochure = $('.field-brochures').children().children()[i*3]
                var f_sent_quantity = $('.field-sent_quantity').children()[i]
                $(f_brochure).val(value[0])
                $(f_sent_quantity).val(value[1])
                i++;
            });
        }

        function removeErrorMessage() {
            $(".errorlist").remove();
            $(".errornote").remove();
        }

        // show/hide on load based on pervious value of selectField
        toggleVerified(selectField.val());

        // show/hide on change
        selectField.change(function() {
            toggleVerified($(this).val());
            if(custom_error){
                removeErrorMessage();
                custom_error = false
            }
        });

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
                $('.inline-deletelink').trigger("click");
                $($('.field-brochures').children().children()[0]).val('')
                $($('.field-sent_quantity').children()[0]).val('')
                $($('.field-received_quantity').children()[0]).val('')
            }
        });
    });
}

)(django.jQuery);