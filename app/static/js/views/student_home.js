$(document).ready(function () {
    toggleProfileTabs()
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
                        alert("response successful")
                        var baseURL = window.location.protocol + '//' + window.location.hostname + (window.location.port ? ':' + window.location.port : '');
                        window.location.href = baseURL + "/student/home?tab=perfil";
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
                    console.log(response)
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

    // Modify ratings float numbers into stars
    $(".score").each(function() {
        const n = this.innerHTML
        this.innerHTML = getStars(n)
    })

    $("#student-class-panel input").on('input', function() {
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
        $(row).addClass("active")
        const classId = $(row).data("classid")
        const subjectId = $(row).data("subjectid")
        const classStatus = $(row).data("status")
        const tutorId = $(row).data("tutorid")
        const studentId = $(row).data("studentid")
        const classType = $(row).data("classtype")
        const hours = $(row).data("slots") / 2
        moreInfoHandle(classId, subjectId, classStatus, tutorId, studentId, classType, hours, userType="student")
    })

    const modalTagId = "schedule-log-modal";
    const tableId = "schedule-table";
    $(`#${modalTagId} .modal-background`).click(function () {
        closeModal($(this).closest(".modal"));
        $(`#${tableId} td`).removeClass("time-added");
        $("#logged-availability-table tbody").empty();
        $("tr.active").removeClass("active");
        // modalOpen = false;
    })
    $("#close-modal-button").click(function () {
        closeModal($(`#${modalTagId}`).closest(".modal"));
        $(`#${tableId} td`).removeClass("time-added");
        $("#logged-availability-table tbody").empty();
        $("tr.active").removeClass("active");
    })
    $(document).on("keydown", function (event) {
        let key = (event.keyCode ? event.keyCode : event.which);
        if (key === 27) {
            closeModal($(`#${modalTagId}`).closest(".modal"));
            $(`#${tableId} td`).removeClass("time-added");
            $("#logged-availability-table tbody").empty();
            $("tr.active").removeClass("active");
        }
    })

    $("#confirm-hours-button").click(function() {
        console.log("entering")
        const row = $("tr.active")
        const classId = $(row).data("classid")
        // const subjectId = $(row).data("subjectid")
        // const classStatus = $(row).data("status")
        const tutorId = $(row).data("tutorid")
        // const studentId = $(row).data("studentid")
        const classType = $(row).data("classtype")
        const hours = $(row).data("slots") / 2


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
                const post_url = `/class_log_re_schedule/${classId}`
                var classesArray = classRowsCreation(getElementsArrayByClass("time-added"))
                const dataToSend = {schedule_data: transformClassRowsData(classesArray)};
                makeStringifyPostRequest(post_url, dataToSend, function(error, response) {
                    if (error) {
                        console.error("Error en el request: ", error)
                        return
                    }
                    var status = response.status;
                    if (status === "Re-schedule Successful") {
                        $("div.box").addClass("is-hidden")
                        $("div.modal-content").css("max-width", "500px")
                        $("#confirmation-message").removeClass("is-hidden")
                    } else {
                        message(response.error, true, "availability-box", messageId="schedule-modal-feedback");
                    }
                })
            } else {
                message(JSON.parse(response)["error"], true, "availability-box", messageId="schedule-modal-feedback");
            }
        })
    });
})