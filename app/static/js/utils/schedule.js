const timeIndexParser = {
    "0": "8:00", "1": "8:30", "2": "9:00", "3": "9:30", "4": "10:00", "5": "10:30", "6": "11:00", "7": "11:30",
    "8": "12:00", "9": "12:30", "10": "13:00", "11": "13:30", "12": "14:00", "13": "14:30", "14": "15:00", "15": "15:30",
    "16": "16:00", "17": "16:30", "18": "17:00", "19": "17:30", "20": "18:00", "21": "18:30", "22": "19:00", "23": "19:30",
    "24": "20:00", "25": "20:30", "26": "21:00", "27": "21:30", "28": "22:00"
}
const scheduleColumnsParser = {
    0: "tutor_id", 1: "monday_week_date", 2: "week_index", 3: "time_slot", 4: "time_index", 5: "availability_1",
    6: "availability_2", 7: "availability_3", 8: "availability_4", 9: "availability_5", 10: "availability_6",
    11: "availability_7", 12: "year_index"
}
/**
 * @param {string} tableId - The id of the <table> tag.
 * @param {number} startIndex - The initial row index to render
 * @param {number} endIndex - The final row index to render
 */
function renderTablePage(tableId, startIndex, endIndex) {

    var rows = $(`#${tableId} tbody tr`);
    rows.each(function(index, row) {
        if ($(row).index() < startIndex || $(row).index() >= endIndex) {
            $(row).addClass("is-hidden")
        } else {
            $(row).removeClass("is-hidden")
        }
    })
}


/**
 * @param {string} tableId - The id of the table tag
 * @param {number} rowsPerPage - The number of rows to be shown in a rendered page
 * @return {number[]} indexList - A list of integers ordered from 1 to the max index pagination for the table attributes
 */
function getTablePaginationIndexList(tableId, rowsPerPage) {
    var rows = $(`#${tableId} tbody tr`);
    var nRows = rows.length;
    var maxIndex = Math.floor(nRows / rowsPerPage) + 1;
    if (nRows % rowsPerPage === 0) {
        maxIndex--;
    }

    var indexList = []
    for (var i = 1; i <= maxIndex; i++) {
        indexList.push(i);
    }
    return indexList
}

/**
 * @param {string} tableId - The id of the table tag.
 * @param {number} tablePageIndex -
 * @param {number[]} tableIndexList -
 */
function renderTablePagButtons(tableId, tablePageIndex, tableIndexList) {
    var pagPrev = $(`#${tableId}-previous a`);
    var pagNext = $(`#${tableId}-next a`);
    if (tablePageIndex === tableIndexList[0]) {
        $(pagPrev).addClass("disabled");
    } else {
        $(pagPrev).removeClass("disabled");
    }
    if (tablePageIndex === tableIndexList[tableIndexList.length - 1]) {
        $(pagNext).addClass("disabled");
    } else {
        $(pagNext).removeClass("disabled");
    }
}

function renderTableTitle(tableId, tablePageIndex, titles) {
    var week = titles[tablePageIndex-1]
    week = week.split("-")
    week = `${week[2]}-${week[1]}-${week[0]}`

    $(`#${tableId}-title`).text(`Semana del ${week}`)
}

/**
 * @param {object} startTd - The starting td element of the selection.
 * @param {object} endTd - The end td element of the selection.
 * @param {string} tableTagId - The table tag id
 */
function selectCellsInTable(startTd, endTd, tableTagId) {
    // Clear previous selection
    $(`#${tableTagId} td`).removeClass("current-selected");

    // Get table coordinates from start to end of selection cells
    var startX = startTd.parent().index();
    var startY = startTd.index();
    var endX = endTd.parent().index();
    var endY = endTd.index();

    // Add class 'selected' to those cells in the table
    for (var i = Math.min(startX, endX); i <= Math.max(startX, endX); i++) {
        for (var j = Math.min(startY, endY); j <= Math.max(startY, endY); j++) {
            var td = $("#" + tableTagId + " tbody tr:eq(" + i + ") td:eq(" + j + ")")
            if (!$(td).hasClass("B")) {
                $(td).addClass("current-selected");
            }

        }
    }
}

/**
 * @param {object} key - The key element from a keydown event
 * @return {string} - the parsed value of the class type to fill the schedule with
 */
function getInputClassTypeValue(key) {
    // if (key.key.toUpperCase() === 'V' || key.key.toUpperCase() === 'P' || key.key.toUpperCase() === 'A') {
    //     var value = key.key.toUpperCase()
    //     if (value === 'A') {
    //         value = 'VyP'
    //     }
    // } else {
    //     if (key.key === ' ' || key.key === 'Delete' || key.key === 'Backspace') {
    //         var value = ""
    //     }
    // }
    // return value
    if (key.toUpperCase() === 'V' || key.toUpperCase() === 'P' || key.toUpperCase() === 'A') {
        var value = key.toUpperCase()
        if (value === 'A') {
            value = 'VyP'
        }
    } else {
        if (key === ' ' || key === 'Delete' || key === 'Backspace') {
            var value = ""
        }
    }
    return value
}