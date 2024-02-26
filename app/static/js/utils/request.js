// Function to make an AJAX request and handle the result with a callback
function makeGetRequest(url, callback) {
    $.get({
        url: url,
        method: "GET",
        success: function(response) {
            callback(null, response); // Pass the response to the callback
        },
        error: function(error) {
            callback(error, null); // Pass the error to the callback
        }
    });
}

function makeStringifyPostRequest(url, dataToSend, callback) {
    $.post({
        url: url,
        method: "POST",
        contentType: 'application/json',
        data: JSON.stringify(dataToSend),
        success: function(response) {
            callback(null, response); // Pass the response to the callback
        },
        error: function(error) {
            callback(error, null); // Pass the error to the callback
        }
    })
}