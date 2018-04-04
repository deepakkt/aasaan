/**
 * Created by manimaran on 21-12-2016.
 */
button_submit = null;
(function($) {
$(document).ready(function() {
    reload();
});

function reload(){
     var url = "/admin/ipcaccounts/treasurer_refresh?"
     url = url+'zone='+$('#id_zone').val()
     console.log(url)
    var options =  {
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
            { "data": "name",
             "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html("<a target='_blank' href='/admin/contacts/contact/"+oData.id+"/change/'>"+oData.name+"</a>");
              }
        },
            { "data": "phone_number" },
            { "data": "primary_email" },
            { "data": "account_holder" },
            { "data": "bank_name" },
            { "data": "branch_name" },
            { "data": "account_number" },
            { "data": "ifsc_code" },
            { "data": "zone" },
            { "data": "center" },
            { "data": "roles" },
        ]
    }

    var table = $('#example').DataTable(options)
    table.ajax.reload()


}
button_submit = reload;
})(jQuery);

