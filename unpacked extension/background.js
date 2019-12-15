chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse) 
{
  if (msg.lean == "load") {
	chrome.tabs.query({active:true, windowType:"normal", currentWindow: true},function(d){
        var tabId = d[0].id;
        chrome.browserAction.setIcon({path: 'load.png', tabId: tabId});
    })
  }
  if(msg.lean == "R") {
     chrome.tabs.query({active:true, windowType:"normal", currentWindow: true},function(d){
        var tabId = d[0].id;
        chrome.browserAction.setIcon({path: 'R.png', tabId: tabId});
    })
  }
  else if(msg.lean == "RC") {
     chrome.tabs.query({active:true, windowType:"normal", currentWindow: true},function(d){
        var tabId = d[0].id;
        chrome.browserAction.setIcon({path: 'RC.png', tabId: tabId});
    })
  }
  else if(msg.lean == "C") {
     chrome.tabs.query({active:true, windowType:"normal", currentWindow: true},function(d){
        var tabId = d[0].id;
        chrome.browserAction.setIcon({path: 'C.png', tabId: tabId});
    })
  }
  else if(msg.lean == "LC") {
     chrome.tabs.query({active:true, windowType:"normal", currentWindow: true},function(d){
        var tabId = d[0].id;
        chrome.browserAction.setIcon({path: 'LC.png', tabId: tabId});
    })
  }
  else if(msg.lean == "L") {
     chrome.tabs.query({active:true, windowType:"normal", currentWindow: true},function(d){
        var tabId = d[0].id;
        chrome.browserAction.setIcon({path: 'L.png', tabId: tabId});
    })
  }
});