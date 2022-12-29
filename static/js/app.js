const video = document.getElementById('video');
const button = document.getElementById('button');
const select = document.getElementById('select');
var vidio = document.getElementById('video');
var btn = document.getElementById('myBtn');
let currentStream;

function stopMediaTracks(stream) {
  stream.getTracks().forEach(track => {
    track.stop();
  });
}

function gotDevices(mediaDevices) {
  select.innerHTML = '';
  select.appendChild(document.createElement('option'));
  let count = 1;
  mediaDevices.forEach(mediaDevice => {
    if (mediaDevice.kind === 'videoinput') {
      const option = document.createElement('option');
      option.value = mediaDevice.deviceId;
      const label = mediaDevice.label || `Camera ${count++}`;
      const textNode = document.createTextNode(label);
      option.appendChild(textNode);
      select.appendChild(option);
    }
  });
}

button.addEventListener('click', event => {
  if (typeof currentStream !== 'undefined') {
    stopMediaTracks(currentStream);
  }
  const videoConstraints = {};
  if (select.value === '') {
    videoConstraints.facingMode = 'environment';
  } else {
    videoConstraints.deviceId = { exact: select.value };
  }
  const constraints = {
    video: videoConstraints,
    audio: false
  };
  navigator.mediaDevices
    .getUserMedia(constraints)
    .then(stream => {
      currentStream = stream;
      video.srcObject = stream;
      return navigator.mediaDevices.enumerateDevices();
    })
    .then(gotDevices)
    .catch(error => {
      console.error(error);
    });
});

navigator.mediaDevices.enumerateDevices().then(gotDevices);

var canvas = document.getElementById('canvas');
canvas.setAttribute('width', video.width);
canvas.setAttribute('height', video.height);

vidio.addEventListener(
    'timeupdate',
    function () {
        var context = canvas.getContext('2d');
        context.drawImage(vidio, 0, 0, video.weight, video.height);
    },
    true
);

//Set the listener that executes capture acquisition when the space key is pressed
var btn = document.getElementById("myBtn");
btn.addEventListener("click", function(event){
        var img_base64 = canvas.toDataURL('images/jpeg').replace(/^.*,/, '')
        captureImg(img_base64);

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