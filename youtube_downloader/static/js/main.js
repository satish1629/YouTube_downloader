let currentVideoId = null;
let progressInterval = null;

document.getElementById('urlForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('youtubeUrl').value;
    
    // Reset UI
    resetUI();
    
    try {
        const response = await fetch('/get-video-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `url=${encodeURIComponent(url)}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayVideoInfo(data);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to fetch video information');
    }
});

function displayVideoInfo(data) {
    document.getElementById('videoInfo').classList.remove('d-none');
    document.getElementById('thumbnail').src = data.thumbnail;
    document.getElementById('videoTitle').textContent = data.title;
    document.getElementById('videoAuthor').textContent = data.author;
    document.getElementById('videoDuration').textContent = formatDuration(data.duration);
    document.getElementById('videoViews').textContent = formatNumber(data.views);
    currentVideoId = data.video_id;
}

async function downloadVideo(quality) {
    const url = document.getElementById('youtubeUrl').value;
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    
    progressContainer.classList.remove('d-none');
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `url=${encodeURIComponent(url)}&quality=${quality}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            startProgressTracking(data.video_id);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to start download');
    }
}

function startProgressTracking(videoId) {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/progress/${videoId}`);
            const data = await response.json();
            
            const progressBar = document.getElementById('progressBar');
            const progress = Math.round(data.progress);
            
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(progressInterval);
                showSuccess('Download completed successfully!');
            }
        } catch (error) {
            clearInterval(progressInterval);
            showError('Failed to track download progress');
        }
    }, 1000);
}

function resetUI() {
    document.getElementById('videoInfo').classList.add('d-none');
    document.getElementById('progressContainer').classList.add('d-none');
    document.getElementById('errorAlert').classList.add('d-none');
    document.getElementById('successAlert').classList.add('d-none');
    if (progressInterval) {
        clearInterval(progressInterval);
    }
}

function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    errorAlert.textContent = message;
    errorAlert.classList.remove('d-none');
}

function showSuccess(message) {
    const successAlert = document.getElementById('successAlert');
    successAlert.textContent = message;
    successAlert.classList.remove('d-none');
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${padZero(minutes)}:${padZero(remainingSeconds)}`;
    }
    return `${minutes}:${padZero(remainingSeconds)}`;
}

function padZero(num) {
    return num.toString().padStart(2, '0');
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}
