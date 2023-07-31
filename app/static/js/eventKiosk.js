$(document).keydown(function(e){
  if (e.key === "Escape") {
    $("#fullscreenCheck").prop("checked", false)
    toggleFullscreen();
  }
  else if(e.key === "Enter") {
      submitData(true)
      $('.qr-reader-button').function(true)
      ;
  }
});
// Source: https://stackoverflow.com/questions/1125084/how-to-make-the-window-full-screen-with-javascript-stretching-all-over-the-screen
function toggleFullscreen() {
  if($("#fullscreenCheck").prop("checked") == false){
    hideElements(false);
    document.exitFullscreen()
    || document.webkitExitFullscreen()
    || document.msExitFullscreen()
  }
  else{
    hideElements(true);
    var el = document.documentElement
    , rfs = // for newer Webkit and Firefox
    el.requestFullscreen
    || el.webkitRequestFullScreen
    || el.mozRequestFullScreen
    || el.msRequestFullscreen
    ;
    if(typeof rfs!="undefined" && rfs){
      rfs.call(el);
    } else if(typeof window.ActiveXObject!="undefined"){
      // for Internet Explorer
      var wscript = new ActiveXObject("WScript.Shell");
      if (wscript!=null) {
        wscript.SendKeys("{F11}");
      }
    }
  }
  $('#submitScannerData').focus();
};

function eventFlasher(flash_message, status){
    if (status === "success") {
        category = "success";
        $("#signinData").append("<div class=\"alert alert-"+ category +"\" role=\"alert\" id=\"flasher\">"+flash_message+"</div>");
        $("#flasher").delay(5000).fadeOut();
    }
    else {
        category = "danger";
        $("#signinData").append("<div class=\"alert alert-"+ category +"\" role=\"alert\" id=\"flasher\">"+flash_message+"</div>");
        $("#flasher").delay(5000).fadeOut();
    }

}

$('.qr-reader-button').on("click", function() {
  //  Opens the camera to scan the ID
  $('#qr-reader').toggle()
  var lastResult, countResults = 0;
  function onScanSuccess(decodedText, decodedResult) {
      if (decodedText !== lastResult) {
          ++countResults;
          lastResult = decodedText;
          // Handle on success condition with the decoded message.
          console.log(`Scan result ${decodedText}`, decodedResult);
          
          $("#submitScannerData").val(decodedText)
          submitData(true);
      }
  }
  let qrboxFunction = function(viewfinderWidth, viewfinderHeight) {
    let minEdgePercentage = 0.9; // 90%
    let minEdgeSize = Math.min(viewfinderWidth, viewfinderHeight);
    let qrboxSize = Math.floor(minEdgeSize * minEdgePercentage);
    return {
        width: qrboxSize,
        height: qrboxSize
    };
  }
  var html5QrcodeScanner = new Html5QrcodeScanner(
      "qr-reader", { fps: 15, qrbox : qrboxFunction, preferFrontCamera: false });
  html5QrcodeScanner.render(onScanSuccess);

  $('#html5-qrcode-button-camera-stop').on("click", function() {
    $('#qr-reader').hide()
    
  })
})

function submitData(hitEnter = false){
  if(hitEnter){
    $("#flasher").remove()
    $.ajax({
      method: "POST",
      url: '/signintoEvent',
      data: {
        "eventid": $("#eventid").val(),
        "bNumber": $("#submitScannerData").val()
      },
      success: function(decodedText) {
        flasherStatus = "success"
        if (decodedText.status == "already signed in") {
          message = decodedText.user + " Already Signed In!"
          flasherStatus = "warning"

        } else if (decodedText.status === "banned") {
          message = decodedText.user + " is ineligible."
          flasherStatus = "danger"
          
        } else if (decodedText.status === "does not exist") {
          message = "User does not exist"
          flasherStatus = "danger"
          
        } else {
          message = decodedText.user + " Successfully Signed In!"
        }
        eventFlasher(message, flasherStatus);
        $("#submitScannerData").val("").blur();
        $('#submitScannerData').focus();
      },
      error: function(request, status, error) {
        console.log(status, error);
        eventFlasher("See Attendant; Unable to Sign In.", "danger");
        $("#submitScannerData").val("").blur();
        $('#submitScannerData').focus();
      }
    })
  }
}

function hideElements(hide) {

  if (hide == true) {

    $("footer").hide();
    $("kiosk-hide").animate({ opacity: 0 }, 1);
    $("kiosk-hide").css("width", "0");
    $("kiosk-hide").prop("disabled", true);
    $("a").hide();
    $("nav").css("width", "0");
  } else {
    $("footer").show();
    $("kiosk-hide").css("width", "inherit");
    $("kiosk-hide").animate({ opacity: 1 }, 1);
    $("kiosk-hide").prop("disabled", false);
    $("a").show();
    $("nav").css("width", "inherit");
  }
}
