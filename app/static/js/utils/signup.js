var signup = function() {
  $.post({
    type: "POST",
    url: "/signup",
    data: {
      "username": $("#signup-user").val(),
      "password": $("#signup-pass").val(),
      "name": $("#signup-name").val(),
      "last_name": $("#signup-last-name").val(),
      "email": $("#signup-mail").val(),
      "user_type": $("input[name='user_type']:checked").val(),
      "phone_country_code": $("select[name='phone_country_code']").val(),
      "phone_city_code": $("input[name='phone_city_code']").val(),
      "phone": $("input[name='phone']").val(),
      "csrf_token": $("#csrf_token").val()
    },
    success(response) {
      var status = JSON.parse(response)["status"];
      if (status === "Signup Successful") {
        location.href = JSON.parse(response)["next_page"];
      } else {
        message(JSON.parse(response)["error"], true, "signup-box");
      }
    }
  });
};