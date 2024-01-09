function makeHTMLElement(tag, classes, text, attributes) {	
    var attrs = '';
    for(var prop in attributes) {
        attrs += ` ${prop}="${attributes[prop]}"`;
    }
    return `<${tag} class="${classes}"${attrs}>${text}</${tag}>`;
}

$.get('/static/users.jsosn', function(data) {
    console.log(data)
    var friends = data.results;
    friends.map(friend => {
        var img = makeHTMLElement('div', 'friend-profile', '', {'style': `background-image: url(${friend.picture.thumbnail})`});
        var name = `${friend.name.first} ${friend.name.last}`;
        var nameBox = makeHTMLElement("div", 'name-box', name);
        var username = `@${friend.login.username}`;
        var unBox = makeHTMLElement('div', 'user-name-box', username + " requested a loan");
        var accept = makeHTMLElement('button', 'friend-request accept-request', 'Accept', {"data-username": friend.login.username});
        var decline = makeHTMLElement('button', 'friend-request decline-request', 'Decline', {"data-username": friend.login.username});
        var rBtnrow = makeHTMLElement('div', 'request-btn-row', accept + decline, {"data-username": friend.login.username});
        var friendBox = makeHTMLElement('div', 'friend-box', img + nameBox + unBox + rBtnrow);
        $('.friend-requests').append(friendBox);
    })
})

$('.friend-requests').on('click', '.friend-request', function() {
	var $elem = $(this);
	var username = $elem.attr('data-username')
	var type = $elem.hasClass('accept-request')
	console.log(username)
	var $rBtnrow = $(`.request-btn-row[data-username="${username}"]`)
	// $rBtnrow.addClass('disappear')
	if(type) {
        var message = makeHTMLElement('div', 'fr-request-pending', 'Load accepted.')
        var $friendBox = $elem.closest('.friend-box');
        $friendBox.remove();
	} else {
		var message = makeHTMLElement('div', 'fr-request-pending', 'Loan declined.')
        var $friendBox = $elem.closest('.friend-box');
        $friendBox.remove();
	}
	$rBtnrow.empty().append(message)
})

function generateRandomCard(loan_name, loan_amount) {
    var name = loan_name;
    var amount = loan_amount;
    
    var nameBox = makeHTMLElement("div", 'name-box', name);
    var amountBox = makeHTMLElement('div', 'amount-box', amount);
    var unBox = makeHTMLElement('div', 'user-name-box', "@" + name + " requested a loan");
    var accept = makeHTMLElement('button', 'friend-request accept-request', 'Accept', {"data-username": name});
    var decline = makeHTMLElement('button', 'friend-request decline-request', 'Decline', {"data-username": name});
    var rBtnrow = makeHTMLElement('div', 'request-btn-row', accept + decline, {"data-username": name});
    var friendBox = makeHTMLElement('div', 'friend-box', nameBox + unBox + rBtnrow);
    
    $('.friend-requests').append(friendBox);
}

$.ajax({
    type: "POST",
    url: "~/hello.py",
    data: { param: text}
  }).done(function( o ) {
     // do something
  });

document.getElementById('myButton').addEventListener('click', function() {
    // Assuming loans is available in JavaScript
    generateRandomCard("John", 1000);
});