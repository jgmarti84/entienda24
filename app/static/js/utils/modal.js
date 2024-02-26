// Functions to open and close a modal
function openModal(el) {
    $(el).addClass('is-active');
}

function closeModal(el) {
    $(el).removeClass('is-active');
}

function closeAllModals() {
    $(".modal").each((modal) => {
        closeModal(modal);
    })
}
function closeModalEvents(modalTagId) {
    $(`#${modalTagId} .modal-background`).click(function () {
        closeModal($(this).closest(".modal"))
    })
    $("#close-modal-button").click(function () {
        closeModal($(`#${modalTagId}`).closest(".modal"))
    })
    $(document).on("keydown", function (event) {
        let key = (event.keyCode ? event.keyCode : event.which);
        if (key === 27) {
            closeModal($(`#${modalTagId}`).closest(".modal"))
        }
    })
}

function openSubjectPricesModal(subjectId, modalTagId) {
    $(`#${modalTagId}`).addClass("is-active")
    var subjectIdentifier = `subject-${subjectId}`
    $(`.prices-tables-div`).each(function () {
        if ($(this).attr('id') === subjectIdentifier) {
            $(this).removeClass("is-hidden")
        } else {
            $(this).addClass("is-hidden")
        }
    })
}