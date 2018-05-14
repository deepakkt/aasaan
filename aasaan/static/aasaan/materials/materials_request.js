'use strict';

(function($) {
    $(document).ready(function() {
         $("#id_zone option[value='']").remove();
         $("#id_material_type option[value='']").remove();
//         $("#id_class_type option[value='']").remove();
//         $("#centermaterialitem_set-group").hide()
//         $("#classmaterialitem_set-group").show()
         handleOptGroup()

//         $("#id_material_type").change(function () {
////            handleOptGroup()
//        });

         $("#id_material_type").click(function () {
            handleOptGroup()
            $("#id_class_type").val('')
         });


         if(document.URL.indexOf('add')>-1){
            $("#courierdetails_set-group").hide()
         }
         else{
            $("#courierdetails_set-group").show()
         }
         var SENT_QUANTITY_INDEX = 3
         var class_table = $("#classmaterialitem_set-group").find('table')
         $(class_table).attr('id','id_table_classmaterialitem_set-group');

         var center_table = $("#centermaterialitem_set-group").find('table')
         $(center_table).attr('id','id_table_centermaterialitem_set-group');

         var kits_table = $("#kitsitem_set-group").find('table')
         $(kits_table).attr('id','id_table_kitsitem_set-group');

         var other_table = $("#othermaterialsmasteritem_set-group").find('table')
         $(other_table).attr('id','id_table_othermaterialsmasteritem_set-group');

         if(document.URL.indexOf('materialsrequestincharge')>-1){
            $('.field-sent_quantity').show()
            $("#id_table_classmaterialitem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").show()
            $("#id_table_centermaterialitem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").show()
            $("#id_table_kitsitem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").show()
            $("#id_table_othermaterialsmasteritem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").show()
         }
         else{
            $('.field-sent_quantity').hide()
            $("#id_table_classmaterialitem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").hide()
            $("#id_table_centermaterialitem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").hide()
            $("#id_table_kitsitem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").hide()
            $("#id_table_othermaterialsmasteritem_set-group thead tr").find("th:eq("+SENT_QUANTITY_INDEX+")").hide()
        }

        function handleOptGroup(){
            if($("#id_material_type").val()=="1"){
                $("#classmaterialitem_set-group").show()
                $("#centermaterialitem_set-group").hide()
                $("#kitsitem_set-group").hide()
                $("#othermaterialsmasteritem_set-group").hide()
                $('.form-row.field-center').hide()

            }
            else if($("#id_material_type").val()=="2"){
                $("#classmaterialitem_set-group").hide()
                $("#centermaterialitem_set-group").show()
                $("#othermaterialsmasteritem_set-group").hide()
                $("#kitsitem_set-group").hide()
                $('.form-row.field-center').show()
            }
            else if($("#id_material_type").val()=="3"){
                $("#classmaterialitem_set-group").hide()
                $("#centermaterialitem_set-group").hide()
                $("#othermaterialsmasteritem_set-group").show()
                $("#kitsitem_set-group").hide()
                $('.form-row.field-center').hide()
            }
            else{
                $("#classmaterialitem_set-group").hide()
                $("#centermaterialitem_set-group").hide()
                $("#othermaterialsmasteritem_set-group").hide()
                $("#kitsitem_set-group").show()
                $('.form-row.field-center').hide()
            }
        }
    });

})(django.jQuery);