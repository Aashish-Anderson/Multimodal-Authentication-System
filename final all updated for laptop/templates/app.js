const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const statusBox = document.getElementById("status");

// === open camera ===
navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    video.srcObject = stream;
});

// === capture image ===
document.getElementById("capture").onclick = () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    statusBox.innerHTML = "Face Captured ✔";
};

// === POST captured photo in Base64 ===
async function send(endpoint) {

    const image = canvas.toDataURL("image/jpeg");

    let result = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ image })
    });

    let data = await result.json();
    statusBox.innerHTML = data.message;
}

document.getElementById("register").onclick = () => send("register_face");
document.getElementById("login").onclick = () => send("verify_face");

