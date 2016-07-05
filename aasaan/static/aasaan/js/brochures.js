'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};


(function($) {
    $(document).ready(function($) {
        var brochure = []
        $('.field-item').find('select').each(function () {
            if ($(this).val()!='')
                brochure.push($(this).val())
        });
        $.ajax({
            type: 'GET',
            url: '/admin/brochures/get_brochure_image/',
            data: {
                    'brochure_ids' : JSON.stringify(brochure)
                    },
            contentType: 'application/json; charset=utf-8',
            cache: false,
            success: function(data) {
                var ps_list = {};
                $.each(data, function(key, value){
                    ps_list[value[0]] = value[1];
                });
                var line_items = parseInt($("#id_brochures_set-TOTAL_FORMS").val())
                for(var i=0;i<line_items;i++){
                    var image_href = ps_list[$($('.field-item').find('select')[i]).val()]
                    if(image_href.indexOf('no-photo.jpg')>=0)
                        $($('.field-brochure_image')[i]).html('<img src="'+image_href+'" style="width:50px; height:50px">')
                    else
                        $($('.field-brochure_image')[i]).html('<a href=""><img src="'+image_href+'" style="width:50px; height:50px"></a>')
                }
            }
        });

        $("#id_name").prop("readonly", true);
        $("#id_zone").prop("disabled", true);
        $("#id_contact_name").prop("readonly", true);
        $("#id_contact_phone").prop("readonly", true);
        $('.change-related').hide()
        $('.add-related').hide()
        $('.field-item').find('select').prop("disabled", true);
        $('.field-quantity').find('input').prop("readonly", true);
        $('.field-status').find('select').prop("disabled", true);
        $('.field-brochure_image').find('input').prop("readonly", true);
    });

    $(document).on("submit", "form", function (e) {
        $("#id_name").prop("readonly", false);
        $("#id_zone").prop("disabled", false);
        $("#id_contact_name").prop("readonly", false);
        $("#id_contact_phone").prop("readonly", false);
        $('.field-item').find('select').prop("disabled", false);
        $('.field-quantity').find('input').prop("readonly", false);
        $('.field-status').find('select').prop("disabled", false);
        $('.field-brochure_image').find('input').prop("readonly", false);
    });
})(django.jQuery);