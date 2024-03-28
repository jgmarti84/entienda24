var login = function() {
  if ($(this).attr("id") === "navbar-login-button") {
    var data = {
      "username_email": $("#navbar-login-user").val(),
      "password": $("#navbar-login-pass").val(),
      "csrf_token": $("#csrf_token").val()
    }
  } else if ($(this).attr("id") === "page-login-button") {
    var data = {
      "username_email": $("#page-login-user").val(),
      "password": $("#page-login-pass").val(),
      "csrf_token": $("#csrf_token").val()
    }
  } else {
    var data = {
      "username_email": $("#create-account-login-user").val(),
      "password": $("#create-account-login-pass").val(),
      "csrf_token": $("#csrf_token").val()
    }
  }
  $.post({
    type: "POST",
    url: '/login',
    data: data,
    success(response){
      console.log(response)
      var status = JSON.parse(response)["status"];
      if (status === "Login Successful") {
        location.href = JSON.parse(response)["next_page"];
      } else {
        $(".username-errors ul").empty()
        var errors = JSON.parse(response)["errors"]
        $(errors).each(function(index, element) {
          $(".username-errors ul").append(`<li style="color: red; font-size: 10px;">${element}</li>`)
        })
        $(".username-errors").removeClass("is-hidden")
        error("login-input");
      }
    }
  });
};
