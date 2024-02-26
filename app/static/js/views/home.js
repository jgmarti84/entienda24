$(document).ready(function() {
    $(document).on("click", "#search-button", function () {
        var subject = $("#sbuject-search").val();
        var faculty = $("#faculty-search").val();

        // Construct the URL with query parameters
        var newURL = 'subjects?subject=' + subject + '&faculty=' + faculty;

        // Redirect to the new URL
        window.location.href = newURL;
    })
})