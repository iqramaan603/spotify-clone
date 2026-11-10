class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.isPlaying = false;
        this.currentSong = null;
        this.volume = parseFloat(localStorage.getItem('playerVolume')) || 1.0;
        this.queue = [];
        this.currentIndex = -1;
        this.currentButton = null;
        this.currentSongData = null;
        this.isNewSong = false;
        this.isInitialized = false;
        this.isFullyInitialized = false;
        this.initializationPromise = null;

        // Bind methods to preserve 'this' context
        this.play = this.play.bind(this);
        this.pause = this.pause.bind(this);
        this.resume = this.resume.bind(this);
        this.togglePlay = this.togglePlay.bind(this);
        this.previous = this.previous.bind(this);
        this.next = this.next.bind(this);
        this.seek = this.seek.bind(this);
        this.setVolume = this.setVolume.bind(this);
        this.loadRandomSong = this.loadRandomSong.bind(this);
        this.updateProgress = this.updateProgress.bind(this);
        this.updateDuration = this.updateDuration.bind(this);
        this.initializePlayerControls = this.initializePlayerControls.bind(this);
        this.handleTimeUpdate = this.handleTimeUpdate.bind(this);
        this.handleMetadataLoaded = this.handleMetadataLoaded.bind(this);

        // Set up audio element and initialize
        this.setupAudioElement();
        this.initializationPromise = this.initialize();

        // Try to restore previous state
        this.loadLastPlayedSong();

        // Initialize UI elements
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeUIElements());
        } else {
            this.initializeUIElements();
        }

        console.log('MusicPlayer v2 initialized');
        console.log('Current song:', this.currentSong);
        console.log('Current song data:', this.currentSongData);
        console.log('Current button:', this.currentButton);
        console.log('Current index:', this.currentIndex);
        console.log('Queue:', this.queue);
        console.log('Is playing:', this.isPlaying);
        console.log('Is initialized:', this.isInitialized);
    }

    async initialize() {
        console.log('Starting player initialization...');
        try {
            await new Promise(resolve => {
                if (this.audio.readyState >= 2) {
                    resolve();
                } else {
                    const handleCanPlay = () => {
                        this.audio.removeEventListener('canplay', handleCanPlay);
                        resolve();
                    };
                    this.audio.addEventListener('canplay', handleCanPlay);
                }
            });
            
            this.isFullyInitialized = true;
            console.log('Player fully initialized');
        } catch (error) {
            console.error('Error during initialization:', error);
        }
    }

    setupAudioElement() {
        // Set up basic audio properties
        this.audio.preload = 'auto';
        this.audio.volume = this.volume;

        // Add core event listeners
        this.audio.addEventListener('ended', () => {
            console.log('Song ended');
            this.isPlaying = false;
            this.updatePlayButtons();
            this.next();
        });

        this.audio.addEventListener('timeupdate', this.handleTimeUpdate);
        this.audio.addEventListener('loadedmetadata', this.handleMetadataLoaded);
        this.audio.addEventListener('error', (e) => {
            console.error('Audio error:', e);
            if (this.audio.error) {
                console.error('Error code:', this.audio.error.code);
                console.error('Error message:', this.audio.error.message);
            }
        });
    }

    handleTimeUpdate() {
        // Skip updates if not fully initialized
        if (!this.isFullyInitialized) {
            console.log('Skipping time update - player not fully initialized');
            return;
        }
        
        // Only update localStorage if not in the middle of a seek operation
        const storedTime = parseFloat(localStorage.getItem('playerCurrentTime'));
        if (isNaN(storedTime) || Math.abs(storedTime - this.audio.currentTime) > 1) {
            if (this.isPlaying) {
                localStorage.setItem('playerCurrentTime', this.audio.currentTime.toString());
            }
        }
        this.updateProgress();
    }

    handleMetadataLoaded() {
        console.log('=== Metadata Loaded ===');
        console.log('Audio Duration:', this.audio.duration);
        console.log('Current Song:', this.currentSong);
        console.log('Is New Song:', this.isNewSong);
        
        this.updateDuration();
        if (this.isNewSong) {
            this.isNewSong = false;
            this.forceUpdateProgress(0);
            return;
        }
        const savedTime = parseFloat(localStorage.getItem('playerCurrentTime'));
        console.log('Saved Time:', savedTime);
        
        if (!isNaN(savedTime) && savedTime > 0 && savedTime < this.audio.duration) {
            console.log('Restoring saved time:', savedTime);
            this.audio.currentTime = savedTime;
            this.forceUpdateProgress(savedTime);
        }
    }

    async play(songId, songUrl, button) {
        console.group('PLAY OPERATION');
        console.log('Initial state:', {
            currentSong: this.currentSong,
            isPlaying: this.isPlaying,
            currentTime: this.audio.currentTime,
            songId,
            songUrl
        });

        try {
            const songData = {
                id: songId,
                url: songUrl,
                title: button.dataset.songTitle,
                artist: button.dataset.songArtist,
                image: button.dataset.songImage
            };
            console.log('Song data:', songData);

            if (this.currentSong === songId) {
                console.log('Same song - toggling playback');
                this.togglePlay();
                console.groupEnd();
                return;
            }

            console.log('New song detected - loading...');
            
            // Save current state before changes
            const previousTime = this.audio.currentTime;
            console.log('Previous time:', previousTime);

            // Update state
            this.currentSongData = songData;
            this.currentButton = button;
            this.currentSong = songId;

            console.log('Loading audio source:', songUrl);
            this.audio.src = songUrl;
            
            // Wait for metadata
            console.log('Waiting for metadata...');
            await new Promise((resolve) => {
                const loadHandler = () => {
                    console.log('Metadata loaded');
                    this.audio.removeEventListener('loadedmetadata', loadHandler);
                    resolve();
                };
                this.audio.addEventListener('loadedmetadata', loadHandler);
            });

            // Update UI
            console.log('Updating player UI');
            this.updatePlayerInfo(songData);
            this.updateDuration();
            this.forceUpdateProgress(0);

            // Start playback
            console.log('Starting playback');
            await this.audio.play();
            this.isPlaying = true;
            this.updatePlayButtons();

            // Save to localStorage
            console.log('Saving to localStorage');
            localStorage.setItem('lastPlayedSong', JSON.stringify(songData));
            localStorage.setItem('playerCurrentTime', '0');

            console.log('Final play state:', {
                currentTime: this.audio.currentTime,
                isPlaying: this.isPlaying,
                currentSong: this.currentSong
            });
        } catch (error) {
            console.error('Error in play method:', error);
        }
        console.groupEnd();
    }

    pause() {
        console.group('PAUSE');
        console.log('Current time before pause:', this.audio.currentTime);
        
        this.audio.pause();
        this.isPlaying = false;
        this.updatePlayButtons();
        
        console.log('State after pause:', {
            currentTime: this.audio.currentTime,
            isPlaying: this.isPlaying
        });
        console.groupEnd();
    }

    async resume() {
        console.group('RESUME');
        console.log('Current time before resume:', this.audio.currentTime);
        
        try {
            await this.audio.play();
            this.isPlaying = true;
            this.updatePlayButtons();
            
            console.log('State after resume:', {
                currentTime: this.audio.currentTime,
                isPlaying: this.isPlaying
            });
        } catch (error) {
            console.error('Resume failed:', error);
        }
        console.groupEnd();
    }

    togglePlay() {
        console.group('TOGGLE PLAY');
        console.log('Initial state:', {
            isPlaying: this.isPlaying,
            currentTime: this.audio.currentTime,
            currentSong: this.currentSong
        });

        if (this.isPlaying) {
            console.log('Pausing playback');
            this.pause();
        } else {
            console.log('Resuming playback');
            this.resume();
        }

        console.log('Final state:', {
            isPlaying: this.isPlaying,
            currentTime: this.audio.currentTime
        });
        console.groupEnd();
    }

    async previous() {
        if (this.audio.currentTime > 3) {
            // If current time is more than 3 seconds, restart the song
            this.audio.currentTime = 0;
            localStorage.setItem('playerCurrentTime', '0');
        } else {
            // Load a random song as previous
            await this.loadRandomSong();
            if (this.isPlaying) {
                this.audio.play();
            }
        }
    }

    async next() {
        // Load a random song as next
        await this.loadRandomSong();
        if (this.isPlaying) {
            this.audio.play();
        }
    }

    setVolume(value) {
        console.log('Setting volume to:', value);
        this.volume = value;
        this.audio.volume = value;
        localStorage.setItem('playerVolume', value.toString());
    }

    updateProgress() {
        if (!this.audio.duration) return;
        
        const currentTime = this.audio.currentTime;
        const duration = this.audio.duration;
        const progress = (currentTime / duration) * 100;
        
        const progressBar = document.getElementById('song-progress');
        const currentTimeDisplay = document.getElementById('current-time');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        if (currentTimeDisplay) {
            currentTimeDisplay.textContent = this.formatTime(currentTime);
        }

        // Save current time to localStorage if playing
        if (this.isPlaying) {
            localStorage.setItem('playerCurrentTime', currentTime.toString());
        }
    }

    updateDuration() {
        const duration = document.getElementById('duration');
        if (duration && this.audio.duration) {
            duration.textContent = this.formatTime(this.audio.duration);
        }
    }

    async seek(event) {
        console.group('SEEK OPERATION');
        console.log('Current State:', {
            isPlaying: this.isPlaying,
            currentTime: this.audio.currentTime,
            duration: this.audio.duration,
            currentSong: this.currentSong,
            readyState: this.audio.readyState
        });
        
        try {
            const progressContainer = document.getElementById('progress-container');
            if (!progressContainer || !this.audio.duration) {
                console.warn('Cannot seek: missing elements or duration');
                console.groupEnd();
                return;
            }

            const rect = progressContainer.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const containerWidth = rect.width;
            
            const seekPercentage = Math.max(0, Math.min(1, clickX / containerWidth));
            const seekTime = this.audio.duration * seekPercentage;
            
            console.log('Seek Calculation:', {
                clickX,
                containerWidth,
                seekPercentage,
                seekTime,
                duration: this.audio.duration
            });

            const wasPlaying = this.isPlaying;
            console.log('Was playing before seek:', wasPlaying);
            
            if (wasPlaying) {
                console.log('Pausing for seek operation');
                this.audio.pause();
            }

            try {
                console.log('Setting new time:', seekTime);
                this.audio.currentTime = seekTime;
                
                console.log('Waiting for seek to complete...');
                await new Promise((resolve, reject) => {
                    const seeked = () => {
                        console.log('Seek completed successfully');
                        this.audio.removeEventListener('seeked', seeked);
                        this.audio.removeEventListener('error', error);
                        resolve();
                    };
                    
                    const error = (e) => {
                        console.error('Seek failed:', e);
                        this.audio.removeEventListener('seeked', seeked);
                        this.audio.removeEventListener('error', error);
                        reject(e);
                    };
                    
                    this.audio.addEventListener('seeked', seeked);
                    this.audio.addEventListener('error', error);
                });

                console.log('Updating UI and storage');
                this.forceUpdateProgress(seekTime);
                localStorage.setItem('playerCurrentTime', seekTime.toString());

                if (wasPlaying) {
                    console.log('Resuming playback');
                    await this.audio.play();
                    this.isPlaying = true;
                }

                console.log('Final state after seek:', {
                    currentTime: this.audio.currentTime,
                    isPlaying: this.isPlaying,
                    storedTime: localStorage.getItem('playerCurrentTime')
                });
            } catch (error) {
                console.error('Seek operation failed:', error);
                if (wasPlaying) {
                    console.log('Attempting to restore playback');
                    await this.audio.play();
                    this.isPlaying = true;
                }
            }
        } catch (error) {
            console.error('Error in seek method:', error);
        }
        console.groupEnd();
    }

    forceUpdateProgress(currentTime) {
        console.group('FORCE UPDATE PROGRESS');
        console.log('Updating progress with time:', currentTime);
        
        const progressBar = document.getElementById('song-progress');
        const currentTimeDisplay = document.getElementById('current-time');
        
        if (!progressBar || !currentTimeDisplay || !this.audio.duration) {
            console.warn('Missing elements or duration');
            console.groupEnd();
            return;
        }
        
        currentTime = Math.max(0, Math.min(currentTime, this.audio.duration));
        const progress = (currentTime / this.audio.duration) * 100;
        
        progressBar.style.width = `${progress}%`;
        currentTimeDisplay.textContent = this.formatTime(currentTime);
        
        console.log('Progress updated:', {
            currentTime,
            progress,
            duration: this.audio.duration
        });
        console.groupEnd();
    }

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    updatePlayButton(button, isPlaying) {
        console.log('Updating play button state:', isPlaying);
        const icon = button.querySelector('i');
        if (isPlaying) {
            icon.classList.remove('fa-play');
            icon.classList.add('fa-pause');
        } else {
            icon.classList.remove('fa-pause');
            icon.classList.add('fa-play');
        }
    }

    updateMainPlayerButton(isPlaying) {
        const mainPlayButton = document.getElementById('play-pause');
        if (mainPlayButton) {
            const icon = mainPlayButton.querySelector('i');
            if (isPlaying) {
                icon.classList.remove('fa-play');
                icon.classList.add('fa-pause');
            } else {
                icon.classList.remove('fa-pause');
                icon.classList.add('fa-play');
            }
        }
    }

    updatePlayerInfo(songData) {
        // Update song title
        const titleElement = document.getElementById('current-song-title');
        if (titleElement) {
            titleElement.textContent = songData.title;
        }

        // Update artist name
        const artistElement = document.getElementById('current-song-artist');
        if (artistElement) {
            artistElement.textContent = songData.artist;
        }

        // Update cover image
        const imageElement = document.getElementById('current-song-image');
        if (imageElement) {
            imageElement.src = songData.image;
        }
    }

   updatePlayButtons() {
    console.log('Updating all play buttons');

    // Existing logic: update small play buttons in song list
    document.querySelectorAll('.play-button').forEach(button => {
        const songId = button.dataset.songId;
        const icon = button.querySelector('i');
        if (icon) {
            if (this.isPlaying && this.currentSong === songId) {
                icon.classList.remove('fa-play');
                icon.classList.add('fa-pause');
            } else {
                icon.classList.remove('fa-pause');
                icon.classList.add('fa-play');
            }
        }
    });

    // 🔥✨ NEWLY ADDED BLOCK: Update the main play/pause icon
    const mainPlayPauseIcon = document.querySelector('#play-pause i');
    if (mainPlayPauseIcon) {
        if (this.isPlaying) {
            mainPlayPauseIcon.classList.remove('fa-play');
            mainPlayPauseIcon.classList.add('fa-pause');
        } else {
            mainPlayPauseIcon.classList.remove('fa-pause');
            mainPlayPauseIcon.classList.add('fa-play');
        }
    }
}

    getCsrfToken() {
        // Try to get from meta tag first
        const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (metaToken) {
            return metaToken;
        }

        // Try to get from cookie
        const name = 'csrftoken';
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

        // Try to get from hidden input
        if (!cookieValue) {
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                cookieValue = csrfInput.value;
            }

        }

        return cookieValue;
    }

    recordPlay(songId) {
        console.log('Recording play for song:', songId);
        const csrfToken = this.getCsrfToken();
        
        if (!csrfToken) {
            console.warn('CSRF token not found, skipping play count recording');
            return;
        }

        fetch(`/music/songs/${songId}/play/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            console.log('Play recorded successfully');
        }).catch(error => {
            console.error('Error recording play:', error);
        });
    }

    async initializePlayerControls() {
        try {
            console.log('Initializing player controls');
            
            // Wait for full initialization if needed
            if (!this.isFullyInitialized) {
                console.log('Waiting for full initialization before setting up controls...');
                await this.initializationPromise;
            }
            
            console.log('Audio ready state:', this.audio.readyState);
            
            const progressContainer = document.getElementById('progress-container');
            if (!progressContainer) {
                console.error('Progress container not found');
                return;
            }

            // Remove old event listeners by cloning
            const newProgressContainer = progressContainer.cloneNode(true);
            progressContainer.parentNode.replaceChild(newProgressContainer, progressContainer);

            // Add click seeking
            newProgressContainer.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.seek(e);
            });

            // Handle drag seeking
            let isDragging = false;
            
            const startDragging = (e) => {
                e.preventDefault();
                isDragging = true;
            };
            
            const stopDragging = () => {
                isDragging = false;
            };
            
            const drag = async (e) => {
                if (isDragging) {
                    e.preventDefault();
                    await this.seek(e);
                }
            };

            newProgressContainer.addEventListener('mousedown', startDragging);
            document.addEventListener('mousemove', drag);
            document.addEventListener('mouseup', stopDragging);

            // Update the progress bar immediately if possible
            if (this.audio.duration) {
                this.updateProgress();
            }
            
            console.log('Player controls initialized');
        } catch (error) {
            console.error('Error in initializePlayerControls:', error);
        }
    }

    initializeUIElements() {
        // Initialize volume
        const volumeControl = document.getElementById('volume-control');
        if (volumeControl) {
            volumeControl.value = this.volume;
            volumeControl.addEventListener('input', (e) => this.setVolume(parseFloat(e.target.value)));
        }

        // Initialize player controls
        this.initializePlayerControls();

        // Initialize play/pause button
        const playPauseButton = document.getElementById('play-pause');
        if (playPauseButton) {
            playPauseButton.addEventListener('click', this.togglePlay);
        }

        // Initialize next/previous buttons
        const prevButton = document.getElementById('prev-button');
        if (prevButton) {
            prevButton.addEventListener('click', this.previous);
        }

        const nextButton = document.getElementById('next-button');
        if (nextButton) {
            nextButton.addEventListener('click', this.next);
        }

        // Set initial volume
        this.audio.volume = this.volume;

        // Initialize all play buttons in the page
        this.updatePlayButtons();
    }

    async loadLastPlayedSong() {
        const lastSongData = localStorage.getItem('lastPlayedSong');
        const lastTime = parseFloat(localStorage.getItem('playerCurrentTime'));
        
        if (lastSongData) {
            // We have a last played song, try to load it
            const songData = JSON.parse(lastSongData);
            this.currentSongData = songData;
            this.currentSong = songData.id;
            this.audio.src = songData.url;
            this.updatePlayerInfo(songData);
            
            // Restore the last playback position
            if (!isNaN(lastTime) && lastTime > 0) {
                this.audio.currentTime = lastTime;
            }
        } else {
            // No last played song, load a random one
            await this.loadRandomSong();
        }
    }

    async loadRandomSong() {
        try {
            const playButtons = document.querySelectorAll('.play-button');
            if (playButtons && playButtons.length > 0) {
                const randomIndex = Math.floor(Math.random() * playButtons.length);
                const randomButton = playButtons[randomIndex];
                
                console.log('Loading random song at index:', randomIndex);
                
                // Get song data from the button
                const songData = {
                    id: randomButton.dataset.songId,
                    url: randomButton.dataset.songUrl,
                    title: randomButton.dataset.songTitle,
                    artist: randomButton.dataset.songArtist,
                    image: randomButton.dataset.songImage
                };

                // Save as current song
                this.currentSongData = songData;
                this.currentButton = randomButton;
                this.currentSong = songData.id;

                // Update audio source
                this.audio.src = songData.url;
                
                // Update player UI
                this.updatePlayerInfo(songData);
                
                // Save to localStorage
                localStorage.setItem('lastPlayedSong', JSON.stringify(songData));
                localStorage.setItem('playerCurrentTime', '0');

                // Wait for metadata to load
                await new Promise((resolve) => {
                    const loadHandler = () => {
                        this.audio.removeEventListener('loadedmetadata', loadHandler);
                        resolve();
                    };
                    this.audio.addEventListener('loadedmetadata', loadHandler);
                });

                // Update duration and progress
                this.updateDuration();
                this.forceUpdateProgress(0);
                
                console.log('Random song loaded successfully');
            } else {
                console.warn('No songs available to play');
            }
        } catch (error) {
            console.error('Error loading random song:', error);
        }
    }
}

// Create global player instance
let player;

// Initialize player when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM Content Loaded, initializing player');
        player = new MusicPlayer();
        window.player = player; // Make it globally accessible
    });
} else {
    console.log('DOM already loaded, initializing player');
    player = new MusicPlayer();
    window.player = player; // Make it globally accessible
}

// Global function for toggling likes
function toggleLike(songId) {
    const likeButton = document.getElementById(`like-btn-${songId}`);
    const likesCountSpan = document.getElementById(`likes-count-${songId}`);
    
    fetch(`/music/songs/${songId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update button style
            if (data.is_liked) {
                likeButton.classList.remove('btn-outline-danger');
                likeButton.classList.add('btn-danger');
            } else {
                likeButton.classList.remove('btn-danger');
                likeButton.classList.add('btn-outline-danger');
            }
            
            // Update likes count
            likesCountSpan.textContent = data.likes_count;
        }
    })
    .catch(error => {
        console.error('Error toggling like:', error);
    });
}

// Global function for recording plays
function recordPlay(songId) {
    fetch(`/music/songs/${songId}/play/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const playsCountSpan = document.getElementById(`plays-count-${songId}`);
            if (playsCountSpan) {
                playsCountSpan.textContent = `${data.play_count} plays`;
            }
        }
    })
    .catch(error => {
        console.error('Error recording play:', error);
    });
}