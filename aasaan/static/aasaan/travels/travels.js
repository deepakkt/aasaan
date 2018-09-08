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
         $('#content').find('h1').remove()

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

         $("#id_travel_mode").change(function () {
            handleOptGroup()
//            setTimeout(handleOptGroup, 1000)
        });

        $("#id_travel_mode").click(function () {

            if($("#id_travel_mode").val()=="FL"){
                $('#id_travel_class').val('')
            }
            else if($("#id_travel_mode").val()=="BS"){
                $('#id_travel_class').val('')
            }
            else{
                $('#id_travel_class').val('')
            }


        });

        if(document.URL.indexOf('agenttravelrequest')>-1){
            var i = document.URL.indexOf('agenttravelrequest');
            var url = document.URL;
            var id = url.substring(i).split('/')[1];
            $.ajax({
                type: 'GET',
                url: '/admin/travels/get_passanger_details?id='+id,
                contentType: 'application/json; charset=utf-8',
                cache: false,
                success: function(data) {
                  $('.form-row.field-teacher').find('.readonly').html(data)
                  console.log(data)
                }
            });
        }

                //hide one transaction set for new voucher
        if($('#id_travelnotes_set-TOTAL_FORMS').val()==0){
            $('#travelnotes_set-group').hide()
        }


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
        if($('#id_is_teacher').val() ==true){
            $('#others_set-group').show()
        }
        else{
            $('#others_set-group').hide()
        }

        $("#id_is_others").click(function () {
            if ($(this).is(':checked')) {
                $('#others_set-group').show()
            }
            else{
                $('#others_set-group').hide()
            }
        })


        if (document.URL.indexOf('change')>-1){
            $('.form-row.field-invoice_no').parent().show()
            $('.form-row.field-ticket_number').show()
            $('#id_ticket_number').prop("readonly", true);
            $('.form-row.field-zone').hide()

        }
        else{
            $('.form-row.field-invoice_no').parent().hide()
            $('.form-row.field-ticket_number').hide()
            $('#id_ticket_number').prop("readonly", true);
            $('.form-row.field-zone').show()
        }

            //Adds validation error message
        if($('#id_is_others').is(":checked")){
            $('#others_set-group').show()
        }else{
            $('#others_set-group').hide()
        }



    });

})(django.jQuery);