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
    });
})(django.jQuery);