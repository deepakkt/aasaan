'use strict';

(function($) {
    $(document).ready(function() {

         $('#content').find('h1').remove()

        //hide one transaction set for new voucher
        if($('#id_feedbacknotes_set-TOTAL_FORMS').val()==0){
            $('#feedbacknotes_set-group').hide()
        }
        if(document.URL.indexOf('add')>-1){
            $('.form-row.field-status').hide()
        }
        else{
            $('.form-row.field-status').show()
        }
    });

})(django.jQuery);