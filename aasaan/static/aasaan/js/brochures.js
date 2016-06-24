'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};


(function($) {
    $(document).ready(function($) {
//         $(".submit-row").hide()
        $("#id_name").prop("readonly", true);
        $("#id_zone").prop("disabled", true);
    });
})(django.jQuery);