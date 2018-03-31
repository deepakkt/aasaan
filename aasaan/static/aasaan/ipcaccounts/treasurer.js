'use strict';

(function($) {

    $(document).ready(function() {
        $('.field-box.field-old_treasurer').hide()
        $("#id_request_type").change(function() {
            if($("#id_request_type").val()=='ADD'){
               $('.field-box.field-old_treasurer').hide()
               $('#id_old_treasurer').val('')
            }
            else{
               $('.field-box.field-old_treasurer').show()
            }
        })

    });

}

)(django.jQuery);