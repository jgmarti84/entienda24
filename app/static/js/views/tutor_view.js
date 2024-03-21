$(document).ready(function () {
    var tablePageIndex = 1;
    var rowsPerPage = 28;
    const tableId = "schedule-table";

    // show profile rating as stars
    ratingToStars()
    renderLastUpdate()
    // functionality to navigate through different tabs
    toggleProfileTabs()
    $(".tutor-prices-link").each(function(index, element) {
        $(element).click(function() {
            const subjectId = $(element).parent("tr").data("subjectid")
            openSubjectPricesModal(subjectId, 'tutor-prices-modal')
        })
    });
    $('.content-table.subjects-data td:nth-of-type(6)').hover(function() {
        $(this).find("p").removeClass("is-hidden")
    }, function () {
        $(this).find("p").addClass("is-hidden")
    });
    $('.content-table.subjects-data td:nth-of-type(4)').hover(function() {
        $(this).find("p").removeClass("is-hidden")
    }, function () {
        $(this).find("p").addClass("is-hidden")
    });
    closeModalEvents("tutor-prices-modal")

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
})