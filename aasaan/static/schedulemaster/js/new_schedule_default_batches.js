var aasaan = window.aasaan || {};

window.addEventListener("load", function (e) {
    // do the auto population only for new schedules. leave existing schedules untouched
    if (document.URL.endsWith('/add/')) {
        aasaan.schedule_batch_1 = document.getElementById("id_programbatch_set-0-batch");
        aasaan.schedule_batch_2 = document.getElementById("id_programbatch_set-1-batch");
        aasaan.schedule_start_time_1 = document.getElementById("id_programbatch_set-0-start_time");
        aasaan.schedule_start_time_2 = document.getElementById("id_programbatch_set-1-start_time");
        aasaan.schedule_end_time_1 = document.getElementById("id_programbatch_set-0-end_time");
        aasaan.schedule_end_time_2 = document.getElementById("id_programbatch_set-1-end_time");
        
        // set first set to default morning times
        // note: 1 - Morning, 2 - Noon, 3 - Evening
        // it follows a chronological ordering
        aasaan.schedule_batch_1.value = "1";
        aasaan.schedule_start_time_1.value = "06:00 AM";
        aasaan.schedule_end_time_1.value = "08:30 AM";
        
        // set second set to default evening times
        aasaan.schedule_batch_2.value = "3";
        aasaan.schedule_start_time_2.value = "06:00 PM";
        aasaan.schedule_end_time_2.value = "08:30 PM";
        
    }
});