function message(status, shake=false, id="", messageId="feedback") {
  if (shake) {
    $("#"+id).effect("shake", {direction: "right", times: 2, distance: 8}, 250);
  }
  document.getElementById(messageId).innerHTML = status;
  $(`#${messageId}`).show().delay(3000).fadeOut();
}

function error(type) {
  $("."+type).css("border-color", "#E14448");
}

/**
 * @param {string} className - name of the class
 * @return {object[]} - Array of all elements with the className class
 */
function getElementsArrayByClass(className) {
    // Select all elements with the class 'selected' using jQuery
    var selElements = $(`.${className}`);

    // Convert the jQuery selection to array
    var selElementsArray = selElements.toArray();
    return selElementsArray
}

/**
 * @param {string} tableId - The tag id of the table to extract data from
 */
function extractTableDataArray(tableId) {
    // Array to store the table data
    var tableData = [];

    // Iterate through each row in the table
    $(`#${tableId} tr`).each(function (rowIndex, row) {
        if (rowIndex > 0) {
            // Object to store cell data for each row
            var rowData = {};
            var availabilityDays = [];
            // Iterate through each cell in the row
            $(row).find('td').each(function (colIndex, cell) {
                // Add cell data to the row object
                if (colIndex < 5 || colIndex === 12) {
                    rowData[scheduleColumnsParser[colIndex]] = $(cell).text();
                } else {
                    availabilityDays.push($(cell).text());
                }
            });
            // Add the row object to the table data array
            rowData["availability_days"] = availabilityDays;
            tableData.push(rowData);
        }
    });
    return tableData
}

function formatName(str) {
    var names = str.split(" ")
    var newNames = []
    $(names).each(function() {
        newNames.push(this.charAt(0).toUpperCase() + this.slice(1))
    })
    return newNames.join(" ")
}

function formatPrice(val) {
    return val.toLocaleString('es-ar', {style: 'currency', currency: 'ARS', minimumFractionDigits: 2})
}

function diff_hours(dt2, dt1) {
    var diff =(dt2.getTime() - dt1.getTime()) / 1000;
    diff /= 3600;
    return Math.abs(Math.round(diff));
}

function transformDate(date) {
    var year = date.getUTCFullYear();
    var month = String(date.getUTCMonth() + 1).padStart(2, '0'); // Adding 1 to month because it's zero-based
    var day = String(date.getUTCDate()).padStart(2, '0'); // Adding zero padding to single-digit days

    var formattedDate = `${day}-${month}-${year}`;
    return formattedDate
}