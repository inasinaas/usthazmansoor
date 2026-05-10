document.addEventListener('DOMContentLoaded', () => {
    const videoGrid = document.getElementById('videoGrid');
    const categoryTabs = document.getElementById('categoryTabs');
    const searchInput = document.getElementById('searchInput');
    const noResults = document.getElementById('noResults');
    const videoModal = document.getElementById('videoModal');
    const closeModalBtn = document.getElementById('closeModal');
    const youtubePlayer = document.getElementById('youtubePlayer');
    const modalTitle = document.getElementById('modalTitle');
    const modalChannel = document.getElementById('modalChannel');
    const videoCounter = document.getElementById('videoCounter');
    const modalLink = document.getElementById('modalLink');

    let allVideos = [];
    let currentCategory = 'All';

    // Initialize with data from data.js
    if (typeof VIDEO_DATA !== 'undefined') {
        allVideos = VIDEO_DATA;
        
        // Sort Usthaz Mansoor's videos to the top
        allVideos.sort((a, b) => {
            const isAMansoor = isMansoorVideo(a);
            const isBMansoor = isMansoorVideo(b);
            if (isAMansoor && !isBMansoor) return -1;
            if (!isAMansoor && isBMansoor) return 1;
            return 0; // maintain original relative order
        });
        
        initApp();
    } else {
        console.error('VIDEO_DATA is not defined. Make sure data.js is loaded.');
        videoCounter.textContent = 'Error loading videos';
        videoGrid.innerHTML = '<p style="color: red; padding: 20px;">Failed to load videos. Please run the python script to generate data.js.</p>';
    }

    function isMansoorVideo(video) {
        const channelLower = video.channel.toLowerCase().replace(/\s/g, '');
        if (channelLower.includes('usthadmansoor') || channelLower.includes('mansoor')) return true;
        
        const textToCheck = video.title.toLowerCase();
        const keywords = ["mansoor", "மன்சூர்", "usthad", "usthaz", "usthaad", "உஸ்தாத்", "usthadh"];
        return keywords.some(kw => textToCheck.includes(kw));
    }

    function initApp() {
        renderCategories();
        renderVideos(allVideos);
        videoCounter.textContent = `Total Videos: ${allVideos.length}`;
    }

    function renderCategories() {
        // Extract unique categories
        const categories = ['All', ...new Set(allVideos.map(v => v.category).filter(Boolean))];

        categoryTabs.innerHTML = '';
        categories.forEach(category => {
            const li = document.createElement('li');
            const btn = document.createElement('button');
            btn.className = `category-btn ${category === 'All' ? 'active' : ''}`;
            btn.textContent = category;
            
            btn.addEventListener('click', () => {
                // Update active state
                document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                currentCategory = category;
                filterVideos();
            });

            li.appendChild(btn);
            categoryTabs.appendChild(li);
        });
    }

    function renderVideos(videos) {
        videoGrid.innerHTML = '';
        
        if (videos.length === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
            
            videos.forEach(video => {
                const card = document.createElement('div');
                card.className = 'video-card glass-panel';
                
                // Extract video ID from URL
                let videoId = video.id;
                if (video.url && video.url.includes('v=')) {
                    videoId = video.url.split('v=')[1].split('&')[0];
                }

                card.innerHTML = `
                    <div class="thumbnail-container">
                        <img src="${video.thumbnail || `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`}" alt="${video.title}" class="thumbnail" loading="lazy">
                        ${video.duration ? `<div class="duration-badge">${video.duration}</div>` : ''}
                        <div class="play-overlay">
                            <div class="play-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                            </div>
                        </div>
                    </div>
                    <div class="video-info">
                        <h3 class="video-title">${video.title}</h3>
                        <div class="video-meta">
                            <span class="channel-name">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-12.5v7l6-3.5z"/></svg>
                                ${video.channel}
                            </span>
                            ${video.view_count ? `<span class="views">${formatViews(video.view_count)} views</span>` : ''}
                        </div>
                    </div>
                `;

                card.addEventListener('click', () => openModal(video, videoId));
                videoGrid.appendChild(card);
            });
        }
    }

    function filterVideos() {
        const searchTerm = searchInput.value.toLowerCase();
        
        const filtered = allVideos.filter(video => {
            const matchesCategory = currentCategory === 'All' || video.category === currentCategory;
            const matchesSearch = video.title.toLowerCase().includes(searchTerm) || 
                                  video.channel.toLowerCase().includes(searchTerm);
            return matchesCategory && matchesSearch;
        });

        renderVideos(filtered);
        
        if (currentCategory === 'All' && searchTerm === '') {
            videoCounter.textContent = `Total Videos: ${filtered.length}`;
        } else {
            videoCounter.textContent = `Showing ${filtered.length} of ${allVideos.length} Videos`;
        }
    }

    // Search functionality
    searchInput.addEventListener('input', filterVideos);

    // Modal functionality
    function openModal(video, videoId) {
        // Using youtube-nocookie.com can sometimes bypass local file:// embed restrictions
        youtubePlayer.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`;
        modalTitle.textContent = video.title;
        modalChannel.textContent = video.channel;
        
        // Provide direct link in case embedding is disabled
        modalLink.href = `https://www.youtube.com/watch?v=${videoId}`;
        
        videoModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    function closeModal() {
        youtubePlayer.src = ''; // Stop video
        videoModal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    closeModalBtn.addEventListener('click', closeModal);
    videoModal.addEventListener('click', (e) => {
        if (e.target === videoModal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !videoModal.classList.contains('hidden')) {
            closeModal();
        }
    });

    function formatViews(views) {
        if (views >= 1000000) {
            return (views / 1000000).toFixed(1) + 'M';
        }
        if (views >= 1000) {
            return (views / 1000).toFixed(1) + 'K';
        }
        return views;
    }
});
