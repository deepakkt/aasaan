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
         $("#id_travel_class option[value='']").remove();

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

         handleOptGroup();

         $("#id_travel_mode").click(function () {
            handleOptGroup()
            if($("#id_travel_mode").val()=="FL"){
                $('#id_travel_class').val('8')
            }
            else if($("#id_travel_mode").val()=="BS"){
                $('#id_travel_class').val('6')
            }
            else{
                $('#id_travel_class').val('1')
            }


        });

        function handleOptGroup(){
            if($("#id_travel_mode").val()=="FL"){
                $('#id_travel_class').children("optgroup[label='Bus']").hide();
                $('#id_travel_class').children("optgroup[label='Flight']").show();
                $('#id_travel_class').children("optgroup[label='Train']").hide();
             }
             else if($("#id_travel_mode").val()=="BS"){
                $('#id_travel_class').children("optgroup[label='Train']").hide();
                $('#id_travel_class').children("optgroup[label='Flight']").hide();
                $('#id_travel_class').children("optgroup[label='Bus']").show();
             }
             else{
                $('#id_travel_class').children("optgroup[label='Train']").show();
                $('#id_travel_class').children("optgroup[label='Flight']").hide();
                $('#id_travel_class').children("optgroup[label='Bus']").hide();
             }
        }

    });

})(django.jQuery);