'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};
var brochure_list = {};
var custom_error = false;


(function($) {
    //Validation on Submit

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
            $("#id_destination_program_schedule").prop("disabled", true);
            $("#id_source_printer").prop("readonly", true);
            $("#id_guest_name").prop("readonly", true);
            $("#id_guest_phone").prop("readonly", true);
            $("#id_guest_email").prop("readonly", true);

            var status = $('#id_status').val()
            if(status=='DD' || status=='TC' || status=='LOST'){
                $('.field-sent_quantity').find('input').prop("readonly", true);
                $('.field-received_quantity').find('input').prop("readonly", true);
                $('.field-brochures').find('select').prop("disabled", true);
                $('#id_status').prop("disabled", true);
            }
            else if(status=='NEW'){
                $('.field-sent_quantity').find('input').prop("readonly", true);
                $('.field-received_quantity').find('input').prop("readonly", false);
                $('.field-brochures').find('select').prop("disabled", true);
            }
        }

        var transaction_type = $('#id_transfer_type');
        function toggleVerified(value) {

            if(value == 'ABSP' || value == 'DBSP') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').hide()
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
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').hide()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SPSC') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').hide()
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
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').hide()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SPSP') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').show()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').hide()
                $('.field-guest_phone').hide()
                $('.field-guest_email').hide()
                $('.field-brochure_set').hide()
                $('.field-status').show()
                $('label[for="'+$('#id_source_stock_point').attr('id')+'"]').text('Source stock Point:');
                $("#brochuresshipment_set-group").show()
            }
            else if(value == 'SPGT') {
                $('.field-source_printer').hide()
                $('.field-source_stock_point').show()
                $('.field-destination_stock_point').hide()
                $('.field-destination_program_schedule').hide()
                $('.field-guest_name').show()
                $('.field-guest_phone').show()
                $('.field-guest_email').show()
                $('.field-brochure_set').hide()
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