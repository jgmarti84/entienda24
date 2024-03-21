var formId = 0;
var isMouseDown = false;
var scheduleValidated = false;
var modalOpen = false;
var students;
var loggedIds;

function updateStudentInfoBox(nStudents) {
    $("#other-students-info-box").empty();
    for (var i=2; i<=nStudents; i++) {
        $("#other-students-info-box").append(createStudentInfo(i, false, false, false, true));
    }
}

$(document).ready(function () {
    ratingToStars();

    var isValid = checkValidValues(formId);
    if (!isValid) {formId--}

    updateForm(formId);
    updatePriceDetail(formId);

    $("#next-button-p").click(function() {
        formId++;
        var isValid = checkValidValues(formId);
        if (!isValid) {formId--}
        if (formId === 3) {
            var dataToSend = $("#other-students-info-box input").map(function(index, item) {return $(item).val()}).get();
            const request_url = "/validate_students/";
            makeStringifyPostRequest(request_url, dataToSend, function(error, response) {
                if (error) {
                    console.error('Error in the fourth request: ', error);
                    return
                }
                var status = response["status"];
                if (status === "Validate Successful") {
                    students = response["students"];
                    updateForm(formId);
                    updatePriceDetail(formId);
                    var sIndex = 2;
                    $.each(students, function(index, student) {
                        $(`#student-info-${sIndex}`).data("student", student.id);
                    })
                } else {
                    message(response["error"], true, "logger-section");
                    formId--;
                    updateForm(formId);
                    updatePriceDetail(formId);
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
        updatePriceDetail(formId);
    })

    $("#class-type-selector").change(function() {
        updatePriceDetail(formId);
    })

    $('#step3 input').on('input', function() {
        updateStudentInfoBox(parseInt($(this).val()))
        updatePriceDetail(formId);
    })

    $('#step4 input').on('input', function() {
        updatePriceDetail(formId);
    })
    $(document).on('click', '#confirm-button, #modify-hours-button', function(event) {
        var tablePageIndex = 1;
        var rowsPerPage = 28;
        const tableId = "schedule-table";

        openModal($("#schedule-log-modal"))
        modalOpen = true
        let cellsElements = updateHoursConfirmButton($('#step4 input').val())

        const modalTagId = "schedule-log-modal";
        $(`#${modalTagId} .modal-background`).click(function () {
            closeModal($(this).closest(".modal"));
            $(`#${tableId} td`).removeClass("time-added");
            $("#logged-availability-table tbody").empty();
            modalOpen = false;
        })
        $("#close-modal-button").click(function () {
            closeModal($(`#${modalTagId}`).closest(".modal"));
            $(`#${tableId} td`).removeClass("time-added");
            $("#logged-availability-table tbody").empty();
            modalOpen = false;
        })
        $(document).on("keydown", function (event) {
            let key = (event.keyCode ? event.keyCode : event.which);
            if (key === 27) {
                closeModal($(`#${modalTagId}`).closest(".modal"));
                $(`#${tableId} td`).removeClass("time-added");
                $("#logged-availability-table tbody").empty();
                modalOpen = false;
            }
        })

        const classType =  $('#class-type-selector').val().toUpperCase();
        const indexes = getTablePaginationIndexList(tableId, rowsPerPage);
        const weeks_list = [...new Set(extractTableDataArray(tableId).map(x => x.monday_week_date))];

        renderTablePage(tableId, (tablePageIndex-1) * rowsPerPage, tablePageIndex * rowsPerPage);
        renderTablePagButtons(tableId, tablePageIndex, indexes);
        renderTableTitle(tableId, tablePageIndex, weeks_list);

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
                selectCellsInTable(startCell, endCell, tableId);
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
            var array = getElementsArrayByClass("current-selected");
            $(array).each(function() {
                $(this).removeClass("current-selected");
                $(this).addClass("selected");
            })
        });

        // Handle deselection when user clicks outside the table
        $(document).on('click', function (e) {
            if (!$(e.target).closest(`#${tableId}`).length) {
                $('.selected').removeClass('selected');
            }
        });
        $("#add-availability-button").click(function() {
            var selectedCells = getElementsArrayByClass("selected");
            var cellsNotAdded = [];
            $(selectedCells).each(function (index, cell) {
                var classTypeCond = $(cell).hasClass(classType) || $(cell).hasClass("VyP");
                var availabilityCond = $(cell).hasClass("enrolled-0");
                if (availabilityCond && classTypeCond) {
                    $(cell).addClass("time-added");
                } else {
                    cellsNotAdded.push(cell);
                }
                $(cell).removeClass("selected");
            })
            let cellsElements = updateHoursConfirmButton($('#step4 input').val())
            var classesArray = classRowsCreation(cellsElements);
            $("#logged-availability-table tbody").empty();
            $(classesArray).each(function(index, rowClass) {
                var firstCellInfo = getCellInfo(rowClass[0]);
                var lastCellInfo = getCellInfo(rowClass[rowClass.length - 1]);
                var classDate =  new Date(firstCellInfo[4]);
                classDate.setDate(classDate.getUTCDate() + firstCellInfo[2]);

                var row = "<tr>";
                row += `<td>${transformDate(classDate)}</td>`;
                row += `<td>${timeIndexParser[firstCellInfo[3]]} - ${timeIndexParser[lastCellInfo[3]+1]}</td>`;
                row += "</tr>";
                $("#logged-availability-table tbody").append(row);
            })
        })

        $("#remove-availability-button").click(function() {
            var selectedCells = getElementsArrayByClass("selected");

            $(selectedCells).each(function(index, cell) {
                $(cell).removeClass("time-added");
                $(cell).removeClass("selected");
            })
            let cellsElements = updateHoursConfirmButton($('#step4 input').val())
            var classesArray = classRowsCreation(cellsElements)
            $("#logged-availability-table tbody").empty();
            $(classesArray).each(function(index, rowClass) {
                var firstCellInfo = getCellInfo(rowClass[0]);
                var lastCellInfo = getCellInfo(rowClass[rowClass.length - 1]);
                var classDate =  new Date(firstCellInfo[4]);
                classDate.setDate(classDate.getUTCDate() + firstCellInfo[2]);

                var row = "<tr>";
                row += `<td>${transformDate(classDate)}</td>`;
                row += `<td>${timeIndexParser[firstCellInfo[3]]} - ${timeIndexParser[lastCellInfo[3]+1]}</td>`;
                row += "</tr>";
                $("#logged-availability-table tbody").append(row);
            })
        })
    })
    $("#confirm-hours-button").click(function() {
        if (modalOpen) {
            const tutorId = $("#logger-section > h1").data("tutorid");
            const hours = $('#step4 input').val();
            const classType =  $('#class-type-selector').val();
            const request_url = `/validate_class_log/${tutorId}`;
            var timeSlots = [];
            $(getElementsArrayByClass("time-added")).each(function(index, element) {timeSlots.push(getCellInfo(element))});
            var dataToSend = {slots: timeSlots, hours: hours, class_type: classType};
            makeStringifyPostRequest(request_url, dataToSend, function(error, response) {
                if (error) {
                    console.error('Error in the fifth request: ', error);
                    return
                }
                var status = JSON.parse(response)["status"];
                if (status === "Validate Successful") {
                    scheduleValidated = true;
                    closeModal($("#add-availability-button").closest(".modal"));
                    $("#log-class-button").removeClass("is-hidden");
                    $("#confirm-button").addClass("is-hidden");
                    $("#modify-hours-button").removeClass("is-hidden");
                } else {
                    message(JSON.parse(response)["error"], true, "availability-box", messageId="schedule-modal-feedback");
                    scheduleValidated = false;
                }
            })
        }
    });
    $("#log-class-button").click(function() {
        if (scheduleValidated) {
            const tutorId = $("#logger-section > h1").data("tutorid");
            var classesArray = classRowsCreation(getElementsArrayByClass("time-added"))
            var scheduleData = transformClassRowsData(classesArray)
            var subjectId = $("#subject-selector").val()
            var classType = $('#class-type-selector').val().toUpperCase()

            const dataToSend = {
                students: students,
                subject_id: subjectId,
                schedule_data: scheduleData,
                class_type: classType,
                tutor_id: tutorId,
            };
            var post_url = `/class_log_save`;
            makeStringifyPostRequest(post_url, dataToSend, function(error, response) {
                if (error) {
                    console.error('Error in the request: ', error);
                    return
                }
                loggedIds = response.logged_classes
                $("#payment-file-timer h1").text(`Total a pagar: ${$("#last-step p.is-pulled-right").text()}`)
                var paymentModalTagId = "upload-payment-modal"
                openModal($(`#${paymentModalTagId}`))
                $('.simple-timer').simpletimer({
                    day: 0,
                    dayDom: '.timer-day',
                    hour: 0,
                    hourDom: '.timer-hour',
                    minute: 10,
                    minuteDom: '.timer-minute',
                    second: 0,
                    secondDom: '.timer-second',
                    millisecond: 0,
                    millisecondDom: '.timer-millisecond',
                    pause: '#pause_btn',
                    endFun: function() {
                        makeStringifyPostRequest('/class_log_remove', loggedIds, function(error, response) {
                            closeModal($(`#${paymentModalTagId}`))
                        })
                    }
                });
                $(`#${paymentModalTagId} .modal-background`).click(function () {
                    closeModal($(this).closest(".modal"));
                    makeStringifyPostRequest('/class_log_remove', loggedIds, function(error, response) {
                        closeModal($(`#${paymentModalTagId}`))
                    })
                })
                $(`#${paymentModalTagId} button.modal-close`).click(function () {
                    closeModal($(`#${paymentModalTagId}`).closest(".modal"));
                    makeStringifyPostRequest('/class_log_remove', loggedIds, function(error, response) {
                        closeModal($(`#${paymentModalTagId}`))
                    })
                })
                $(document).on("keydown", function (event) {
                    let key = (event.keyCode ? event.keyCode : event.which);
                    if (key === 27) {
                        makeStringifyPostRequest('/class_log_remove', loggedIds, function(error, response) {
                            closeModal($(`#${paymentModalTagId}`))
                        })
                    }
                })
            })
        }
    })

    const fileInput = $("#upload-file-box input[type=file]");
    fileInput.change(function () {
        if ($(this)[0].files.length > 0) {
            $('#upload-file-box .file-name').text($(this)[0].files[0].name)
        }
    })
    $(`#upload-file`).on('click', function () {
        const formData = new FormData();
        const file = $(fileInput)[0].files[0];
        formData.append('file', file);
        formData.append('loggedIds', JSON.stringify(loggedIds));
        const post_url = '/class_log_confirm'
        $.post({
            type: 'POST',
            url: post_url,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.status === "Confirm Successful") {
                    setTimeout(function() {
                        var baseURL = window.location.protocol + '//' + window.location.hostname + (window.location.port ? ':' + window.location.port : '');
                        window.location.href = baseURL;
                    }, 60000);
                    $("#payment-file-timer").addClass("is-hidden")
                    $("#confirmation-message").removeClass("is-hidden")
                } else {
                    message(response.error, true, "upload-payment-modal", "payment-modal-feedback")
                }

            },
            error: function (response) {
                alert(response.error)
            }
        });
    })
})