'use strict';
var aasaan = window.aasaan || {};

window.addEventListener("load", function (e) {
    // do the auto population only for new schedules. leave existing schedules untouched
    if (document.URL.endsWith('/add/')) {
        // the next set of lines attempts to locate the add new row for program 
        // batch programmatically. Lack of id for that particular line makes it
        // not so straightforward
        aasaan.program_batch_div = document.getElementById('programbatch_set-group');
        aasaan.program_batch_add_tr = aasaan.program_batch_div.getElementsByClassName('add-row')[0];
        aasaan.program_batch_add_set = aasaan.program_batch_add_tr.getElementsByTagName('a')[0];
        
        // now simulate click of adding two new rows which will setup two dynamic rows
        // which will allow for their deletion as well by virtue of the event handlers
        aasaan.program_batch_add_set.click();
        aasaan.program_batch_add_set.click();
        
        aasaan.schedule_batch_1 = document.getElementById("id_programbatch_set-0-batch");
        aasaan.schedule_batch_2 = document.getElementById("id_programbatch_set-1-batch");
        aasaan.schedule_start_time_1 = document.getElementById("id_programbatch_set-0-start_time");
        aasaan.schedule_start_time_2 = document.getElementById("id_programbatch_set-1-start_time");
        aasaan.schedule_end_time_1 = document.getElementById("id_programbatch_set-0-end_time");
        aasaan.schedule_end_time_2 = document.getElementById("id_programbatch_set-1-end_time");
        
        for (var i=0; i < aasaan.schedule_batch_1.children.length; i++) {
            var each_item = aasaan.schedule_batch_1.children[i];
            if (each_item.innerHTML.startsWith('Morning'))
                {
                    aasaan.schedule_batch_1.value = each_item.value;
                    aasaan.schedule_start_time_1.value = "06:00 AM";
                    aasaan.schedule_end_time_1.value = "08:30 AM";
                    break;
                }
        }
        
        for (var i=0; i < aasaan.schedule_batch_2.children.length; i++) {
            var each_item = aasaan.schedule_batch_2.children[i];
            if (each_item.innerHTML.startsWith('Evening'))
                {
                    aasaan.schedule_batch_2.value = each_item.value;
                    aasaan.schedule_start_time_2.value = "06:00 PM";
                    aasaan.schedule_end_time_2.value = "08:30 PM";
                    break;
                }
        }
        
    }
});