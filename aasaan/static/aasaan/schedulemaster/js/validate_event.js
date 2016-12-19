'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};

document.addEventListener("DOMContentLoaded", function(event) {
    aasaan.base_form = aasaan.base_form || document.forms[0];
    aasaan.event_name_element = document.getElementById("id_event_name");
    aasaan.program_name_element = document.getElementById("id_program");
    aasaan.event_parent_div = aasaan.event_name_element.parentNode.parentNode;
    aasaan.event_warning_node = document.createElement('div');
    aasaan.event_parent_div.appendChild(aasaan.event_warning_node);

    aasaan.event_name_element.addEventListener("input", eventNameChange, false);
});

function eventNameChange() {
    var x = aasaan.program_name_element;
    var y = aasaan.event_name_element;

    if (! y.value) {
        aasaan.event_warning_node.innerHTML = "";
        return;
    }

    if (x.options[x.selectedIndex].innerText !== "Special Event") {
        if (! aasaan.event_warning_node.innerHTML) {
            aasaan.event_warning_node.innerHTML = "<b style='color:red'>Note: Event name overrides program name in sync. It is really required only when program type is special event. Otherwise it can be left blank</b>";
        }
    }
}