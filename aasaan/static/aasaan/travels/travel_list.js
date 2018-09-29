/**
 * Created by manimaran on 21-12-2016.
 */

(function($) {
$(document).ready(function() {
    reload();
});



function reload(){
     var url = "/admin/travels/ticketlist_refresh?zone=null"
//     url = url+'zone='+$('#id_zone').val()
    var options =  {
        responsive: true,
        "destroy": true,
       "lengthMenu": [ [10, 25, 50, -1], [10, 25, 50, "All"] ],
        autoFill: true,
        dom: 'Blfrtip',
        buttons: [
            {
                extend: 'copyHtml5',
                exportOptions: {
                    columns: [ 0, ':visible' ]
                }
            },
            {
                extend: 'excelHtml5',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'pdfHtml5',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                download: 'open',
                exportOptions: {
                    columns: ':visible'
                }
            },
            'print',
            'colvis'
        ],
        scrollY: 400,
        colReorder: true,
        "ajax": url,
        "columns": [
            { "data": "ticket_number",
                 "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                  $(nTd).html("<a target='_blank' href='/admin/travels/travelrequest/"+oData.id+"/change/'>"+oData.ticket_number+"</a>");
                  }
            },
            { "data": "passanger_name"},
            { "data": "source" },
            { "data": "destination" },
            { "data": "onward_date" },
            { "data": "travel_mode" },
            { "data": "travel_class" },
            { "data": "status" },
            { "data": "invoice_no" },
            { "data": "amount" },
            { "data": "created_by"},
            { "data": "zone"},
        ],
        columnDefs: [
            {   "targets": [6],
                "visible": false,
                "searchable": false
            }
        ],
    }
    var table = $('#passanger_table').DataTable(options)
    table.ajax.reload()
}
})(jQuery);

