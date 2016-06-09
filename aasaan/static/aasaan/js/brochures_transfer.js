'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};

(function($) {

    $(function() {
        var selectField = $('#id_transfer_type');

        function toggleVerified(value) {
            if(value == 'PSP') {
                $('#id_source_printer').closest("div").parent('div').show()
                $('#id_source_stock_point').closest("div").parent('div').parent('div').hide()
                $('#id_destination_stock_point').closest("div").parent('div').parent('div').show()
                $('#id_source_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_destination_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_guest_name').closest("div").parent('div').hide()
                $('#id_guest_phone').closest("div").parent('div').hide()
                $('#id_guest_email').closest("div").parent('div').hide()
            }
            else if(value == 'SPSH') {
                $('#id_source_printer').closest("div").parent('div').hide()
                $('#id_source_stock_point').closest("div").parent('div').parent('div').show()
                $('#id_destination_stock_point').closest("div").parent('div').parent('div').hide()
                $('#id_source_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_destination_program_schedule').closest("div").parent('div').parent('div').show()
                $('#id_guest_name').closest("div").parent('div').hide()
                $('#id_guest_phone').closest("div").parent('div').hide()
                $('#id_guest_email').closest("div").parent('div').hide()
            }
            else if(value == 'SCSP') {
                $('#id_source_printer').closest("div").parent('div').hide()
                $('#id_source_stock_point').closest("div").parent('div').parent('div').hide()
                $('#id_destination_stock_point').closest("div").parent('div').parent('div').show()
                $('#id_source_program_schedule').closest("div").parent('div').parent('div').show()
                $('#id_destination_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_guest_name').closest("div").parent('div').hide()
                $('#id_guest_phone').closest("div").parent('div').hide()
                $('#id_guest_email').closest("div").parent('div').hide()
            }
            else if(value == 'STPT') {
                $('#id_source_printer').closest("div").parent('div').hide()
                $('#id_source_stock_point').closest("div").parent('div').parent('div').show()
                $('#id_destination_stock_point').closest("div").parent('div').parent('div').show()
                $('#id_source_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_destination_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_guest_name').closest("div").parent('div').hide()
                $('#id_guest_phone').closest("div").parent('div').hide()
                $('#id_guest_email').closest("div").parent('div').hide()
            }
            else if(value == 'GUST') {
                $('#id_source_printer').closest("div").parent('div').hide()
                $('#id_source_stock_point').closest("div").parent('div').parent('div').show()
                $('#id_destination_stock_point').closest("div").parent('div').parent('div').hide()
                $('#id_source_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_destination_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_guest_name').closest("div").parent('div').show()
                $('#id_guest_phone').closest("div").parent('div').show()
                $('#id_guest_email').closest("div").parent('div').show()
            }
            else{
                $('#id_source_stock_point').closest("div").parent('div').parent('div').hide()
                $('#id_source_printer').closest("div").parent('div').hide()
                $('#id_destination_stock_point').closest("div").parent('div').parent('div').hide()
                $('#id_source_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_destination_program_schedule').closest("div").parent('div').parent('div').hide()
                $('#id_guest_name').closest("div").parent('div').hide()
                $('#id_guest_phone').closest("div").parent('div').hide()
                $('#id_guest_email').closest("div").parent('div').hide()
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