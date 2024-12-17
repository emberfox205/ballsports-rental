const formalBallNames = {
    'american_football': 'American football',
    'baseball': 'Baseball',
    'basketball': 'Basketball',
    'football': 'Football',
    'table_tennis_ball': 'Table tennis',
    'tennis_ball': 'Tennis',
    'volleyball': 'Volleyball'
  }

// Fix ball names and number formatting
function fixFormat(response) {
    // Fix ball names' captalization and other formatting
    if (formalBallNames.hasOwnProperty(response.ball_name)) {
        response.ball_name = formalBallNames[response.ball_name];
    }

    // Round accuracy 
    if (typeof response.confidence === 'number') {
        response.confidence = response.confidence.toFixed(4);
    }

    return response;
}

function retrieveDetection() {
    var formattedStorage = fixFormat(localStorage);
    const ballType = formattedStorage.getItem('ballType');
    const accuracy = formattedStorage.getItem('accuracy');
    const email = formattedStorage.getItem('user');
    const currentTimestamp = new Date().getTime(); 

    const formattedDate = new Date(currentTimestamp).toLocaleString();

    document.getElementById('object').textContent = ballType;
    document.getElementById('accuracy').textContent = accuracy;
    document.getElementById('user').textContent = email;
    document.getElementById('date').textContent = formattedDate;
}

// Send data upon clicking
function sendInfo() {
    const ballType = localStorage.getItem('ballType');
    const accuracy = localStorage.getItem('accuracy');
    const currentTimestamp = new Date().getTime();

    // Find endpoint to send data towards
    var subpage = window.location.pathname;
    if (subpage === '/finalRent') {
      endpoint = '/confirmRent'
    } else if (subpage === '/finalReturn') {
      endpoint = '/confirmReturn'
    }

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }, 
        body: JSON.stringify({ ball_name: ballType, confidence: accuracy, date: currentTimestamp})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch((error) => {
      console.error('Error: ', error);
    })
}

function logOut() {
    sendInfo();
    window.location.href='logout';
}

// Call function on DOM load
document.addEventListener('DOMContentLoaded', function() {
    retrieveDetection();
})

