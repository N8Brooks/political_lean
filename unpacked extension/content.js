
chrome.runtime.sendMessage({lean: "load"});

// capture all text
var textToSend = document.body.innerText.substring(300,2048);

//alert(textToSend);

// summarize and send back
const api_url = 'https://us-central1-braided-upgrade-262021.cloudfunctions.net/function-1';

//alert(textToSend);


fetch(api_url, {
	method: 'POST',
	body: JSON.stringify(textToSend),
	headers:{
		'Content-Type': 'application/json'
	} })
	.then(data => { return data.text() })
	.then(res => {chrome.runtime.sendMessage({lean: res})})
.catch(error => console.error('Error:', error));





