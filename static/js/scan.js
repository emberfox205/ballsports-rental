// Consecutive images -> Confirmation 
var imageCounter = 0;

// Request access to media devices to prompt for permissions
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  .then((stream) => {
    // Enumerate devices after permission is granted
    return navigator.mediaDevices.enumerateDevices();
  })
  .then((devices) => {
    // Find the integrated camera
    const videoDevices = devices.filter(device => device.kind === 'videoinput');
    const integratedCamera = videoDevices.find(device => device.label.toLowerCase().includes('integrated'));

    if (integratedCamera) {
      // Use the device ID of the integrated camera to request the media stream
      // Note: Firefox only supports Native webcam size 
      const constraints = {
        audio: false,
        video: {
          deviceId: { exact: integratedCamera.deviceId },
          width: {min: 640, ideal: 960, max: 1280},
          height: { min: 480, ideal: 720, max: 1080}
        }
      };

      return navigator.mediaDevices.getUserMedia(constraints);
    } else {
      throw new Error('Integrated camera not found');
    }
  })
  .then((mediaStream) => {
    const video = document.querySelector("video");
    video.srcObject = mediaStream;
    video.onloadedmetadata = () => {
      video.play();
    };
    
    // Take snapshot function
    const takeSnapshot = () => {
      // Setup variables
      const video = document.querySelector('video');
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert the image to Base64
      const imageData = canvas.toDataURL('image/jpg');

      // POST Request 
      fetch('/rent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // Content of request
        body: JSON.stringify({ image: imageData })
      })
      .then(response => response.json())
      .then(data => {
        console.log(response);
      })
      .catch((error) => {
        console.error('Error: ', error);
      });
    }

    // Call snapshot function 
    takeSnapshot();

    // Take snapshots continuously
    // Time interval to be changed
    setInterval(takeSnapshot, 10000);
  })
  .catch((err) => {
    console.error(`${err.name}: ${err.message}`);
  });


