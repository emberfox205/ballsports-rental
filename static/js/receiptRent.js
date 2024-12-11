function retrieveDetection() {
    const ballType = localStorage.getItem('ballType');
    const accuracy = localStorage.getItem('accuracy');
    const email = localStorage.getItem('user');
    const currentTimestamp = new Date().getTime(); 

    const formattedDate = new Date(currentTimestamp).toLocaleString();

    document.getElementById('object').textContent = ballType;
    document.getElementById('accuracy').textContent = accuracy;
    document.getElementById('user').textContent = email;
    document.getElementById('date').textContent = formattedDate;
}

// Send data upon clicking
function sendRentInfo() {
    const ballType = localStorage.getItem('ballType');
    const accuracy = localStorage.getItem('accuracy');
    const currentTimestamp = new Date().getTime();

    fetch('/confirmRent', {
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

// Call function on DOM load
document.addEventListener('DOMContentLoaded', function() {
    retrieveDetection();
})

