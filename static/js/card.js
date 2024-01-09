var departments = document.getElementsByClassName('department');
var cards = document.getElementsByClassName('card');
var bottomValues = ['0px', '50px', '100px'];

var oldBottom = 0;
var newBottom = 0;

for (var i = 0; i < cards.length; i++) {
  cards[i].addEventListener('click', function() {
    animation(this.id);
  })
}

function animation(id) {

  for (var i = 0; i < cards.length; i++) {
    var card = document.getElementById(cards[i].id);
    card.style.bottom = bottomValues[i];
    if (card.id != id) {
      card.name = '';
    }
  }

  var selected = document.getElementById(id);
  selected.style.transition = '0.3s';

  if (selected.name != 'moved') {

    oldBottom = parseInt(selected.style.bottom, 10);
    newBottom = '350px';
    selected.style.bottom = newBottom;
    selected.name = 'moved';

  } else if (selected.name == 'moved') {

    selected.style.bottom = oldBottom + 'px';
    selected.name = '';

  }
}

document.addEventListener('DOMContentLoaded', function() {
  document.documentElement.style.setProperty('--random-color-1', getRandomColor());
  document.documentElement.style.setProperty('--random-color-2', getRandomColor());
});

function getRandomColor() {
  var colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#e67e22', '#1abc9c', '#d35400'];
  return colors[random(0, colors.length - 1)];
}

function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}
