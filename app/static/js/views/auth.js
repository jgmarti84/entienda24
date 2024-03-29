$(document).ready(function() {
    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function () {
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
    });
    $(document).on("click", ".login-button", login);
    $(document).keypress(function (e) {
        if (e.which === 13) {
            login;
        }
    });
    $(document).on("click", "#signup-button", signup);
})