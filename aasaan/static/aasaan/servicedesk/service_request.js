'use strict';

(function($) {

    $(document).ready(function() {
         $("#id_zone option[value='']").remove();
         $("#id_status option[value='']").remove();
         $("#id_system_type option[value='']").remove();

                //hide one transaction set for new voucher
        if($('#id_servicerequestnotes_set-TOTAL_FORMS').val()==0){
            $('#servicerequestnotes_set-group').hide()
        }




    });

})(django.jQuery);