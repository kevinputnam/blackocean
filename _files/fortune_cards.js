// contact: kevin.putnam@gmail.com
// created: 11/27/2021

var decks = [];
var deck = []
var cards = [];
var num_cards = 0;
const card_file = "_files/cards.json";


function load_cards(){
  fetch(card_file).then(response => response.text()).then(respText => start_deck(respText));
}

function start_deck(text){
  decks = JSON.parse(text);
  cards = decks.main;
  cards = cards.concat(decks.seasons);
  num_cards = cards.length;
  shuffleDeck();
}

function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1) + min); //The maximum is inclusive and the minimum is inclusive
}

function shuffleDeck(){
    document.getElementById('cards').innerHTML = '';
    deck = [];
    var pull_deck = [];
    for (let i=0;i<num_cards;i++){
        pull_deck.push(i);
    }
    while(pull_deck.length > 0){
        var pull_index = getRandomIntInclusive(0,pull_deck.length -1);
        var new_card = pull_deck[pull_index];
        pull_deck.splice(pull_index,1);
        deck.push(new_card);
    }
}

function drawCard(){
    if (deck.length == 0) {
        alert("Time to shuffle the deck.");
        return;
    }
    var card_number = deck.pop();
    var the_card = cards[card_number];
    var orientation = getRandomIntInclusive(0,1);
    var card_name = the_card['name'];
    var card_meaning = the_card['meanings'][orientation];
    var card_meaning_reverse = the_card['meanings'][(orientation+1)%2];
    var card_suit = the_card['suit'];
    var card_number = the_card['number'];

    var img = new Image;
    var style = "max-width: 200px;";
    if (orientation == 1){
        card_name += " (reversed)";
        style += "transform: rotate(180deg);"
    }
    img.style = style;
    img.src = "_files/fortune_cards/" + the_card['image'];
    img.classList.add('card-image');

    var card_div = document.createElement('div');
    card_div.classList.add('card');
    card_div.appendChild(img);

    var card_name_div = document.createElement('div');
    card_name_div.innerHTML = card_name;
    card_name_div.classList.add("card-name");

    var card_number_div = document.createElement('div');
    card_number_div.innerHTML = card_number;
    card_number_div.classList.add('card-number');

    var card_meaning_div = document.createElement('div');
    card_meaning_div.innerHTML = card_meaning;
    card_meaning_div.classList.add("card-meaning");

    var card_meaning_rev_div = document.createElement('div');
    card_meaning_rev_div.innerHTML = card_meaning_reverse;
    card_meaning_rev_div.classList.add("card-meaning-reverse")

    var card_suit_div = document.createElement('div');
    card_suit_div.innerHTML = card_suit;
    card_suit_div.classList.add('card-suit');

    card_div.appendChild(card_number_div);
    card_div.appendChild(card_suit_div);
    card_div.appendChild(card_meaning_div);
    card_div.appendChild(card_meaning_rev_div);
    card_div.appendChild(card_name_div);
    var card_surface = document.getElementById('cards')
    card_surface.appendChild(card_div);
    card_surface.scrollTop = card_surface.scrollHeight;
}