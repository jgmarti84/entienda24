$(document).ready(function () {
    var tablePageIndex = 1;
    var rowsPerPage = 28;
    const tableId = "schedule-table";

    ratingToStars()
    renderLastUpdate()
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

    $("#validate-info-button").click(function() {
        var dataToSend = {
          "username": $("#signup-user").val(),
          "name": $("#signup-name").val(),
          "last_name": $("#signup-last-name").val(),
          "email": $("#signup-mail").val(),
          "phone_country_code": $("select[name='phone_country_code']").val(),
          "phone_city_code": $("input[name='phone_city_code']").val(),
          "phone": $("input[name='phone']").val(),
          "csrf_token": $("#csrf_token").val()
        }
        $.post({
            type: "POST",
            url: `/update_user_data`,
            data: dataToSend,
            success(response){
                if (JSON.parse(response)["status"] === "Validate Successful") {
                    location.reload();
                }
                else {
                    message(JSON.parse(response)["error"], true, "user-info-box", "feedback");
                }
            }
        })
    })

    // save picture
    const fileInput = $("input[type=file].my_file");
    fileInput.change(function () {
        console.log("changing picture")
        if ($(this)[0].files.length > 0) {
            $('#upload-file-box .file-name').text($(this)[0].files[0].name)
            const formData = new FormData();
            const file = $(fileInput)[0].files[0];
            formData.append('file', file);
            $.post({
                type: "POST",
                url: '/upload_picture',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.status === "Upload Successful") {
                        // alert("response successful")
                        var baseURL = window.location.protocol + '//' + window.location.hostname + (window.location.port ? ':' + window.location.port : '');
                        window.location.href = baseURL + "/tutor/home?tab=perfil";
                    }
                }
            })
        }
    })

    // modify password
    $("#modify-password-button").click(function() {
        openModal($("#modify-password-modal"))
        $("#confirm-modify").click(function () {
            var dataToSend = {
                "old_password": $("#old-pass").val(),
                "new_password": $("#new-pass").val(),
                "csrf_token": $("#csrf_token").val()
            }
            $.post({
                type: "POST",
                url: `/change_password`,
                data: dataToSend,
                success(response){
                    if (JSON.parse(response)["status"] === "Modify Successful") {
                        location.reload();
                    }
                    else {
                        message(JSON.parse(response)["error"], true, "modify-password-box", "pass-feedback");
                    }
                }
            })
        })
    })
    closeModalEvents("modify-password-modal")

    // bank account details
    $("#bank-details-button").click(function() {
        var dataToSend = {
            "cbu": $("#bank-cbu").val(),
            "alias": $("#bank-alias").val(),
            "csrf_token": $("#csrf_token").val()
        }
        $.post({
            type: "POST",
            url: `/validate_bank_details`,
            data: dataToSend,
            success: function(response) {
                if (JSON.parse(response)["status"] === "Validate Successful") {
                    location.reload()
                } else {
                    message(JSON.parse(response)["error"], true, "modify-password-box", "bank-feedback");
                }
            }
        })
    })

    if ($(`#bank-cbu`).val() === "" || $(`#bank-alias`).val() === "") {
        $(`#bank-cbu`).closest(`div.transparent-box`).css("border", "2px solid red")
    }

    // Modify ratings float numbers into stars
    $(".score").each(function() {
        const n = this.innerHTML
        this.innerHTML = getStars(n)
    })

    $("#tutor-class-panel input").on('input', function() {
        var tabStatus = $(`.panel-tabs a.is-active`).data("status")
        var panelRows = $(`.panel-table tbody tr`)
        const inputString = this.value
        $(panelRows).each(function() {
            const subjectName = removeAccentsAndLowerCase($(this).find("td.subject-name-cell").text());
            const rowStatus = $(this).find("td.status-cell").data("status")
            if (tabStatus === rowStatus || tabStatus === -1) {
                if (subjectName.includes(inputString)) {
                    $(this).removeClass("is-hidden")
                }
                else {
                    $(this).addClass("is-hidden")
                }
            }
        })
    });

    $(".panel-tabs a").click(function() {
        $(".panel-tabs a").each(function() {
            $(this).removeClass("is-active")
        })
        $(this).addClass("is-active")
        var tabStatus = $(this).data("status")
        var panelRows = $(`.panel-table tbody tr`)
        if (tabStatus === -1) {
            $(panelRows).each(function() {
                $(this).removeClass("is-hidden")
            })
        } else {
            $(panelRows).each(function() {
                var rowStatus = $(this).find("td.status-cell").data("status")
                if (rowStatus === tabStatus) {
                    $(this).removeClass("is-hidden")
                } else {
                    $(this).addClass("is-hidden")
                }
            })
        }
    })

    $(".more-info-cell").click(function() {
        const row = $(this).parent('tr')
        const classId = $(row).data("classid")
        const classStatus = $(row).find("td.status-cell").data("status")
        tutorMoreInfoHandle(classId, classStatus, userType="tutor")
    })
})
