// scanner/static/scanner/js/scanner.js
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const qrCodeSuccessCallback = (decodedText, decodedResult) => {
    document.getElementById("result").innerText = `Scanned: ${decodedText}`;
    fetch("/scan/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ code: decodedText })
    })
    .then(res => res.json())
    .then(data => {
        alert(`Scan successful. Direction: ${data.direction}`);
    });
};

const html5QrCode = new Html5Qrcode("reader");
html5QrCode.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 250 },
    qrCodeSuccessCallback
);