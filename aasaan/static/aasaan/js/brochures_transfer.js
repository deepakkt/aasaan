'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};

(function($) {

    $(document).on("submit", "form", function (e) {
        $("#id_transfer_type").prop("disabled", false);
        $("#id_source_stock_point").prop("disabled", false);
        $("#id_destination_stock_point").prop("disabled", false);
        $("#id_source_program_schedule").prop("disabled", false);
        $("#id_destination_program_schedule").prop("disabled", false);
        $('#id_status').prop("disabled", false);
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

        // show/hide on load based on pervious value of selectField
        toggleVerified(selectField.val());

        // show/hide on change
        selectField.change(function() {
            toggleVerified($(this).val());
        });
    });
}

)(django.jQuery);