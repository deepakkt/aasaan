var URL = "http://aasaan.isha.in/config/admin_dashboard";
var CMD = '';
var SPAN_ID = '';
var MSG = 'MESSAGE IS NOT FROM THE SERVER';

function setCommand(txtcmd, txtSpanId) {
    CMD = txtcmd;
    SPAN_ID = txtSpanId;    
    return true;
}

$(document).ready(function() {
    for (var i = 4; i <= 12; i++) {
        $("#id_button" + i).hide();
    }
    $('button[type="submit"]').on('click', function() {        
        var result = $.ajax({
            url: URL,
            data: {
                command: CMD
            },
            type: "POST",
            dataType: "json",
            timeout: 20000,
            async: false,
        }).responseText;
        if (result.code == 'success') {
            $("#" + SPAN_ID).html(result.message).addClass('success').slideUp("slow").slideDown("slow");
        } else if (result.code == 'warning') {
            $("#" + SPAN_ID).html(result.message).addClass('warning').slideUp("slow").slideDown("slow");
        } else if (result.code == 'error') {
            $("#" + SPAN_ID).html(result.message).addClass('error').slideUp("slow").slideDown("slow");
        } else {
            $("#" + SPAN_ID).html(MSG).slideUp("slow").slideDown("slow");
        }
    });
});