lucide.createIcons();

const themeToggleBtns = document.querySelectorAll(".theme-toggle-handler");
const body = document.body;

const setTheme = (theme) => {
    // 1. Apply the dark-mode class to the body
    if (theme === "dark") {
        body.classList.add("dark-mode");
    } else {
        body.classList.remove("dark-mode");
    }

    // 2. Update the icon and toggle class for ALL theme buttons
    themeToggleBtns.forEach(btn => {
        if (theme === "dark") {
            btn.innerHTML = '<i data-lucide="moon"></i>';
        } else {
            btn.innerHTML = '<i data-lucide="sun"></i>';
        }
        btn.classList.toggle("toggled", theme === "dark");
    });
    
    // Re-create lucide icons for the newly set icons
    lucide.createIcons(); 
};

// Check for saved theme and apply it
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
    setTheme(savedTheme);
} else {
    setTheme("light");
}

// Add event listener to ALL theme buttons
themeToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        if (body.classList.contains("dark-mode")) {
            setTheme("light");
            localStorage.setItem("theme", "light");
        } else {
            setTheme("dark");
            localStorage.setItem("theme", "dark");
        }
    });
});

// home page js 

(function () {
    'use strict';

    // --- Particle Class ---
    class Particle {
        constructor(width, height, ctx) {
            this.width = width;
            this.height = height;
            this.ctx = ctx;
            this.reset();
        }
        reset() {
            this.x = Math.random() * this.width;
            this.y = Math.random() * this.height;
            this.radius = Math.random() * 3 + 1;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.color = `hsla(${Math.random() * 360}, 70%, 60%, 0.3)`;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            // Wrap around screen
            if (this.x < -50 || this.x > this.width + 50 || this.y < -50 || this.y > this.height + 50) {
                this.reset();
            }
        }
        draw() {
            this.ctx.beginPath();
            this.ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = this.color;
            this.ctx.shadowColor = this.color;
            this.ctx.shadowBlur = 15;
            this.ctx.fill();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // --- Cache DOM elements ---
        const errorDiv = document.querySelector('.error');
        const glassBox = document.querySelector('.glass-box');
        const categoryCards = document.querySelectorAll('.category-card:not(#toggle-other)');
        const categoryToggleBtn = document.getElementById('toggle-other');
        const canvas = document.getElementById('animated-bg');
        const searchInput = document.querySelector('.search-input');
        const resultsBox = document.querySelector('.results');
        const searchForm = document.querySelector('.hero-search-form');
        const dynamicSpan = document.querySelector('.dynamic-placeholder');
        // Handle case where resultsBox might not exist yet
        const historyContainer = resultsBox ? resultsBox.querySelector('.search-history') : null;

        // --- 1. Error Message Handler ---
        if (errorDiv) {
            const closeButton = errorDiv.querySelector('.error__close');
            if (closeButton) {
                const hideError = () => {
                    errorDiv.classList.add('fade-out');
                    errorDiv.addEventListener('animationend', () => errorDiv.remove(), { once: true });
                };
                const timer = setTimeout(hideError, 3000);
                closeButton.addEventListener('click', () => {
                    clearTimeout(timer);
                    hideError();
                });
            }
        }

        // --- 2. Glass Box Tilt (OPTIMIZED with RequestAnimationFrame) ---
        if (glassBox) {
            const getActiveImage = () => [...glassBox.querySelectorAll('.book-image')].find((img) => getComputedStyle(img).display !== 'none');
            let ticking = false;

            glassBox.addEventListener('mousemove', (e) => {
                if (!ticking) {
                    window.requestAnimationFrame(() => {
                        const rect = glassBox.getBoundingClientRect();
                        const rotateX = ((e.clientY - rect.top) / rect.height - 0.5) * 10;
                        const rotateY = ((e.clientX - rect.left) / rect.width - 0.5) * -10;
                        
                        const activeImg = getActiveImage();
                        if (activeImg) {
                            activeImg.style.transition = 'transform 0.1s ease-out';
                            activeImg.style.setProperty('--tilt-x', `${rotateY}deg`);
                            activeImg.style.setProperty('--tilt-y', `${rotateX}deg`);
                        }
                        ticking = false;
                    });
                    ticking = true;
                }
            });

            glassBox.addEventListener('mouseleave', () => {
                const activeImg = getActiveImage();
                if (activeImg) {
                    activeImg.style.transition = 'transform 0.4s ease-in-out';
                    activeImg.style.setProperty('--tilt-x', '0deg');
                    activeImg.style.setProperty('--tilt-y', '0deg');
                }
            });
        }

        // --- 3. Category Cards Toggle ---
        if (categoryCards.length && categoryToggleBtn) {
            let showingAll = false;
            const btnText = categoryToggleBtn.querySelector('div');
            const btnIcon = categoryToggleBtn.querySelector('i');

            const updateView = () => {
                categoryCards.forEach((card, i) => (card.style.display = showingAll || i < 17 ? 'inline-block' : 'none'));
                if (btnText) btnText.textContent = showingAll ? 'Show Less' : 'Other';
                if (btnIcon) btnIcon.setAttribute('data-lucide', showingAll ? 'circle-chevron-up' : 'circle-chevron-down');
                if (window.lucide) lucide.createIcons();
            };

            categoryToggleBtn.addEventListener('click', () => {
                showingAll = !showingAll;
                updateView();
            });
            updateView();
        }

        // --- 4. Animated Canvas (OPTIMIZED with IntersectionObserver) ---
        if (canvas) {
            const ctx = canvas.getContext('2d');
            let width = (canvas.width = window.innerWidth);
            let height = (canvas.height = window.innerHeight);
            const particles = Array.from({ length: 120 }, () => new Particle(width, height, ctx));
            
            let animationFrameId = null;
            let isAnimating = false;

            const animate = () => {
                ctx.clearRect(0, 0, width, height);
                particles.forEach((p) => {
                    p.update();
                    p.draw();
                });
                animationFrameId = requestAnimationFrame(animate);
            };

            const startAnimation = () => {
                if (!isAnimating) {
                    isAnimating = true;
                    animate();
                }
            };

            const stopAnimation = () => {
                isAnimating = false;
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
            };

            // Only run animation when hero section is visible
            const heroSection = document.querySelector('.hero-bg');
            if (heroSection) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) startAnimation();
                        else stopAnimation();
                    });
                });
                observer.observe(heroSection);
            } else {
                startAnimation(); // Fallback if no hero section found
            }

            // Resize handler
            let resizeTimer;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    stopAnimation();
                    width = canvas.width = window.innerWidth;
                    height = canvas.height = window.innerHeight;
                    particles.forEach((p) => {
                        p.width = width;
                        p.height = height;
                        p.reset();
                    });
                    startAnimation();
                }, 100);
            });
        }

        // --- 5. AJAX Search ---
        if (searchInput && resultsBox && searchForm && dynamicSpan && historyContainer) {
            
            // Dynamic Placeholder Animation
            const words = ['"Books"', '"Authors"', '"Genres"', '"Categories"', '"Stories"', '"Novels"'];
            let wordIdx = 0;
            
            const changeWord = () => {
                if (document.activeElement === searchInput || searchInput.value.trim() !== '' || document.hidden) return;
                dynamicSpan.classList.add('hide');
                setTimeout(() => {
                    wordIdx = (wordIdx + 1) % words.length;
                    dynamicSpan.textContent = words[wordIdx];
                    dynamicSpan.classList.remove('hide');
                }, 500);
            };
            setInterval(changeWord, 3000);
            
            // Search Logic
            let abortController;
            const searchUrl = searchForm.getAttribute('data-ajax-url'); // Get URL from HTML

            const fetchResults = async (query) => {
                if (abortController) abortController.abort();
                abortController = new AbortController();

                try {
                    // Use dynamic URL
                    const targetUrl = searchUrl ? 
                        `${searchUrl}?q=${encodeURIComponent(query)}` : 
                        `/book/ajax/search/?q=${encodeURIComponent(query)}`;

                    const response = await fetch(targetUrl, { signal: abortController.signal });
                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const data = await response.json();
                    const results = data.results;

                    historyContainer.innerHTML = '';
                    const fragment = document.createDocumentFragment();

                    const titleEl = document.createElement('div');
                    titleEl.className = 'search-history-title';
                    titleEl.textContent = `Results for "${query}"`;
                    fragment.appendChild(titleEl);

                    if (!results || results.length === 0) {
                        const noResult = document.createElement('div');
                        noResult.className = 'history-item';
                        noResult.innerHTML = `
                            <i data-lucide="search"></i>
                            <div class="history-item-info"><span class="history-item-title">No results found</span></div>`;
                        fragment.appendChild(noResult);
                    } else {
                        results.forEach((book) => {
                            const link = document.createElement('a');
                            link.href = `book/library/open/${book.slug}`; // Consider passing this base URL via data attr too
                            link.className = 'history-item';
                            // Simple text escaping
                            const safeTitle = book.title.replace(/[&<>"']/g, function(m) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#039;'}[m] });
                            const safeAuthor = book.author.replace(/[&<>"']/g, function(m) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#039;'}[m] });
                            
                            link.innerHTML = `
                                <i data-lucide="notebook"></i> 
                                <div class="history-item-info">
                                    <span class="history-item-title">${safeTitle}</span>
                                    <span class="history-item-author">by ${safeAuthor}</span>
                                </div>`;
                            fragment.appendChild(link);
                        });
                    }
                    
                    historyContainer.appendChild(fragment);
                    resultsBox.style.display = 'block';
                    if (window.lucide) lucide.createIcons({ root: historyContainer, nameAttr: 'data-lucide' });

                } catch (err) {
                    if (err.name === 'AbortError') return;
                    console.error(err);
                }
            };

            let typingTimer;
            searchInput.addEventListener('input', () => {
                clearTimeout(typingTimer);
                const query = searchInput.value.trim();
                if (query.length > 1) {
                    resultsBox.style.display = 'block';
                    searchForm.style.borderRadius = '0.875rem 0.875rem 0 0';
                    
                    // Skeleton Loader
                    const skeletonItem = `
                        <div class="skeleton-item">
                            <div class="skeleton-icon"></div>
                            <div class="skeleton-text-col"><div class="skeleton-line long"></div><div class="skeleton-line short"></div></div>
                        </div>`;
                    historyContainer.innerHTML = `<div class="search-history-title">Searching...</div>${skeletonItem.repeat(3)}`;
                    
                    typingTimer = setTimeout(() => fetchResults(query), 300);
                } else {
                    resultsBox.style.display = 'none';
                    searchForm.style.borderRadius = '0.875rem';
                }
            });

            // Hide on outside click
            document.addEventListener('click', (e) => {
                if (!searchForm.contains(e.target)) {
                    resultsBox.style.display = 'none';
                    searchForm.style.borderRadius = '0.875rem';
                }
            });
            
            // Show on focus
            searchInput.addEventListener('focus', () => {
                if (searchInput.value.trim().length > 1) {
                    resultsBox.style.display = 'block';
                    searchForm.style.borderRadius = '0.875rem 0.875rem 0 0';
                }
            });
        }
    });
})();