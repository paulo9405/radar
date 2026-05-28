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

    // ==========================
    // NEW CONVERSION FLOW - INTERACTIVE ANALYSIS
    // ==========================

    const productInput = document.getElementById('product-input');
    const analyzeButton = document.getElementById('analyze-button');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const analysisResults = document.getElementById('analysis-results');
    const unlockForm = document.getElementById('unlock-form');
    const contactInput = document.getElementById('contact-input');
    const contactError = document.getElementById('contact-error');

    let currentProduct = '';
    let userContact = '';
    let feedbackData = {};
    let analysisCount = 0;
    const MAX_ANALYSES = 2;

    // Check analysis count from localStorage
    function getAnalysisCount() {
        const count = localStorage.getItem('analysis_count');
        const timestamp = localStorage.getItem('analysis_timestamp');
        const today = new Date().toDateString();

        // Reset count if it's a new day
        if (timestamp !== today) {
            localStorage.setItem('analysis_count', '0');
            localStorage.setItem('analysis_timestamp', today);
            return 0;
        }

        return parseInt(count || '0');
    }

    function incrementAnalysisCount() {
        analysisCount = getAnalysisCount() + 1;
        localStorage.setItem('analysis_count', analysisCount.toString());
        localStorage.setItem('analysis_timestamp', new Date().toDateString());
        return analysisCount;
    }

    function hasReachedLimit() {
        return getAnalysisCount() >= MAX_ANALYSES;
    }

    // Initialize analysis count
    analysisCount = getAnalysisCount();

    // Loading sequence messages (analytical and procedural)
    const loadingMessages = [
        'Analisando sinais de mercado...',
        'Verificando densidade de vendedores...',
        'Comparando tendências recentes...',
        'Calculando saturação estimada...'
    ];

    // Rotating product placeholders
    const productPlaceholders = [
        'Mini impressora térmica',
        'Projetor portátil',
        'Smartwatch infantil',
        'Escova secadora rotativa',
        'Câmera veicular',
        'Fone bluetooth gamer'
    ];

    let currentPlaceholderIndex = 0;

    // Rotate placeholders every 3 seconds
    if (productInput) {
        setInterval(() => {
            currentPlaceholderIndex = (currentPlaceholderIndex + 1) % productPlaceholders.length;

            // Fade transition
            productInput.style.transition = 'opacity 0.3s ease';
            productInput.style.opacity = '0.5';

            setTimeout(() => {
                productInput.placeholder = 'Ex: ' + productPlaceholders[currentPlaceholderIndex];
                productInput.style.opacity = '1';
            }, 300);
        }, 3000);
    }

    // Analyze product button click
    if (analyzeButton && productInput) {
        analyzeButton.addEventListener('click', function() {
            const product = productInput.value.trim();

            if (!product) {
                productInput.focus();
                productInput.style.borderColor = 'var(--error)';
                setTimeout(() => {
                    productInput.style.borderColor = '';
                }, 2000);
                return;
            }

            // Check analysis limit
            if (hasReachedLimit()) {
                showLimitScreen();
                return;
            }

            currentProduct = product;

            // Track event
            if (typeof clarity !== 'undefined') {
                clarity('set', 'product_analyzed', product);
            }

            startAnalysis(product);
        });

        // Allow Enter key to trigger analysis
        productInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeButton.click();
            }
        });
    }

    function startAnalysis(product) {
        // Show loading overlay
        loadingOverlay.style.display = 'flex';

        // Disable hero input
        productInput.disabled = true;
        analyzeButton.disabled = true;

        let messageIndex = 0;
        const messageInterval = 800; // Change message every 800ms
        const totalDuration = 3000; // Total loading time: 3 seconds

        // Cycle through loading messages
        const messageTimer = setInterval(() => {
            messageIndex++;
            if (messageIndex < loadingMessages.length) {
                loadingText.textContent = loadingMessages[messageIndex];
            }
        }, messageInterval);

        // Complete analysis after total duration
        setTimeout(() => {
            clearInterval(messageTimer);
            showPartialAnalysis(product);
        }, totalDuration);
    }

    function showPartialAnalysis(product) {
        // Hide loading
        loadingOverlay.style.display = 'none';

        // Increment analysis count
        incrementAnalysisCount();

        // Generate analysis data
        const analysis = generateAnalysis(product);

        // Update partial analysis content
        document.getElementById('analysis-product-name').textContent = product;
        document.getElementById('status-text').textContent = analysis.status;
        document.getElementById('trend-text').textContent = analysis.trendText;
        document.getElementById('competition-text').textContent = analysis.competitionText;
        document.getElementById('saturation-text').textContent = analysis.saturationText;
        document.getElementById('opportunity-text').textContent = analysis.opportunityText;
        document.getElementById('partial-insight').textContent = analysis.partialInsight;

        // Update status badge style
        const statusBadge = document.getElementById('analysis-status-badge');
        statusBadge.className = 'analysis-status-badge';
        if (analysis.statusLevel === 'warning') {
            statusBadge.classList.add('status-warning');
        } else if (analysis.statusLevel === 'danger') {
            statusBadge.classList.add('status-danger');
        }

        // Show testimonial
        const testimonial = document.getElementById('micro-testimonial');
        if (testimonial) {
            testimonial.style.display = 'block';
        }

        // Scroll to and show results
        analysisResults.style.display = 'block';
        setTimeout(() => {
            analysisResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    function showLimitScreen() {
        // Hide hero form
        document.getElementById('product-input-form').style.display = 'none';

        // Show limit message
        const heroContent = document.querySelector('.hero-content-centered');
        const limitMessage = document.createElement('div');
        limitMessage.className = 'limit-message-card';
        limitMessage.innerHTML = `
            <div class="limit-icon">
                <i class="bi bi-clock-history"></i>
            </div>
            <h2 class="limit-title">Limite de análises atingido</h2>
            <p class="limit-text">Você atingiu o limite gratuito de análises por agora.</p>
            <p class="limit-subtext">Estamos liberando novos acessos gradualmente durante a fase beta.</p>
            <div class="limit-action">
                <p class="limit-cta-text">Entre na lista para acesso prioritário:</p>
                <a href="#final-cta" class="btn-limit-cta smooth-scroll">ENTRAR NA LISTA</a>
            </div>
        `;
        heroContent.appendChild(limitMessage);
    }

    // Simple hash function for deterministic product analysis
    function hashString(str) {
        let hash = 0;
        const normalized = str.toLowerCase().trim();
        for (let i = 0; i < normalized.length; i++) {
            const char = normalized.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash);
    }

    function generateAnalysis(product) {
        // Deterministic analysis based on product name
        // Same product always returns same result (critical for trust)

        const analysisProfiles = {
            trending: {
                status: 'Crescimento forte detectado',
                statusLevel: 'success',
                trendText: '+78% nas buscas nas últimas semanas',
                competitionText: '~45 vendedores ativos detectados',
                saturationText: 'Saturação estimada em 15% (amplo espaço)',
                opportunityText: 'Janela estimada: próximos 60-90 dias',
                partialInsight: 'Crescimento acelerado detectado. Baixa concorrência. Mercado permite entrada rápida.',
                fullInsight: 'Produto apresenta crescimento forte com concorrência baixa. Momento favorável para entrada no mercado.',
                statusLabel: 'CRESCIMENTO FORTE',
                trendDetail: '+78% nas buscas (últimas 4 semanas)',
                competitionDetail: '~45 vendedores ativos no ML',
                saturationDetail: 'Estimada em 15% (amplo espaço)',
                recommendationDetail: 'Mercado permite entrada rápida',
                recommendationReason: 'Janela ampla para testar. Validar fornecedor.'
            },

            moderate: {
                status: 'Crescimento detectado',
                statusLevel: 'success',
                trendText: 'Volume de buscas cresceu nas últimas semanas',
                competitionText: '~120 vendedores ativos detectados',
                saturationText: 'Saturação estimada em 35% (espaço disponível)',
                opportunityText: 'Janela estimada: próximos 45-60 dias',
                partialInsight: 'Crescimento consistente detectado. Concorrência gerenciável. Mercado permite entrada com diferenciação.',
                fullInsight: 'Produto apresenta crescimento consistente com concorrência gerenciável. Momento adequado para entrada no mercado com diferenciação.',
                statusLabel: 'CRESCIMENTO DETECTADO',
                trendDetail: '+45% nas buscas (últimas 4 semanas)',
                competitionDetail: '~120 vendedores ativos no ML',
                saturationDetail: 'Estimada em 35% (espaço disponível)',
                recommendationDetail: 'Validar fornecedor antes de escalar',
                recommendationReason: 'Teste lote pequeno (50-100 un). Janela: 45-60 dias.'
            },

            saturated: {
                status: 'Sinais mistos detectados',
                statusLevel: 'warning',
                trendText: 'Crescimento desacelerando nas últimas semanas',
                competitionText: '~340 vendedores ativos detectados',
                saturationText: 'Saturação estimada em 72% (espaço limitado)',
                opportunityText: 'Janela curta para entrada',
                partialInsight: 'Mercado apresenta sinais de saturação. Alta concorrência. Entrada exige diferenciação forte.',
                fullInsight: 'Produto com saturação elevada e concorrência intensa. Entrada requer posicionamento diferenciado ou margem apertada.',
                statusLabel: 'ALTA CONCORRÊNCIA',
                trendDetail: 'Crescimento desacelerando',
                competitionDetail: '~340 vendedores ativos no ML',
                saturationDetail: 'Estimada em 72% (espaço limitado)',
                recommendationDetail: 'Alta concorrência reduz margem',
                recommendationReason: 'Evite sem diferenciação clara. Margem competitiva.'
            },

            declining: {
                status: 'Demanda enfraquecendo',
                statusLevel: 'danger',
                trendText: '-18% nas buscas nas últimas semanas',
                competitionText: '~260 vendedores ativos detectados',
                saturationText: 'Mercado próximo da saturação',
                opportunityText: 'Risco elevado para entrada',
                partialInsight: 'Demanda em queda. Concorrência alta. Mercado difícil para novos entrantes.',
                fullInsight: 'Produto apresenta demanda decrescente com concorrência estabelecida. Risco elevado para novos vendedores.',
                statusLabel: 'DEMANDA EM QUEDA',
                trendDetail: '-18% nas buscas (últimas 4 semanas)',
                competitionDetail: '~260 vendedores ativos no ML',
                saturationDetail: 'Mercado próximo da saturação',
                recommendationDetail: 'Produto exige cautela operacional',
                recommendationReason: 'Risco alto. Evite sem estratégia clara.'
            },

            seasonal: {
                status: 'Demanda sazonal detectada',
                statusLevel: 'warning',
                trendText: 'Volume oscilando nas últimas semanas',
                competitionText: '~90 vendedores ativos detectados',
                saturationText: 'Saturação moderada (40%)',
                opportunityText: 'Desempenho varia por período',
                partialInsight: 'Padrão sazonal detectado. Concorrência moderada. Pode funcionar com timing correto.',
                fullInsight: 'Produto apresenta demanda sazonal com variação significativa. Entrada depende do timing de mercado.',
                statusLabel: 'DEMANDA SAZONAL',
                trendDetail: 'Volume oscilando (padrão sazonal)',
                competitionDetail: '~90 vendedores ativos no ML',
                saturationDetail: 'Estimada em 40% (moderada)',
                recommendationDetail: 'Melhor desempenho em períodos específicos',
                recommendationReason: 'Validar sazonalidade antes de investir.'
            }
        };

        // Deterministic profile selection based on product hash
        const hash = hashString(product);
        const profileKeys = Object.keys(analysisProfiles);
        const selectedProfile = profileKeys[hash % profileKeys.length];

        return analysisProfiles[selectedProfile];
    }

    // Smart placeholder and formatting for contact input
    if (contactInput) {
        let isFormatting = false;

        contactInput.addEventListener('input', function(e) {
            if (isFormatting) return;

            const cursorPosition = e.target.selectionStart;
            const value = e.target.value;

            // Clear error on input
            contactError.style.display = 'none';
            contactInput.style.borderColor = '';

            // Detect if email (has @ or starts with letter)
            if (value.includes('@') || (value.length > 0 && /^[a-zA-Z]/.test(value))) {
                // Email mode
                contactInput.placeholder = 'voce@email.com';
                return; // Don't format emails
            }

            // Phone mode
            contactInput.placeholder = '(38) 99999-9999';

            // Only format if it starts with a digit
            if (value.length > 0 && !/^\d/.test(value.replace(/\D/g, ''))) {
                return;
            }

            // Remove all non-digits
            const cleaned = value.replace(/\D/g, '');

            // Apply formatting only if we have digits
            if (cleaned.length > 0) {
                isFormatting = true;

                let formatted = '';

                if (cleaned.length <= 2) {
                    formatted = cleaned;
                } else if (cleaned.length <= 7) {
                    formatted = `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`;
                } else {
                    formatted = `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`;
                }

                e.target.value = formatted;

                // Restore cursor position intelligently
                let newCursorPosition = cursorPosition;
                if (formatted.length < value.length) {
                    // Characters were removed (backspace)
                    newCursorPosition = cursorPosition;
                } else if (formatted.length > value.length) {
                    // Characters were added (formatting)
                    newCursorPosition = cursorPosition + (formatted.length - value.length);
                }

                // Set cursor position
                e.target.setSelectionRange(newCursorPosition, newCursorPosition);

                isFormatting = false;
            }
        });

        // Set initial placeholder
        contactInput.placeholder = '(38) 99999-9999';
    }

    // Unlock form submission
    if (unlockForm) {
        unlockForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const contact = contactInput.value.trim();

            if (!contact) {
                showContactError('Por favor, digite seu WhatsApp ou email');
                return;
            }

            // Basic validation
            const isEmail = contact.includes('@');
            const isPhone = /\d{10,11}/.test(contact.replace(/\D/g, ''));

            if (!isEmail && !isPhone) {
                showContactError('Digite um WhatsApp ou email válido');
                return;
            }

            userContact = contact;

            // Track event
            if (typeof clarity !== 'undefined') {
                clarity('set', 'contact_submitted', isEmail ? 'email' : 'whatsapp');
            }

            // Submit to backend
            submitContact(contact, currentProduct);

            // Show full analysis
            unlockFullAnalysis();
        });
    }

    function showContactError(message) {
        contactError.textContent = message;
        contactError.style.display = 'block';
        contactInput.style.borderColor = 'var(--error)';
        contactInput.focus();
    }

    function submitContact(contact, product) {
        // Submit contact to backend
        fetch('/api/submit-contact/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                contact: contact,
                product: product
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Contact submitted successfully:', data.lead_id);
                // Store lead ID for later updates
                window.currentLeadId = data.lead_id;
            }
        })
        .catch(error => {
            console.error('Error submitting contact:', error);
        });
    }

    function unlockFullAnalysis() {
        // Hide lock screen
        const lockScreen = document.getElementById('lock-screen');
        lockScreen.style.display = 'none';

        // Get analysis data
        const analysis = generateAnalysis(currentProduct);

        // Update full analysis content
        document.getElementById('full-product-name').textContent = currentProduct;
        document.getElementById('full-status-label').textContent = analysis.statusLabel;
        document.getElementById('full-insight').textContent = analysis.fullInsight;
        document.getElementById('trend-detail').textContent = analysis.trendDetail;
        document.getElementById('competition-detail').textContent = analysis.competitionDetail;
        document.getElementById('saturation-detail').textContent = analysis.saturationDetail;
        document.getElementById('recommendation-detail').textContent = analysis.recommendationDetail;
        document.getElementById('recommendation-reason').textContent = analysis.recommendationReason;

        // Show full analysis
        const fullAnalysis = document.getElementById('full-analysis');
        fullAnalysis.style.display = 'block';

        // Scroll to full analysis
        setTimeout(() => {
            fullAnalysis.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);

        // Show feedback section after a delay
        setTimeout(() => {
            showFeedbackSection();
        }, 2000);
    }

    function showFeedbackSection() {
        // Simplified: Go straight to purchase intent (Step 1)
        const purchaseSection = document.getElementById('purchase-intent-section');
        purchaseSection.style.display = 'block';

        setTimeout(() => {
            purchaseSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }

    // Purchase intent buttons (Step 1)
    const intentButtons = document.querySelectorAll('.intent-btn');
    intentButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            feedbackData.purchaseIntent = value;

            if (typeof clarity !== 'undefined') {
                clarity('set', 'purchase_intent', value);
            }

            // If answered yes or maybe, show launch interest
            // If answered no, skip to thank you
            if (value === 'yes' || value === 'maybe') {
                showLaunchInterest();
            } else {
                submitFeedback(feedbackData);
                showThankYou();
            }
        });
    });

    // Launch interest buttons (Step 2)
    const launchButtons = document.querySelectorAll('.launch-btn');
    launchButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            feedbackData.launchInterest = value === 'yes';

            if (typeof clarity !== 'undefined') {
                clarity('set', 'launch_interest', value);
            }

            // Submit all feedback data
            submitFeedback(feedbackData);

            showThankYou();
        });
    });

    function showLaunchInterest() {
        document.getElementById('purchase-intent-section').style.display = 'none';
        const launchSection = document.getElementById('launch-interest-section');
        launchSection.style.display = 'block';

        setTimeout(() => {
            launchSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }

    function submitFeedback(data) {
        // Submit feedback to backend
        fetch('/api/submit-feedback/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                lead_id: window.currentLeadId,
                contact: userContact,
                product: currentProduct,
                feedback: data
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                console.log('Feedback submitted successfully');
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
        });
    }

    function showThankYou() {
        // Hide all feedback sections
        document.getElementById('purchase-intent-section').style.display = 'none';
        const launchSection = document.getElementById('launch-interest-section');
        if (launchSection) {
            launchSection.style.display = 'none';
        }

        // Show thank you
        const thankYouSection = document.getElementById('thank-you-section');
        thankYouSection.style.display = 'block';

        setTimeout(() => {
            thankYouSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }

    // Helper function to get CSRF token
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
});
