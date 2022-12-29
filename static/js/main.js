var video = document.getElementById('video');
// getUserMedia()Get camera footage with
var media = navigator.mediaDevices.getUserMedia({ video: true });
//Pour into video tags for real-time playback (streaming)
media.then((stream) => {
    video.srcObject = stream;
});

var canvas = document.getElementById('canvas');
canvas.setAttribute('width', video.width);
canvas.setAttribute('height', video.height);

video.addEventListener(
    'timeupdate',
    function () {
        var context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, video.width, video.height);
    },
    true
);

//Set the listener that executes capture acquisition when the space key is pressed
var button = document.getElementById("myBtn");
button.addEventListener("click", function(event){
        var img_base64 = canvas.toDataURL('images/jpeg').replace(/^.*,/, '')
        captureImg(img_base64);
        //setTimeout(url, 1000);
        //function url(){
                //window.location.href = "http://127.0.0.1:8000/identify";}
});

var xhr = new XMLHttpRequest();

//Captured image data(base64)POST
function captureImg(img_base64) {
    const body = new FormData();
    body.append('img', img_base64);
    xhr.open('POST', 'http://127.0.0.1:8000/capture_img', true);
    xhr.onload = () => {
        console.log(xhr.responseText)
    };
    xhr.send(body);
}