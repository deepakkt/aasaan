'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};


(function($) {
    $(document).ready(function($) {
//         $(".submit-row").hide()
        $("#id_name").prop("readonly", true);
        $("#id_zone").prop("disabled", true);
        $("#id_contact_name").prop("readonly", true);
        $("#id_contact_phone").prop("readonly", true);
        $('.change-related').hide()
        $('.add-related').hide()
    });

    $(document).on("submit", "form", function (e) {
        $("#id_name").prop("readonly", false);
        $("#id_zone").prop("disabled", false);
        $("#id_contact_name").prop("readonly", false);
        $("#id_contact_phone").prop("readonly", false);
    });
})(django.jQuery);