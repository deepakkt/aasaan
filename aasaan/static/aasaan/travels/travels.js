'use strict';

(function($) {
    $(document).ready(function() {
         $('.actions').find('button').click(function(event) {
            if($('.actions').find('select').val() == 'make_email'){
                var favorite = [];
                $.each($("input[name='_selected_action']:checked"), function(){
                    favorite.push($(this).val());
                });
                if(favorite.length>0){
                    document.getElementById('send_email').href = document.getElementById('send_email').href+'?emailforid='+favorite.join(", ")
                    document.getElementById('send_email').click();
                }
            }
         })

         $('.actions').find('button').click(function(event) {
            if($('.actions').find('select').val() == 'make_email'){
                var favorite = [];
                $.each($("input[name='_selected_action']:checked"), function(){
                    favorite.push($(this).val());
                });
                if(favorite.length>0){
                    document.getElementById('send_email').href = document.getElementById('send_email').href+'?emailforid='+favorite.join(", ")
                    document.getElementById('send_email').click();
                }
            }
         })

         $("#searchbar").attr('title', "Search Source or Destination or Teacher Name")
         $("#id_zone option[value='']").remove();

         if($('#id_status').val()!='CB'){
            $('.form-row.field-refund_amount').hide()
         }

         $('#id_status').click(function(event) {
             if($('#id_status').val()=='CB'){
                $('.form-row.field-refund_amount').show()
             }
             else{
                $('.form-row.field-refund_amount').hide()
             }
         });

    });

})(django.jQuery);