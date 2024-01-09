function makeHTMLElement(tag, classes, text, attributes) {	
    var attrs = '';
    for(var prop in attributes) {
        attrs += ` ${prop}="${attributes[prop]}"`;
    }
    return `<${tag} class="${classes}"${attrs}>${text}</${tag}>`;
}

$('.friend-requests').on('click', '.friend-request', function() {
    var $elem = $(this);
    var username = $elem.attr('data-username');
    var type = $elem.hasClass('accept-request');
    var loan_id = $elem.attr('data-loan-id');
    console.log(username);

    // Assuming you have a server endpoint to handle loan approval/decline

    fetch("/loan_approval", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: username, 
            approval: type ? "accepted" : "declined", 
            loan_id: loan_id
        }),
      })
        .then(function (response) {
          if (response.ok) {
            // If the account was created successfully, hide the modal
            var $rBtnrow = $(`.request-btn-row[data-loan-id="${loan_id}"]`);

            var message;
            if (type) {
                message = makeHTMLElement('div', 'fr-request-pending', 'Loan accepted.');
            } else {
                message = makeHTMLElement('div', 'fr-request-pending', 'Loan declined.');
            }

            $rBtnrow.empty().append(message);
          } else {
            console.error("Failed to create account:", response.statusText);
          }
        })
        .catch(function (error) {
          console.error("Failed to submit form:", error);
        });
});


function generateRandomCard(loan_name, loan_amount, loanID) {
    var name = loan_name;
    var amount = loan_amount;
    
    var nameBox = makeHTMLElement("div", 'name-box', name);
    var amountBox = makeHTMLElement('div', 'amount-box', amount);
    var unBox = makeHTMLElement('div', 'user-name-box', "@" + name + " requested a loan");
    var accept = makeHTMLElement('button', 'friend-request accept-request', 'Accept', {"data-username": name, "data-loan-id": loanID});
    var decline = makeHTMLElement('button', 'friend-request decline-request', 'Decline', {"data-username": name, "data-loan-id": loanID});
    var rBtnrow = makeHTMLElement('div', 'request-btn-row', accept + decline, {"data-loan-id": loanID});
    var friendBox = makeHTMLElement('div', 'friend-box', nameBox + unBox + rBtnrow);
    
    $('.friend-requests').append(friendBox);
}