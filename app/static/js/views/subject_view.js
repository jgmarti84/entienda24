$(document).ready(function () {
    // show profile rating as stars
    ratingToStars()

    // Sorting the tutor cards
    $("#order-tutors-select").change(function() {
        var newURL = $(location).attr('href').split("?")[0] + '?sortby=' + this.value
        window.location.href = newURL
    })
    $("#ascending-arrow").click(function() {
        var newURL = $(location).attr('href').split("?")[0] + '?sortby=' + $('#order-tutors-select').val() + '&asc=true'
        window.location.href = newURL
    })
    $("#descending-arrow").click(function() {
        var newURL = $(location).attr('href').split("?")[0] + '?sortby=' + $('#order-tutors-select').val() + '&asc=false'
        window.location.href = newURL
    })
    $(".media").each(function() {
        $(this).css("cursor", "pointer")
        $(this).click(function() {
            const tutorId = $(this).data("tutorid")
            const newURL = `/tutor-view/${tutorId}`
            // Redirect to the new URL
            location.href = newURL;
        })
    })
})