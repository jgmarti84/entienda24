function getStars(rating) {
  // Round to nearest half
  rating = Math.round(rating * 2) / 2;
  let output = [];

  // Append all the filled whole stars
  for (var i = rating; i >= 1; i--)
    output.push('<i class="fas fa-star" aria-hidden="true" style="color: gold;"></i>&nbsp;');

  // If there is a half a star, append it
  if (i == .5) output.push('<i class="fas fa-star-half" aria-hidden="true" style="color: gold;"></i>&nbsp;');

  return output.join('');
}

function ratingToStars() {
    // Modify ratings float numbers into stars
    var stars = $('.stars')
    $(stars).each(function() {
        const n = this.innerHTML
        this.innerHTML = getStars(n)
    })
}

function renderLastUpdate() {
    var dateString = $(".last-update").data("last-update");
    console.log(dateString)
    const date = new Date(dateString);
    // Format the date components
    // Convert the date to a different timezone
    const options = { timeZone: 'America/Argentina/Buenos_Aires' };
    const formattedDate = date.toLocaleString('es-AR', options);
    console.log(formattedDate)
    // const formattedDate = `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()} a las ${date.getHours()}:${date.getMinutes()} hrs`;
    // Update the text content of the HTML element with the formatted date
    $(".last-update strong").text(formattedDate);
}