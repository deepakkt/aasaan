/**
 * Created by manimaran on 21-12-2016.
 */

(function($) {
$(document).ready(function() {
    reload();
});



function reload(){
     var url = "/admin/travels/passanger_refresh?"

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
            { "data": "name"},
            { "data": "t_no" },
            { "data": "category" },
            { "data": "gender" },
            { "data": "age" },
            { "data": "phone_number" },
            { "data": "primary_email" },
            { "data": "id_proof_type" },
            { "data": "id_proof_number" },
            { "data": "zone" },
        ],
        columnDefs: [
            {   "targets": [1,2,7,8],
                "visible": false,
                "searchable": false
            }
        ],
    }
    var table = $('#passanger_table').DataTable(options)
    table.ajax.reload()
}
})(jQuery);

