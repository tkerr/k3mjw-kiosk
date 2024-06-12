
var sondehub_url = "https://tracker.sondehub.org"

// Function to load the sondehub iframe.
function loadIFrameSource(id, source) {
  document.getElementById(id).src=source;
}
    
function update_frame() {
    intervalHandle = setInterval(function() {get_data();}, 10000);
}

// Function to kick off an async ajax request to get data.
function get_data() {
    // Launch an ajax HTTP request to get server data.
    jQuery.ajax({
        url: 'sondehub_url.txt',
        cache: false,
        success: function(data) {
            console.log(data)
            if (data.length > 0) {
                if (sondehub_url !== data) {
                    sondehub_url = data
                    loadIFrameSource("sondehub", sondehub_url);
                }
            }
        }
    });
}
 
// Initiate an interval timer to gather data.
$(document).ready(function(){
    get_data();  // Initial page load
    // Wait for orignial sondehub page to load before updating it.
    timeoutHandle = setTimeout(update_frame, 30000);
});
