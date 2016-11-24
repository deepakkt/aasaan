/**
 * Created by dpack on 22-11-2016.
 */
google.charts.load('current', {'packages':['table', 'corechart', 'bar']});
google.charts.setOnLoadCallback(drawCharts);

function filterRows(nestedArray, column, value) {
    filteredArray = [];

    for (i=0; i < nestedArray.length; i++) {
        if (nestedArray[i][column] == value) {
            filteredArray.push(nestedArray[i]);
        }
    }

    return filteredArray;
}

function stripColumns(nestedArray, columns) {
    strippedArray = [];

    for (i=0; i < nestedArray.length; i++) {
        subArray = [];
        for (j=0; j < nestedArray[i].length; j++) {
            if (columns.indexOf(j) < 0) {
                subArray.push(nestedArray[i][j]);
            }
        }
        strippedArray.push(subArray);
    }

    return strippedArray;
}

function refreshZone(zone) {
    var currentZone = document.getElementById(aasaan_irc_dashboard.zone_id).innerText;
    var clickedZone = zone;
    var clickedZoneName = document.getElementById(zone).innerText;

    if (currentZone == clickedZoneName) {
        // active zone was clicked. no action is required
        return
    }

    document.getElementById(clickedZone).parentNode.className = "active";
    document.getElementById(aasaan_irc_dashboard.zone_id).parentNode.className = "";
    aasaan_irc_dashboard.zone_id = zone;

    pageHeader = document.getElementsByClassName("page-header")[0];
    pageHeader.innerText = "IRC Dashboard - " + clickedZoneName;

    drawCharts();
}

function drawCharts() {
    zone_name = document.getElementById(aasaan_irc_dashboard.zone_id).innerText;

    drawProgramChart(zone_name);
    drawProgramFutureChart(zone_name);
    drawRoleChart(zone_name);
    drawRoleTableChart(zone_name);
    drawTeacherChart(zone_name);
    drawSectorChart(zone_name);
    drawMissingRolesChart(zone_name);
}

function drawProgramChart(zone) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'program name');
    data.addColumn('number', 'number of programs');

    programBaseData = aasaan_irc_dashboard.dashboard_data.program_counts.data;
    programBaseData = filterRows(programBaseData, 0, zone);
    programBaseData = filterRows(programBaseData, 3, 'past');
    programBaseData = stripColumns(programBaseData, [0, 3]);

    data.addRows(programBaseData);

    var options = {
        vAxis: {
            'title': 'Number of Programs',
            ticks: [2, 4, 6, 8, 10]
        },
        height: 450,
        legend: {
            position: 'none'
        }
      };

    var chart = new google.visualization.ColumnChart(document.getElementById("program-chart"));
    chart.draw(data, options);
}

function drawProgramFutureChart(zone) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'program name');
    data.addColumn('number', 'number of programs');

    programBaseData = aasaan_irc_dashboard.dashboard_data.program_counts.data;
    programBaseData = filterRows(programBaseData, 0, zone);
    programBaseData = filterRows(programBaseData, 3, 'future');
    programBaseData = stripColumns(programBaseData, [0, 3]);

    data.addRows(programBaseData);

    var options = {
        vAxis: {
            'title': 'Number of Programs',
            ticks: [2, 4, 6, 8, 10]
        },
        height: 450,
        legend: {
            position: 'none'
        }
      };

    var chart = new google.visualization.ColumnChart(document.getElementById("program-future-chart"));
    chart.draw(data, options);
}

function drawRoleChart(zone) {
 var data = new google.visualization.DataTable();
    data.addColumn('string', 'role name');
    data.addColumn('number', 'role count');

    roleData = aasaan_irc_dashboard.dashboard_data.role_summary.data;
    roleData = filterRows(roleData, 0, zone);
    roleData = stripColumns(roleData, [0]);

    data.addRows(roleData);

    var chart = new google.visualization.PieChart(document.getElementById('role-chart'));
    var options = {
        height: 450,
        legend: {
            position: 'none'
        }

    };

    chart.draw(data, options);

}


function drawRoleTableChart(zone) {
 var data = new google.visualization.DataTable();
    data.addColumn('string', 'role name');
    data.addColumn('number', 'role count');

    roleData = aasaan_irc_dashboard.dashboard_data.role_summary.data;
    roleData = filterRows(roleData, 0, zone);
    roleData = stripColumns(roleData, [0]);

    data.addRows(roleData);

    var table = new google.visualization.Table(document.getElementById('role-table-chart'));

    var options = {
        cssClassNames: {
            tableRow: 'table-text-style',
            oddTableRow: 'table-text-style'
        },
        showRowNumber: true,
        width: '100%',
        height: '100%'
        };

    table.draw(data, options);
}

function drawZoneSummaryChart(zone) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'zone_name');
    data.addColumn('number', 'center count');
    data.addColumn('number', 'teacher count');
    data.addColumn('number', 'program count');

    zoneSummaryBaseData = aasaan_irc_dashboard.dashboard_data.zone_summary.data;
    zoneSummaryBaseData = filterRows(zoneSummaryBaseData, 0, zone);

    data.addRows(zoneSummaryBaseData);

    var options = {
        vAxis: {
            'title': 'Value'
        },
        height: 400,
      };

    var chart = new google.visualization.ColumnChart(document.getElementById("zone-summary-chart"));
    chart.draw(data, options);
}

function  drawTeacherChart(zone) {
    var data = new google.visualization.DataTable();

    data.addColumn('string', 'name');

    teacherData = aasaan_irc_dashboard.dashboard_data.teachers;
    teacherData = filterRows(teacherData, 0, zone);
    teacherData = stripColumns(teacherData, [0])

    data.addRows(teacherData);

    var table = new google.visualization.Table(document.getElementById('teacher-chart'));

    var options = {
        cssClassNames: {
            tableRow: 'table-text-style',
            oddTableRow: 'table-text-style'
        },
        showRowNumber: true,
        width: '100%',
        height: '100%'
        };

    table.draw(data, options);
}


function  drawSectorChart(zone) {
    var data = new google.visualization.DataTable();

    data.addColumn('string', 'name');
    data.addColumn('string', 'centers');

    sectorCoordinatorsBaseData = aasaan_irc_dashboard.dashboard_data.sector_coordinators.data;
    sectorCoordinatorsBaseData = filterRows(sectorCoordinatorsBaseData, 0, zone);
    sectorCoordinatorsBaseData = stripColumns(sectorCoordinatorsBaseData, [0])

    data.addRows(sectorCoordinatorsBaseData);

    var table = new google.visualization.Table(document.getElementById('sector-chart'));

    var options = {
        cssClassNames: {
            tableRow: 'table-text-style',
            oddTableRow: 'table-text-style'
        },
        showRowNumber: true,
        width: '100%',
        height: '100%'
        };

    table.draw(data, options);

}


function drawMissingRolesChart(zone) {
    var data = new google.visualization.DataTable();

    data.addColumn('string', 'center');
    data.addColumn('string', 'available roles');
    data.addColumn('string', 'missing roles');

    missingRolesBaseData = aasaan_irc_dashboard.dashboard_data.missing_roles.data;
    missingRolesBaseData = filterRows(missingRolesBaseData, 0, zone);
    missingRolesBaseData = stripColumns(missingRolesBaseData, [0]);

    data.addRows(missingRolesBaseData);

    var table = new google.visualization.Table(document.getElementById('missing-roles-chart'));

    table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
}