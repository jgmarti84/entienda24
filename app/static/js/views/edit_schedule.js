// scope variables
var isMouseDown = false;
var startCell, endCell;

$(document).ready(function () {
    var tablePageIndex = 1;
    var rowsPerPage = 28;
    const tableId = "schedule-table";

    ratingToStars()

    const indexes = getTablePaginationIndexList(tableId, rowsPerPage);
    const weeks_list = [...new Set(extractTableDataArray(tableId).map(x => x.monday_week_date))]
    renderTablePage(tableId, (tablePageIndex-1) * rowsPerPage, tablePageIndex * rowsPerPage);
    renderTablePagButtons(tableId, tablePageIndex, indexes);
    renderTableTitle(tableId, tablePageIndex, weeks_list);
    // next page table button
    $(`#${tableId}-next`).click(function() {
        if (tablePageIndex < indexes[indexes.length - 1]) {
            tablePageIndex++;
        }
        renderTablePage(tableId, (tablePageIndex-1) * rowsPerPage, tablePageIndex * rowsPerPage);
        renderTablePagButtons(tableId, tablePageIndex, indexes);
        renderTableTitle(tableId, tablePageIndex, weeks_list);
    })

    $(`#${tableId}-previous`).click(function() {
        if (tablePageIndex > indexes[0]) {
            tablePageIndex--;
        }
        renderTablePage(tableId, (tablePageIndex-1) * rowsPerPage, tablePageIndex * rowsPerPage);
        renderTablePagButtons(tableId, tablePageIndex, indexes);
        renderTableTitle(tableId, tablePageIndex, weeks_list);
    })

    $(`#${tableId} td`).mousedown(function() {
        isMouseDown = true;
        startCell = $(this);
        return false;
    }).mouseover(function() {
        if (isMouseDown) {
            endCell = $(this);
            selectCellsInTable(startCell, endCell, tableId)
        }
    })
    // Individual cells deselection
    $(`#${tableId} td`).click(function() {
        if (!$(this).hasClass("B")) {
            if ($(this).hasClass("selected")) {
                $(this).removeClass("selected");
            } else {
                if ($(this).hasClass("enrolled-0")) {
                    $(this).addClass("selected");
                }
            }
        }
    })
    $(document).mouseup(function() {
        isMouseDown = false;
        var array = getElementsArrayByClass("current-selected")
        $(array).each(function() {
            $(this).removeClass("current-selected")
            $(this).addClass("selected")
        })
    });

    // Handle deselection when user clicks outside the table
    $(document).on('click', function (e) {
        if (!$(e.target).closest(`#${tableId}`).length) {
            $('.selected').removeClass('selected');
        }
    });

    $(document).on('keydown', function (e) {
        var selectedCellsArray = getElementsArrayByClass("selected")
        var value = getInputClassTypeValue(e)
        selectedCellsArray.forEach((td) => {
            var cond1 = $(td).hasClass("enrolled-1")
            var cond2 = $(td).hasClass("enrolled-2")
            if (!(cond1 || cond2)) {
                $(td).text(value)
            }
        })
    })

    $("#save-button").click(function () {
        const data = extractTableDataArray(tableId);
        const dataToSend = {data: data};
        $.post({
            type: "POST",
            url: `/save_tutor_schedule/`,
            contentType: 'application/json',
            data: JSON.stringify(dataToSend),
            success(response){
                var status = JSON.parse(response)["status"];
                if (status === "Save Successful") {
                    location.href = JSON.parse(response)["next_page"];
                } else {
                    message(JSON.parse(response)["error"], true, "schedule-table");
                }
            }
        });
    });
})