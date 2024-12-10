// Request access to media devices to prompt for permissions
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  .then((stream) => {
    // Enumerate devices after permission is granted
    return navigator.mediaDevices.enumerateDevices();
  })
  .then((devices) => {
    // Find the integrated camera
    const keywords = ['integrated', 'built-in', 'internal', 'webcam'];
    const videoDevices = devices.filter(device => device.kind === 'videoinput');
<<<<<<< HEAD
    const integratedCamera = videoDevices.find(device => device.label.toLowerCase().includes('webcam'));
=======
    const integratedCamera = videoDevices.find(device => 
      keywords.some(keyword => device.label.toLowerCase().includes(keyword))
    );
>>>>>>> 01e5338c073ded73e2bc1364732fda592e4cbff8

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
    
    // Take snapshot and handle POST (Horrendous, I know)
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
      fetch('/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // Content of request
        body: JSON.stringify({ image: imageData })
      })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        if ('ball_type' in data && 'confidence' in data) {
          updateDetection(data);
        }
        else if ('redirect' in data) {
          detectionRedirect();
        };
      })
      .catch((error) => {
        console.error('Error: ', error);
      });
    }

    // Update components on /rent with response data
    function updateDetection(detectionResponse) {
      var ballType = detectionResponse.ball_name || "Unknown";
      var accuracy = detectionResponse.confidence || "N/A";

      if (typeof accuracy === 'number') {
        accuracy = accuracy.toFixed(4);
      }

      document.getElementById('ball-type').textContent = ballType;
      document.getElementById('accuracy').textContent = accuracy;
    }

    // Redirect on successful detection
    function detectionRedirect() {
      window.location.href = '/finalRent';
      }

    // Call snapshot function 
    takeSnapshot();

    // Take snapshots continuously
    // Time interval to be changed
    setInterval(takeSnapshot, 3000);
  })
  .catch((err) => {
    console.error(`${err.name}: ${err.message}`);
  });


