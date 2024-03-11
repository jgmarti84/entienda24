var rateColors = ['red', 'darkorange', 'orange', 'gold', 'rgb(248, 248, 41)']

function setPriority(event) {
  var star = event.srcElement;
  var priority = star.getAttribute("data-priority-value");
  var index = priority;

  var markedStar = star.getAttribute("data-status-marked");
  if (markedStar === "false")
    markStar(index);
  else {
    unMarkStar(index);
  }
  $("#ratingBox").data("index", parseInt(index)+1)
}

function markStar(index) {
  var stars = document.getElementsByClassName("rating");
  for (let i = 0; i <= index; i++) {
    stars[i].style.color = rateColors[index];
    stars[i].setAttribute("data-status-marked", "true");
  }
}

function unMarkStar(index) {
  var stars = document.getElementsByClassName("rating");
  for (let i = 1; i < stars.length; i++) {
    stars[i].style.color = '#5b555b';
    stars[i].setAttribute("data-status-marked", "false");
  }
  markStar(index);
}

function updateFlag(index) {
  var flag = document.getElementById("priorityFlag");
  // console.log("update flag acc to",index,rateColors[index]);//updating flag color to this index of flagColors array
  flag.style.color = rateColors[index];
  flag.style.borderColor = rateColors[index];
}