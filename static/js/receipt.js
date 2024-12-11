function retrieveDetection() {
    const ballType = localStorage.getItem('ballType');
    const accuracy = localStorage.getItem('accuracy');

    document.getElementById('object').textContent = ballType;
    document.getElementById('accuracy').textContent = accuracy;
}

document.addEventListener('DOMContentLoaded', function() {
    retrieveDetection();
})
