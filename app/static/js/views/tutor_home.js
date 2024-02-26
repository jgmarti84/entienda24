$(document).ready(function () {
    var tablePageIndex = 1;
    var rowsPerPage = 28;
    const tableId = "schedule-table";

    ratingToStars()
    toggleProfileTabs()
    $(".tutor-prices-link").click(function() {
        const subject_id = $(this).parent("tr").data("subject");
        openSubjectPricesModal(subject_id, 'tutor-prices-modal')
    })
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