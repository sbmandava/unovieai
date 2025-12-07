// Advanced JavaScript for Enhanced Interactions

class UnovieWebsite {
    constructor() {
        this.init();
    }

    init() {
        this.initTheme();
        this.initMobileMenu();
        this.initScrollEffects();
        this.initParticles();
        this.initMagneticButtons();
        this.initRippleEffect();
        this.initParallax();
        this.initObserver();
        this.initSmoothScroll();
        this.initCounterAnimation();
        this.initTypewriter();
        this.initScrollProgress();
        this.initScrollReveal();
        this.initCursorEffects();
        this.initKeyboardNavigation();
    }

    // Theme Management
    initTheme() {
        const themeToggle = document.getElementById('darkModeToggle');
        const savedTheme = localStorage.getItem('theme');

        if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        }

        themeToggle?.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        });
    }

    // Mobile Menu
    initMobileMenu() {
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const mobileMenu = document.getElementById('mobileMenu');

        mobileMenuToggle?.addEventListener('click', () => {
            mobileMenu?.classList.toggle('hidden');
            mobileMenuToggle?.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#mobileMenuToggle') && !e.target.closest('#mobileMenu')) {
                mobileMenu?.classList.add('hidden');
                mobileMenuToggle?.classList.remove('active');
            }
        });
    }

    // Scroll Effects
    initScrollEffects() {
        let lastScrollY = window.scrollY;
        const header = document.querySelector('nav');

        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;

            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                header?.classList.add('-translate-y-full');
            } else {
                header?.classList.remove('-translate-y-full');
            }

            lastScrollY = currentScrollY;
        });
    }

    // Particle System
    initParticles() {
        const particleContainer = document.querySelector('.particle-bg');
        if (!particleContainer) return;

        const particleCount = 50;
        const particles = [];

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particleContainer.appendChild(particle);
            particles.push(particle);
        }

        // Animate particles on mouse move
        document.addEventListener('mousemove', (e) => {
            const mouseX = e.clientX / window.innerWidth;
            const mouseY = e.clientY / window.innerHeight;

            particles.forEach((particle, index) => {
                const speed = (index % 5 + 1) * 0.01;
                const x = (mouseX - 0.5) * speed * 100;
                const y = (mouseY - 0.5) * speed * 100;
                particle.style.transform = `translate(${x}px, ${y}px)`;
            });
        });
    }

    // Magnetic Button Effect
    initMagneticButtons() {
        const magneticButtons = document.querySelectorAll('.magnetic-button');

        magneticButtons.forEach(button => {
            button.addEventListener('mousemove', (e) => {
                const rect = button.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;

                button.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px) scale(1.05)`;
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translate(0, 0) scale(1)';
            });
        });
    }

    // Ripple Effect
    initRippleEffect() {
        const rippleButtons = document.querySelectorAll('.ripple');

        rippleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                ripple.className = 'ripple-effect';

                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';

                button.appendChild(ripple);

                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    // Parallax Effect
    initParallax() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;

            parallaxElements.forEach(element => {
                const speed = element.dataset.parallax || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    // Intersection Observer for Animations
    initObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slide-up');

                    // Add delay based on data-delay attribute
                    const delay = entry.target.dataset.delay || 0;
                    entry.target.style.animationDelay = `${delay}ms`;
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        document.querySelectorAll('.stagger-item, .feature-card, .text-reveal').forEach(el => {
            observer.observe(el);
        });
    }

    // Enhanced Smooth Scroll
    initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));

                if (target) {
                    const offsetTop = target.offsetTop - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });

                    // Update URL without page jump
                    history.pushState(null, null, anchor.getAttribute('href'));
                }
            });
        });
    }

    // Counter Animation
    initCounterAnimation() {
        const counters = document.querySelectorAll('[data-counter]');

        const updateCounter = (counter) => {
            const target = parseInt(counter.dataset.counter);
            const current = parseInt(counter.innerText);
            const increment = target / 100;

            if (current < target) {
                counter.innerText = Math.ceil(current + increment);
                setTimeout(() => updateCounter(counter), 20);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    // Typewriter Effect
    initTypewriter() {
        const typewriterElements = document.querySelectorAll('[data-typewriter]');

        typewriterElements.forEach(element => {
            const text = element.dataset.typewriter;
            let index = 0;

            const type = () => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                    setTimeout(type, 50);
                }
            };

            // Start typing when element is in view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        type();
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(element);
        });
    }

    // Scroll Progress Indicator
    initScrollProgress() {
        const progressBar = document.createElement('div');
        progressBar.className = 'fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-500 to-accent-500 z-50 transform origin-left scale-x-0 transition-transform';
        document.body.appendChild(progressBar);

        window.addEventListener('scroll', () => {
            const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (window.scrollY / windowHeight) * 100;
            progressBar.style.transform = `scaleX(${scrolled / 100})`;
        });
    }

    // Scroll Reveal Animation
    initScrollReveal() {
        const revealElements = document.querySelectorAll('[data-reveal]');

        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        revealElements.forEach(element => {
            element.classList.add('text-reveal');
            revealObserver.observe(element);
        });
    }

    // Custom Cursor Effects
    initCursorEffects() {
        const cursor = document.createElement('div');
        cursor.className = 'fixed w-4 h-4 bg-primary-500 rounded-full pointer-events-none z-50 mix-blend-difference';
        document.body.appendChild(cursor);

        const cursorFollower = document.createElement('div');
        cursorFollower.className = 'fixed w-8 h-8 border border-primary-500 rounded-full pointer-events-none z-50 transition-all duration-200';
        document.body.appendChild(cursorFollower);

        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX - 8 + 'px';
            cursor.style.top = e.clientY - 8 + 'px';

            setTimeout(() => {
                cursorFollower.style.left = e.clientX - 16 + 'px';
                cursorFollower.style.top = e.clientY - 16 + 'px';
            }, 100);
        });

        // Hide cursor when leaving window
        document.addEventListener('mouseleave', () => {
            cursor.style.opacity = '0';
            cursorFollower.style.opacity = '0';
        });

        document.addEventListener('mouseenter', () => {
            cursor.style.opacity = '1';
            cursorFollower.style.opacity = '1';
        });

        // Scale cursor on hover over interactive elements
        document.querySelectorAll('a, button, .card-hover').forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.style.transform = 'scale(2)';
                cursorFollower.style.transform = 'scale(1.5)';
            });

            el.addEventListener('mouseleave', () => {
                cursor.style.transform = 'scale(1)';
                cursorFollower.style.transform = 'scale(1)';
            });
        });
    }

    // Keyboard Navigation
    initKeyboardNavigation() {
        let focusableElements = [];
        let currentIndex = 0;

        const updateFocusableElements = () => {
            focusableElements = Array.from(document.querySelectorAll(
                'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
            )).filter(el => !el.hasAttribute('disabled'));
        };

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                updateFocusableElements();

                if (e.shiftKey) {
                    // Shift + Tab
                    currentIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
                } else {
                    // Tab
                    currentIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0;
                }

                e.preventDefault();
                focusableElements[currentIndex]?.focus();
            }

            // Escape key to close modals/menus
            if (e.key === 'Escape') {
                const mobileMenu = document.getElementById('mobileMenu');
                mobileMenu?.classList.add('hidden');
            }
        });

        // Initial setup
        updateFocusableElements();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new UnovieWebsite();
});

// Page load animations
window.addEventListener('load', () => {
    document.body.classList.add('loaded');

    // Fade in page elements
    const pageTransition = document.querySelectorAll('.page-transition');
    pageTransition.forEach((el, index) => {
        setTimeout(() => {
            el.classList.add('active');
        }, index * 100);
    });
});

// Performance optimization: Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Lazy loading for images
document.addEventListener('DOMContentLoaded', () => {
    const lazyImages = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    }, { rootMargin: '50px' });

    lazyImages.forEach(img => imageObserver.observe(img));
});

// Service Worker Registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}