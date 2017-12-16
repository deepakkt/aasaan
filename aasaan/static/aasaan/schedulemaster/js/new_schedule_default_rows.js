'use strict';
var aasaan = window.aasaan || {};

(function($) {
    function removeDateIcon(){
        var e_date = $('.field-end_date').find('span')
        var s_date = $('.field-start_date').find('span')
        $(e_date[0]).remove()
        $(s_date[0]).remove()
    }
    $(window).setInterval(removeDateIcon, 1000);

})(django.jQuery);

aasaan.addEntries = function(groupID, groupEntries) {
    var validInputElements = ['text', 'select-one', 'textarea'];

    // get the div containing the group that is requested
    var rootDiv = document.getElementById(groupID + "-group");

    // get the click link.
    var clickTr = rootDiv.getElementsByClassName('add-row')[0];
    var addRow = clickTr.getElementsByTagName('a')[0];

    var numRows = groupEntries.length;

    // now 'click' the button as many times the entries are
    for (var i=0; i < numRows; i++) {
        addRow.click();
    }


    // now fill in the values from the group entries array
    // we will simply assume the array row columns match the
    // columns in the grid where the input elements are one of
    // text box, text area box or single select box and attempt
    // to fill in the values
    for (i=0; i < numRows; i++) {
        var currentRow = document.getElementById(groupID + '-' + i);

        // if all is well, this will produce an array of 'td' entries
        var rowSet = currentRow.children;

        // variable to track actual movement in the data array
        var k = 0;

        for (var j=0; j < rowSet.length; j++) {
            if (rowSet[j].className === "original") {
                continue;
            }

            if (rowSet[j].className === "delete") {
                continue;
            }

            // the actual input element)
            var currentElement = rowSet[j].children[0];

            if (validInputElements.indexOf(currentElement.type) < 0) {
                continue;
            }

            currentElement.value = groupEntries[i][k];

            k++;
        }
    }
};


aasaan.addJoomla = function() {
    var joomlaSet = "programadditionalinformation_set";

    var joomlaValues = [["JOOMLA_INTRO_TIME", "6 pm – 7 pm"],
        ["JOOMLA_CUSTOM_TEXT", "Limited Seats Available. Pre- Registration is recommended."],
        ["JOOMLA_SESSION_TIME", "2 batches: <br />\n Morning 06:30 AM - 09:30 AM <br />\n Evening 06:00 PM - 09:00 PM <br />\n Sunday Full day"],
        ["JOOMLA_EFLYER_URL", "None"]
    ];

    aasaan.addEntries(joomlaSet, joomlaValues);
};


aasaan.addBatchNew = function() {
    // this doesn't work. need to debug
    // reason it doesn't work is that addEntries assumes
    // inside a td, the element is available right away
    // however the batch select is wrapped inside a div
    // if addEntries is modified to handle that, this function can be used
    // instead of addBatch
    var batchSet = "programbatch_set";
    var batchValues = [["1", "6:00 AM", "8:30 AM"],
    ["2", "6:00 PM", "8:30 PM"]];

    aasaan.addEntries(batchSet, batchValues);
};

aasaan.addBatch = function() {
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

    for (i=0; i < aasaan.schedule_batch_2.children.length; i++) {
        each_item = aasaan.schedule_batch_2.children[i];
        if (each_item.innerHTML.startsWith('Evening'))
            {
                aasaan.schedule_batch_2.value = each_item.value;
                aasaan.schedule_start_time_2.value = "06:00 PM";
                aasaan.schedule_end_time_2.value = "08:30 PM";
                break;
            }
    }
};

window.addEventListener("load", function (e) {
    // do the auto population only for new schedules. leave existing schedules untouched
    if (document.URL.endsWith('/add/')) {
        aasaan.addBatch();
        aasaan.addJoomla();
    }
});
