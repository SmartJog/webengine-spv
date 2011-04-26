/* Close the overlay and widget-add */
function closeOverlay(){
    $('div.popup-background').hide();
    $('div.popup-div').hide();
    return false;
}

/* Show status details */
function showDetails(status_id) {
    $.post('/spv/status/details/' + status_id + '/' , {}, function(data){
            showDetailsContent(data);
            });
};

/* Helper to get the page "viewed" height */
function pageHeight(){
    return Math.max($(window).height(), $(document.body).height());
}

function alertmsg(evt){
    if (evt.keyCode == 27) {
        closeOverlay();
    }
}

/* Ajax callback which displays overlay and update its content */
function showDetailsContent(content) {
    var box = $('div.popup-div');
    box.css({
        left:( $(window).width() - box.width() )/2,
        top:( $(window).height() - box.height() )/2
        });
    $('div.popup-div').innerHTML = "";
    $('div.popup-div').html("");
    $('div.popup-background').height(pageHeight()).show();
    $('div.popup-div').html(content).show();
    $('div.popup-background').bind('click',closeOverlay);
    document.onkeypress=alertmsg;
};

/* Function called to reschedule a check and update display */
function reschedule_check(status_id) {
    var client = new XMLHttpRequest();
    client.open("GET", '/spv/status/reschedule/' + status_id + '/', false);
    client.send();
    showDetails(status_id);
};

/* Function called to acknowledge a check status and update display */
function acknowledge_status(status_id) {
    var client = new XMLHttpRequest();
    client.open("GET", '/spv/status/acknowledge/' + status_id + '/', false);
    client.send();
    document.getElementById('status' + status_id).className = "acknowledged";
    showDetails(status_id);
};

function submitSearch()
    {
        $('form').submit();
    }

/* Initialise document elements */
$(document).ready(function(){
        $('.check a').bind('click',function(){
            showDetails(this.id);
            return false;
            });
        });
