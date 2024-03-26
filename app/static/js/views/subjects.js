function tableRowUrlNavigate(tableTagId) {
    // $(`#${tableTagId} tbody tr`).on("click", function() {
    //     location.href = $(this).data("url")
    // })
    console.log('entrando')
    $("td.clickeable-cell").on("click", function() {
        location.href = $(this).parent("tr").data("url")
    })
}

$(document).ready(function() {
    $("td").click(function() {
        if ($(this).hasClass('clickeable-cell')) {
            location.href = $(this).parent("tr").data("url")
        }
    })
    var dataTable = $('#subjects-search-table').DataTable({
        dom: 'rt<"pull-left"l><"pull-right"p>',
        paging: true,         // Enable pagination
        info: false,          // Enable/Disable the info
        lengthMenu: [10, 15, 20, 25, 50, 100],
        pageLength: 15,       // Set the number of rows per page
        // responsive: true,     // Enable responsive behavior
        language: {
            lengthMenu: "Mostrar _MENU_ Materias por Página",
            zeroRecords: "No se encontraron materias",
            paginate: {
                first: "Primero",
                last: "Ultimo",
                next: "Siguiente",
                previous: "Anterior"
            }
        },
        columns: [
            { title: "Codigo Facultad", visible: false, orderable: false },
            { title: "Codigo Materia", visible: false , orderable: false },
            { title: "Materia", visible: true, orderable: true },
            { title: "Unidad Academica", visible: true, orderable: true },
            { title: "Programa", visible: true, orderable: false },
            { title: "Materia Unidecode", visible: false, orderable: false },
            // { title: "Menu", visible: true, orderable: false}
        ],
    });

    $('input[name="facultad_filter"]').on('change', function() {
        if (this.value === "0") {
            // Show all rows if no filter is selected
            dataTable.columns(0).search('').draw();
            tableRowUrlNavigate("subjects-search-table")
        } else {
            // Filter based on selected Unidad Academica
            dataTable.columns(0).search(this.value).draw();
            tableRowUrlNavigate("subjects-search-table")
        }
    })
    // $(".dropdown").on("click", function () {
    //     $(this).toggleClass("is-active");
    // })
    // $(document).on("click", function(){
    //     $(".dropdown.is-active").toggleClass("is-active");
    // })

    $('#subject-name-filter').on('input', function() {
        const converted_filter = removeAccentsAndLowerCase(this.value)
        dataTable.columns(5).search(converted_filter).draw();
        tableRowUrlNavigate("subjects-search-table")
    });

    // Filter based on default value of subject name filter and faculty radiobutton
    const converted_filter = removeAccentsAndLowerCase($('#subject-name-filter').val())
    dataTable.columns(5).search(converted_filter).draw();

    const ffilter = $('input[name="facultad_filter"]:checked').val()
    if (ffilter === "0") {
        dataTable.columns(0).search('').draw();
    } else {
        dataTable.columns(0).search(ffilter).draw();
    }
    tableRowUrlNavigate("subjects-search-table")
})