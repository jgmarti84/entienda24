$(document).ready(function () {
    ratingToStars()

    var tutorSubjectsTable = $('#classes-table').DataTable({
        dom: 'rt',
        paging: false,
        autoWidth: false,
        columns: [
            {title: "Codigo Unidad Academica", visible: false, orderable: false},
            {title: "Codigo Materia", visible: false, orderable: false},
            {title: "Materia", visible: true, orderable: false},
            {title: "Unidad Academica", visible: true, orderable: false},
            {title: "Precio de Referencia ($)", visible: true, orderable: false},
            {title: "Comentario", visible: true, orderable: false},
            {title: "Eliminar", visible: true, orderable: false},
        ],
    });

    // Add click event to delete buttons
    $('#classes-table tbody').on('click', '.delete', function () {
        var row = tutorSubjectsTable.row($(this).parents('tr'));

        // Confirm deletion
        if (confirm('Está seguro que quiere sacar esta materia?')) {
            row.remove().draw();
        }
    });

    $('#add-subject-button').on('click', function() {
        const subjectId = $('#classes-select').val()
        var exists = tutorSubjectsTable.rows().data().toArray().some(function(rowData) {
            return rowData[1] === String(subjectId);
        });

        if (!exists) {
            var newRow = [
                String($('#classes-select').find(':selected').data('facultyid')),
                String($('#classes-select').val()),
                String($('#classes-select').find(':selected').data('subjectname')),
                String($('#classes-select').find(':selected').data('facultyname')),
                0,
                "",
                `<td><button class="delete has-background-danger"></button></td>`
            ]
            // Add the new row to the DataTable
            var subjectRow = tutorSubjectsTable.row.add(newRow).draw().node();
            $(subjectRow).find('td:eq(2), td:eq(3)').addClass('editable').attr('contenteditable', 'true');
            // Enable cell editing for specific columns
            $('#classes-table tbody').on('blur', 'td.editable', function () {
                var cell = tutorSubjectsTable.cell(this);
                cell.data($(this).text());
            });
        } else {
            message(`La materia ${$('#classes-select').find(':selected').data('subjectname')} ya se encuentra agregada!`, true, "classes-select");
            // alert('La materia ya se encuentra agregada!');
        }
    });

    $("#save-button").click(function() {
        const dataToSend = {tutor_subjects_array: tutorSubjectsTable.rows().data().toArray()};
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