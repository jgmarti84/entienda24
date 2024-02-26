var formId = 0;
var isMouseDown = false;

function updateStudentInfoBox(nStudents) {
    $("#other-students-info-box").empty()
    for (var i=2; i<=nStudents; i++) {
        $("#other-students-info-box").append(createStudentInfo(i, false, false, false, true))
    }
}

$(document).ready(function () {
    ratingToStars()

    var isValid = checkValidValues(formId);
    if (!isValid) {formId--}

    updateForm(formId);
    updatePriceDetail(formId);

    $("#next-button-p").click(function() {
        formId++
        var isValid = checkValidValues(formId);
        if (!isValid) {formId--}
        if (formId === 3) {
            var dataToSend = $("#other-students-info-box input").map(function(index, item) {return $(item).val()}).get()
            const request_url = "/validate_students/"
            makeStringifyPostRequest(request_url, dataToSend, function(error, response) {
                if (error) {
                    console.error('Error in the fourth request: ', error)
                    return
                }
                var status = JSON.parse(response)["status"]
                if (status === "Validate Successful") {
                    var students = JSON.parse(response)["students"]
                    updateForm(formId);
                    updatePriceDetail(formId)
                    var sIndex = 2
                    $.each(students, function(index, student) {
                        $(`#student-username-${sIndex}`).data("student", student.student_id)
                    })
                } else {
                    message(JSON.parse(response)["error"], true, "logger-section")
                    formId--
                    updateForm(formId)
                    updatePriceDetail(formId)
                }
            })
        } else {
            updateForm(formId);
            updatePriceDetail(formId);
        }
    })

    $("#back-button-p").click(function() {
        formId--;
        updateForm(formId);
        updatePriceDetail(formId);
    });

    $("#subject-selector").change(function() {
        updatePriceDetail(formId)
    })

    $("#class-type-selector").change(function() {
        updatePriceDetail(formId)
    })

    $('#step3 input').on('input', function() {
        updateStudentInfoBox(parseInt($(this).val()))
        updatePriceDetail(formId)
    })

    $('#step4 input').on('input', function() {
        updatePriceDetail(formId)
    })

    $("#confirm-button").click(function() {
        var tablePageIndex = 1;
        var rowsPerPage = 28;
        const tableId = "schedule-table";

        openModal($("#schedule-log-modal"))
        closeModalEvents("schedule-log-modal")

        const classType =  $('#class-type-selector').val().toUpperCase();
        const indexes = getTablePaginationIndexList(tableId, rowsPerPage);
        const weeks_list = [...new Set(extractTableDataArray(tableId).map(x => x.monday_week_date))]

        renderTablePage(tableId, (tablePageIndex-1) * rowsPerPage, tablePageIndex * rowsPerPage)
        renderTablePagButtons(tableId, tablePageIndex, indexes)
        renderTableTitle(tableId, tablePageIndex, weeks_list)

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


        $("#add-availability-button").click(function() {
            var selectedCells = getElementsArrayByClass("selected")
            var cellsNotAdded = []
            $(selectedCells).each(function (index, cell) {
                var classTypeCond = $(cell).hasClass(classType) || $(cell).hasClass("VyP")
                var availabilityCond = $(cell).hasClass("enrolled-0")
                if (availabilityCond && classTypeCond) {
                    $(cell).addClass("time-added")
                } else {
                    cellsNotAdded.push(cell)
                }
                $(cell).removeClass("selected")
            })
            var classesArray = classRowsCreation(getElementsArrayByClass("time-added"))
            $("#logged-availability-table tbody").empty()
            $(classesArray).each(function(index, rowClass) {
                var firstCellInfo = getCellInfo(rowClass[0])
                var lastCellInfo = getCellInfo(rowClass[rowClass.length - 1])
                var classDate =  new Date(firstCellInfo[4]);
                classDate.setDate(classDate.getUTCDate() + firstCellInfo[2])

                var row = "<tr>"
                row += `<td>${transformDate(classDate)}</td>`
                row += `<td>${timeIndexParser[firstCellInfo[3]]} - ${timeIndexParser[lastCellInfo[3]+1]}</td>`
                row += "</tr>"
                $("#logged-availability-table tbody").append(row)
            })
        })

        $("#remove-availability-button").click(function() {
            var selectedCells = getElementsArrayByClass("selected")

            $(selectedCells).each(function(index, cell) {
                $(cell).removeClass("time-added")
                $(cell).removeClass("selected")
            })

            var classesArray = classRowsCreation(getElementsArrayByClass("time-added"))
            $("#logged-availability-table tbody").empty()
            $(classesArray).each(function(index, rowClass) {
                var firstCellInfo = getCellInfo(rowClass[0])
                var lastCellInfo = getCellInfo(rowClass[rowClass.length - 1])
                var classDate =  new Date(firstCellInfo[4]);
                classDate.setDate(classDate.getUTCDate() + firstCellInfo[2])

                var row = "<tr>"
                row += `<td>${transformDate(classDate)}</td>`
                row += `<td>${timeIndexParser[firstCellInfo[3]]} - ${timeIndexParser[lastCellInfo[3]+1]}</td>`
                row += "</tr>"
                $("#logged-availability-table tbody").append(row)
            })
        })

        $("#confirm-hours-button").click(function() {
            const tutorId = $("#logger-section > h1").data("tutorid");
            const hours = $('#step4 input').val();
            const request_url = `/validate_class_log/${tutorId}`;
            var timeSlots = []
            $(getElementsArrayByClass("time-added")).each(function(index, element) {timeSlots.push(getCellInfo(element))});
            console.log(timeSlots)
            var dataToSend = {slots: timeSlots, hours: hours}
            makeStringifyPostRequest(request_url, dataToSend, function(error5, response5) {
                if (error5) {
                    console.error('Error in the fifth request: ', error5)
                    return
                }
                handleScheduleValidationRequestCompletion(response1, response2, response3, response4, response5)
            })

        })

    })
})