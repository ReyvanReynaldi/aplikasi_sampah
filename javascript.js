let nodeList = document.querySelector(".buttons");

$('.buttons').click(function(){

  $(this).addClass('button-active').siblings().removeClass('button-active');

  let filter = $(this).attr('data-filter');
  if(filter == 'all'){
      $('.menu .image').show(400);
  }else{
      $('.menu .image').not('.'+filter).hide(200);
      $('.menu .image').filter('.'+filter).show(400);
  }

});

// Global variables
let socket;
let isWebcamOpen = false;
let stream = null;

function initializeSocket() {
    const socketUrl = window.location.hostname === 'localhost' 
        ? 'http://localhost:5000'
        : `http://${window.location.hostname}:5000`;
    
    socket = io(socketUrl, {
        transports: ['websocket'],
        upgrade: false,
        reconnection: true,
        reconnectionAttempts: 5
    });
    
    socket.on('connect', () => {
        console.log('Connected to detection server');
    });

    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        alert('Gagal terhubung ke server deteksi. Silakan refresh halaman.');
    });

    socket.on('detection_result', (data) => {
        updateDetectionDisplay(data);
    });

    socket.on('detection_error', (data) => {
        console.error('Detection error:', data.error);
        closeWebcam();
    });
}


// function buat camera
async function getPicture() {
    const webcamElement = document.getElementById('webcam');
    const webcamControl = document.getElementById('webcam-control');
    
    if (!isWebcamOpen) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: 640,
                    height: 480
                } 
            });
            webcamElement.srcObject = stream;
            webcamControl.textContent = 'Tutup Kamera';
            isWebcamOpen = true;
            
            // mulai deteksi pas kamera kebuka
            if (!socket) {
                initializeSocket();
            }
            socket.emit('start_detection');
            
        } catch (err) {
            console.error('Error accessing webcam:', err);
            alert('Tidak dapat mengakses kamera');
        }
    } else {
        closeWebcam();
    }
}

// function buat nutup kamera
function closeWebcam() {
    const webcamElement = document.getElementById('webcam');
    const webcamControl = document.getElementById('webcam-control');
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        webcamElement.srcObject = null;
    }
    
    if (socket) {
        socket.emit('stop_detection');
    }
    
    webcamControl.textContent = 'Buka Kamera';
    isWebcamOpen = false;
}

function updateDetectionDisplay(data) {
    const webcamElement = document.getElementById('webcam');
    const prediksiElement = document.getElementById('elemPrediksi');
    const kontenElement = document.getElementById('konten');
    
    // update video frame
    if (data.frame) {
        webcamElement.style.display = 'block';
        webcamElement.src = `data:image/jpeg;base64,${data.frame}`;
    }
    
    // update deteksi
    if (data.detections && data.detections.length > 0) {
        let prediksiHTML = '<h3>Hasil Deteksi:</h3>';
        let kontenHTML = '';
        
        data.detections.forEach((detection, index) => {
            const confidence = (detection.confidence * 100).toFixed(2);
            prediksiHTML += `<p>Objek ${index + 1}: ${detection.label} (${confidence}%)</p>`;
            
            // Generate detailed content
            const info = detection.description;
            kontenHTML += `
                <div class="content-box ${detection.label.toLowerCase()}-box">
                    <h4>${info.title}</h4>
                    <p><strong>Deskripsi:</strong> ${info.description}</p>
                    <p><strong>Penanganan:</strong> ${info.handling}</p>
                    <p><strong>Contoh:</strong> ${info.examples || ''}</p>
                    ${info.decomposition_time ? `<p><strong>${info.decomposition_time}</strong></p>` : ''}
                    ${info.warning ? `<p class="warning">${info.warning}</p>` : ''}
                </div>
            `;
        });
        
        prediksiElement.innerHTML = prediksiHTML;
        kontenElement.innerHTML = kontenHTML;
    } else {
        prediksiElement.innerHTML = '<p>Tidak ada objek terdeteksi</p>';
        kontenElement.innerHTML = '';
    }
}