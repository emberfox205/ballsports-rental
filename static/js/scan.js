// Define the endpoint to send data towards
var endpoint;

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
    const integratedCamera = videoDevices.find(device => 
      keywords.some(keyword => device.label.toLowerCase().includes(keyword))
    );

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

      // Find endpoint to send data towards
      var subpage = window.location.pathname;
      if (subpage === "/rent") {
        endpoint = '/detect'
      } else if (subpage === '/returnning') {
        endpoint = '/detectReturn'
      }

      // POST Request 
      fetch(endpoint, {
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
        if ('redirect' in data) {
          detectionRedirect();
        }
        else if ('ball_name' in data) {
          updateBallDetection(data);
          updateStatusDetection(data);
        };
      })
      .catch((error) => {
        console.error('Error: ', error);
      })
    }

    // Update status of both ball and logo detection: 
    function updateStatusDetection(detectionResponse) {
      var ballStatus = detectionResponse.ball_name || "None";
      var logoStatus = detectionResponse.logo_flag;
      var accuracy = detectionResponse.confidence || 0

      if (ballStatus != "None" && accuracy > 0.85) {
        document.getElementById('ball-status').textContent = "✅ Item detected";
      }
      else {
        document.getElementById('ball-status').textContent = "⚪ Detecting item";
      }

      if (logoStatus != 0) {
        document.getElementById('logo-status').textContent = "✅ Logo detected";
      }
      else {
        document.getElementById('logo-status').textContent = "⚪ Detecting logo";
      }
    }

    // Update components on /rent with response data
    function updateBallDetection(detectionResponse) {
      var ballType = detectionResponse.ball_name || "Unknown";
      var accuracy = detectionResponse.confidence || "N/A";
      
      // Round accuracy 
      if (typeof accuracy === 'number') {
        accuracy = accuracy.toFixed(4);
      }

      // Modify HTML elements based on response
      document.getElementById('ball-type').textContent = ballType;
      document.getElementById('accuracy').textContent = accuracy;
    
      var accuracyElement = document.getElementById('accuracy');
      var accuracyValue = parseFloat(accuracy);
    
      if (accuracyValue > 0.85) {
        accuracyElement.style.backgroundColor = '#39FF14';
        accuracyElement.style.color = 'red';
      } else {
        accuracyElement.style.backgroundColor = 'red'; // Reset to default if needed
        accuracyElement.style.color = 'yellow';
      }
    }
    


    // Redirect on successful detection
    // Add data to local storage to be redisplayed to the Confirmation page 
    function detectionRedirect() {
      const ballType = document.getElementById('ball-type').textContent;
      const accuracy = document.getElementById('accuracy').textContent;
      
      localStorage.setItem('ballType', ballType);
      localStorage.setItem('accuracy', accuracy);
      // Redirect based on what the current functionality is
      if (endpoint === '/detect') {
        window.location.href = '/finalRent';
      }
      else {
        window.location.href = '/finalReturn'
      }
    }

    // Call snapshot function 
    takeSnapshot();

    // Take snapshots continuously
    // Time interval to be changed
    setInterval(takeSnapshot, 1000);
  })
  .catch((err) => {
    console.error(`${err.name}: ${err.message}`);
  });


