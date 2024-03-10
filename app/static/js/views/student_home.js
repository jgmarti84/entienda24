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
            // formData.append('student_id', JSON.stringify());
            $.post({
                type: "POST",
                url: '/upload_picture',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    console.log(response)
                    if (response.status === "Upload Successful") {
                        alert("response successful")
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

    $(".more-info-cell").click(function() {
        const row = $(this).parent('tr')
        const classId = $(row).data("classid")
        const subjectId = $(row).data("subjectid")
        const classStatus = $(row).data("status")
        const tutorId = $(row).data("tutorid")
        const studentId = $(row).data("studentid")
        const classType = $(row).data("classtype")
        const hours = $(row).data("slots") / 2
        moreInfoHandle(classId, subjectId, classStatus, tutorId, studentId, classType, hours, userType="student")
    })
})