// Radar de Tendências - Enhanced JavaScript
// Premium interactions and AI intelligence indicators

document.addEventListener('DOMContentLoaded', function() {

    // ==========================
    // SMOOTH SCROLL
    // ==========================
    const smoothScrollLinks = document.querySelectorAll('.smooth-scroll');

    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ==========================
    // INTERSECTION OBSERVER - Fade in sections
    // ==========================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -80px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);

    // Observe sections for animation
    const sections = document.querySelectorAll('.how-it-works-section, .problem-section, .features-section, .form-section, .faq-section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(40px)';
        section.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
        observer.observe(section);
    });

    // ==========================
    // WHATSAPP INPUT FORMATTING
    // ==========================
    const whatsappInput = document.querySelector('input[name="whatsapp"]');

    if (whatsappInput) {
        whatsappInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove non-digits

            // Format as (XX) XXXXX-XXXX
            if (value.length > 0) {
                if (value.length <= 2) {
                    value = `(${value}`;
                } else if (value.length <= 7) {
                    value = `(${value.slice(0, 2)}) ${value.slice(2)}`;
                } else {
                    value = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7, 11)}`;
                }
            }

            e.target.value = value;
        });
    }

    // ==========================
    // ENHANCED FORM VALIDATION - Loading state + Scroll to error
    // ==========================
    const form = document.querySelector('form');

    if (form) {
        // Handle client-side validation on submit
        form.addEventListener('submit', function(e) {
            // Find all required inputs
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            let firstInvalidField = null;

            // Check each required field
            inputs.forEach(input => {
                // Remove previous error styling
                input.classList.remove('is-invalid');
                input.removeAttribute('aria-invalid');

                // Check if field is empty
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    input.setAttribute('aria-invalid', 'true');

                    if (!firstInvalidField) {
                        firstInvalidField = input;
                    }
                }
            });

            // If there's an invalid field, scroll to it and prevent submission
            if (firstInvalidField) {
                e.preventDefault();

                // Scroll to first invalid field smoothly
                firstInvalidField.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });

                // Focus the field after scroll completes
                setTimeout(() => {
                    firstInvalidField.focus({ preventScroll: true });
                }, 300);

                return false;
            }

            // If validation passes, show loading state
            const submitButton = form.querySelector('.submit-button, .submit-button-conversion');

            if (submitButton) {
                const buttonText = submitButton.querySelector('.button-text');
                if (buttonText) {
                    buttonText.textContent = 'Enviando...';
                }
                submitButton.disabled = true;
                submitButton.style.opacity = '0.7';

                // Add spinner
                const spinner = document.createElement('div');
                spinner.className = 'spinner-border spinner-border-sm me-2';
                spinner.setAttribute('role', 'status');
                submitButton.prepend(spinner);
            }
        });

        // Remove error styling on input
        const formInputs = form.querySelectorAll('input, textarea');
        formInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                this.removeAttribute('aria-invalid');
            });
        });
    }

    // ==========================
    // SCROLL TO SERVER-SIDE ERRORS ON PAGE LOAD
    // ==========================
    document.addEventListener('DOMContentLoaded', function() {
        // Check if there are any Django form errors displayed
        const firstError = document.querySelector('.invalid-feedback.d-block');

        if (firstError) {
            // Find the parent form group
            const formGroup = firstError.closest('.mb-4');

            if (formGroup) {
                const input = formGroup.querySelector('input, textarea');

                if (input) {
                    // Add is-invalid class for styling
                    input.classList.add('is-invalid');
                    input.setAttribute('aria-invalid', 'true');

                    // Scroll to the field smoothly
                    setTimeout(() => {
                        input.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });

                        // Focus after scroll
                        setTimeout(() => {
                            input.focus({ preventScroll: true });
                        }, 300);
                    }, 100);
                }
            }
        }
    });

    // ==========================
    // AUTO-DISMISS ALERTS
    // ==========================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 6000);
    });

    // ==========================
    // MOCKUP CARD ANIMATIONS
    // ==========================

    // Animate score ring on scroll
    const mockupCard = document.querySelector('.mockup-card');
    if (mockupCard) {
        const cardObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('animated-score')) {
                    entry.target.classList.add('animated-score');

                    // Trigger score animation
                    const scoreRingProgress = entry.target.querySelector('.score-ring-progress');
                    if (scoreRingProgress) {
                        scoreRingProgress.style.animation = 'drawCircle 2s ease-in-out forwards';
                    }
                }
            });
        }, { threshold: 0.3 });

        cardObserver.observe(mockupCard);
    }

    // ==========================
    // STEP CARDS HOVER EFFECT
    // ==========================
    const stepCards = document.querySelectorAll('.step-card');
    stepCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.15}s`;

        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // ==========================
    // FEATURE CARDS STAGGER ANIMATION
    // ==========================
    const featureCards = document.querySelectorAll('.feature-card');
    const featureObserver = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });

    featureCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
        featureObserver.observe(card);
    });

    // ==========================
    // PROBLEM CARDS ANIMATION
    // ==========================
    const problemCards = document.querySelectorAll('.problem-card');
    const problemObserver = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, index * 150);
            }
        });
    }, { threshold: 0.2 });

    problemCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-40px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.15}s, transform 0.6s ease ${index * 0.15}s`;
        problemObserver.observe(card);
    });

    // ==========================
    // SCROLL PROGRESS INDICATOR (header background)
    // ==========================
    const header = document.querySelector('.landing-header');
    if (header) {
        window.addEventListener('scroll', function() {
            const scrollProgress = window.pageYOffset;

            if (scrollProgress > 100) {
                header.style.backgroundColor = 'rgba(10, 14, 26, 0.95)';
                header.style.borderBottom = '1px solid rgba(0, 212, 255, 0.1)';
            } else {
                header.style.backgroundColor = 'transparent';
                header.style.borderBottom = 'none';
            }
        });
    }

    // ==========================
    // FORM FIELD FOCUS ENHANCEMENT
    // ==========================
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateX(4px)';
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateX(0)';
        });
    });

    // ==========================
    // ACCORDION SMOOTH EXPAND
    // ==========================
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add subtle glow to active accordion
            setTimeout(() => {
                const activeItem = document.querySelector('.accordion-button:not(.collapsed)');
                if (activeItem) {
                    activeItem.closest('.accordion-item').style.boxShadow = '0 8px 24px rgba(0, 212, 255, 0.15)';
                }

                // Remove glow from inactive
                const inactiveItems = document.querySelectorAll('.accordion-button.collapsed');
                inactiveItems.forEach(item => {
                    item.closest('.accordion-item').style.boxShadow = 'none';
                });
            }, 300);
        });
    });

    // ==========================
    // DYNAMIC METRICS COUNTER (subtle number animation)
    // ==========================
    const metricValues = document.querySelectorAll('.metric-value');

    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    // Observe metrics for number animation
    const metricsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');

                // Example: if text contains numbers, animate them
                const text = entry.target.textContent;
                const numberMatch = text.match(/\d+/);

                if (numberMatch) {
                    const finalNumber = parseInt(numberMatch[0]);
                    // Subtle count-up animation could be added here if needed
                }
            }
        });
    }, { threshold: 0.5 });

    metricValues.forEach(metric => {
        metricsObserver.observe(metric);
    });

    // ==========================
    // PREVENT DOUBLE FORM SUBMISSION
    // ==========================
    if (form) {
        let isSubmitting = false;

        form.addEventListener('submit', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                return false;
            }
            isSubmitting = true;
        });
    }

    // ==========================
    // CONSOLE MESSAGE (Easter egg for developers)
    // ==========================
    console.log(
        '%c🚀 Radar de Tendências',
        'color: #00d4ff; font-size: 20px; font-weight: bold;'
    );
    console.log(
        '%cInteligência de mercado com IA',
        'color: #94a3b8; font-size: 14px;'
    );
    console.log(
        '%cInteressado em fazer parte da equipe? Entre em contato!',
        'color: #10b981; font-size: 12px;'
    );
});
