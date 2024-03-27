function getSubjectsTableData(tableTagId) {
    var tableData = []
    $(`#${tableTagId} tbody tr`).each(function (rowIndex, row) {
        // Object to store cell data for each row
        var rowData = [];
        $(row).find('td').each(function (colIndex, cell) {
            rowData.push($(cell).text())
        });
        // Add the row object to the table data array
        tableData.push(rowData);
    });
    return tableData
}

$(document).ready(function () {
    ratingToStars()
    renderLastUpdate()

    var tableId = 'classes-table'
    // Add click event to delete buttons
    $('#classes-table tbody').on('click', '.delete', function () {
        // var row = tutorSubjectsTable.row($(this).parents('tr'));
        var row = $(this).parents("tr")

        // Confirm deletion
        if (confirm('Está seguro que quiere sacar esta materia?')) {
            $(row).remove();
        }
    });

    $('#add-subject-button').on('click', function() {
        const subjectId = $('#classes-select').val()
        var tutorSubjectsTable = getSubjectsTableData(tableId)
        var exists = tutorSubjectsTable.some(function(rowData) {
            return rowData[1] === String(subjectId);
        });
        if (!exists) {
            var newRow = `<tr data-subject="subjectId">`
            newRow += `<td class="is-hidden">${$("#classes-select").find(":selected").data("facultyid")}</td>`
            newRow += `<td class="is-hidden">${$("#classes-select").val()}</td>`
            newRow += `<td>${$("#classes-select").find(":selected").data("subjectname")}</td>`
            newRow += `<td>${$("#classes-select").find(":selected").data("facultyname")}</td>`
            newRow += `<td class="editable" contenteditable="true">0</td>`
            newRow += `<td class="editable" contenteditable="true"></td>`
            newRow += `<td><button class="delete has-background-danger"></button></td>`
            newRow += `</tr>`

            // Add the new row to the DataTable
            $('#classes-table tbody').append(newRow)
        } else {
            message(`La materia ${$('#classes-select').find(':selected').data('subjectname')} ya se encuentra agregada!`, true, "classes-select");
        }
    });

    $("#save-button, #save-button-mobile").click(function() {
        const dataToSend = {tutor_subjects_array: getSubjectsTableData(tableId)};
        console.log(dataToSend)
        $.post({
            type: "POST",
            url: `/save_tutor_sutbjects/`,
            contentType: 'application/json',
            data: JSON.stringify(dataToSend),
            success(response) {
                var status = JSON.parse(response)["status"];
                if (status === "Save Successful") {
                    location.href = JSON.parse(response)["next_page"];
                } else {
                    message(JSON.parse(response)["error"], true, "classes-select");
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                alert(xhr.responseText);
            }
        });
    })
})