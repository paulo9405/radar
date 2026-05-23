● I'll create a comprehensive architecture and structure proposal for the Trends Radar landing page. Let me present the complete plan.

  PROJECT ARCHITECTURE PROPOSAL

  1. DJANGO PROJECT STRUCTURE

  radar/
  ├── radar/                      # Main project folder
  │   ├── __init__.py
  │   ├── settings.py            # Project settings (modified)
  │   ├── urls.py                # Main URL config
  │   ├── wsgi.py
  │   └── asgi.py
  ├── landing/                    # Landing page app
  │   ├── __init__.py
  │   ├── models.py              # Lead model
  │   ├── views.py               # Form handling and page view
  │   ├── urls.py                # App URLs
  │   ├── forms.py               # Lead form
  │   ├── admin.py               # Admin configuration
  │   ├── apps.py
  │   ├── migrations/
  │   │   └── __init__.py
  │   ├── templates/
  │   │   └── landing/
  │   │       ├── index.html     # Main landing page
  │   │       ├── base.html      # Base template (optional)
  │   │       └── partials/      # Reusable components
  │   │           ├── hero.html
  │   │           ├── pain.html
  │   │           ├── features.html
  │   │           ├── benefits.html
  │   │           ├── early_access.html
  │   │           └── faq.html
  │   └── static/
  │       └── landing/
  │           ├── css/
  │           │   └── style.css  # Custom styles
  │           ├── js/
  │           │   └── main.js    # Form interactions, animations
  │           └── images/
  │               └── (mockup images if needed)
  ├── manage.py
  └── requirements.txt

  ---
  2. DATABASE MODEL

  landing/models.py
  from django.db import models
  from django.core.validators import RegexValidator

  class Lead(models.Model):
      PRICE_CHOICES = [
          ('29', 'R$29/month'),
          ('49', 'R$49/month'),
          ('99', 'R$99/month'),
          ('annual', 'Would pay annual plan with discount'),
          ('free_first', 'Would only try it free first'),
          ('other', 'Other'),
      ]

      name = models.CharField(max_length=200, verbose_name='Name')
      niche = models.CharField(max_length=300, verbose_name='Niche/Product')

      phone_regex = RegexValidator(
          regex=r'^\+?1?\d{9,15}$',
          message="Phone number must be entered in valid format."
      )
      whatsapp = models.CharField(
          validators=[phone_regex],
          max_length=17,
          verbose_name='WhatsApp'
      )

      email = models.EmailField(verbose_name='Email')
      price_range = models.CharField(
          max_length=20,
          choices=PRICE_CHOICES,
          verbose_name='Price Range'
      )
      created_at = models.DateTimeField(auto_now_add=True)

      class Meta:
          verbose_name = 'Lead'
          verbose_name_plural = 'Leads'
          ordering = ['-created_at']

      def __str__(self):
          return f"{self.name} - {self.email}"

  ---
  3. FORMS

  landing/forms.py
  from django import forms
  from .models import Lead

  class LeadForm(forms.ModelForm):
      class Meta:
          model = Lead
          fields = ['name', 'niche', 'whatsapp', 'email', 'price_range']
          widgets = {
              'name': forms.TextInput(attrs={
                  'class': 'form-control',
                  'placeholder': 'Your name'
              }),
              'niche': forms.TextInput(attrs={
                  'class': 'form-control',
                  'placeholder': 'e.g., Electronics, Fashion, Home decor'
              }),
              'whatsapp': forms.TextInput(attrs={
                  'class': 'form-control',
                  'placeholder': '+55 11 99999-9999'
              }),
              'email': forms.EmailInput(attrs={
                  'class': 'form-control',
                  'placeholder': 'your@email.com'
              }),
              'price_range': forms.Select(attrs={
                  'class': 'form-select'
              }),
          }

  ---
  4. VIEWS

  landing/views.py
  from django.shortcuts import render, redirect
  from django.contrib import messages
  from .forms import LeadForm

  def index(request):
      if request.method == 'POST':
          form = LeadForm(request.POST)
          if form.is_valid():
              form.save()
              messages.success(
                  request,
                  'Registration received. You have joined the Trends Radar early access list.'
              )
              return redirect('landing:index')
      else:
          form = LeadForm()

      return render(request, 'landing/index.html', {'form': form})

  ---
  5. URL CONFIGURATION

  landing/urls.py
  from django.urls import path
  from . import views

  app_name = 'landing'

  urlpatterns = [
      path('', views.index, name='index'),
  ]

  radar/urls.py (main project)
  from django.contrib import admin
  from django.urls import path, include

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('', include('landing.urls')),
  ]

  ---
  6. ADMIN CONFIGURATION

  landing/admin.py
  from django.contrib import admin
  from .models import Lead

  @admin.register(Lead)
  class LeadAdmin(admin.ModelAdmin):
      list_display = ['name', 'email', 'whatsapp', 'niche', 'price_range', 'created_at']
      list_filter = ['price_range', 'created_at']
      search_fields = ['name', 'email', 'niche']
      readonly_fields = ['created_at']
      date_hierarchy = 'created_at'

  ---
  7. SETTINGS.PY MODIFICATIONS

  # Add to INSTALLED_APPS
  INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      'landing',  # NEW
  ]

  # Static files configuration
  STATIC_URL = '/static/'
  STATIC_ROOT = BASE_DIR / 'staticfiles'

  # Language and timezone (optional - keep as is or adjust)
  LANGUAGE_CODE = 'en-us'
  TIME_ZONE = 'America/Sao_Paulo'  # or your timezone

  ---
  8. LANDING PAGE SECTIONS WIREFRAME

  Structure flow:

  ┌─────────────────────────────────────────────┐
  │  NAVIGATION (optional minimal nav/logo)     │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  1. HERO SECTION                            │
  │  - Headline + Subheadline                   │
  │  - CTA Button (scroll to form)              │
  │  - Product Analysis Mockup Card (visual)    │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  2. PAIN SECTION                            │
  │  - Title + Description                      │
  │  - 5 pain point bullets (icons + text)     │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  3. WHAT THE AI ANALYZES                    │
  │  - Grid of 8 feature cards                 │
  │  - Each with icon + title + brief text     │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  4. BENEFITS SECTION                        │
  │  - Title                                    │
  │  - 5 benefit items (checkmarks + text)     │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  5. EARLY ACCESS SECTION + FORM             │
  │  - Title + description                      │
  │  - Form card (centered, elevated)           │
  │  - Submit button                            │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  6. FAQ SECTION                             │
  │  - 4 Q&A items (accordion or simple)       │
  └─────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────┐
  │  FOOTER (minimal)                           │
  │  - Copyright, maybe social links            │
  └─────────────────────────────────────────────┘

  ---
  9. VISUAL STRATEGY

  Color Palette:
  - Background: #0a0e1a (deep dark blue/black)
  - Secondary background: #131825 (slightly lighter)
  - Accent primary: #00d4ff (cyan/neon blue)
  - Accent secondary: #0066ff (electric blue)
  - Text primary: #ffffff
  - Text secondary: #a0aec0 (muted gray)
  - Card backgrounds: #1a1f2e with subtle gradient
  - Success green: #00ff88 (for positive indicators)

  Typography:
  - Headings: Inter, -apple-system, system-ui (clean, modern)
  - Body: Same as headings for consistency
  - Font weights: 300 (light), 400 (regular), 600 (semibold), 700 (bold)

  Component Design:

  1. Hero Mockup Card:
    - Floating card with subtle shadow and glow
    - Gradient border (cyan to blue)
    - Stats displayed in clean grid
    - Score displayed prominently with radial gradient
    - Confidence indicator with color coding
  2. Feature Cards:
    - Dark background with subtle border
    - Icon at top (Bootstrap Icons)
    - Hover effect: subtle lift + glow
    - 2x4 or 4x2 grid on desktop, stack on mobile
  3. Form Design:
    - Centered card, max-width 600px
    - Dark input fields with cyan focus border
    - Large, prominent submit button with gradient
    - Clean spacing between fields
    - Success message: full-width banner with icon
  4. Buttons:
    - Primary CTA: Gradient (cyan to blue) + hover glow
    - Large padding, rounded corners
    - Smooth transitions
  5. Spacing:
    - Large section padding: 100px top/bottom (desktop)
    - Medium padding: 60px (tablet)
    - Mobile padding: 40px
    - Generous whitespace between elements

  Animations:
  - Fade in on scroll (hero, sections)
  - Subtle hover effects (cards, buttons)
  - Smooth transitions (0.3s ease)
  - Form submit animation
  - NO excessive animations - keep it professional

  Responsive Breakpoints:
  - Mobile: < 768px (stack everything)
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

  ---
  10. TECHNICAL IMPLEMENTATION NOTES

  Dependencies needed (requirements.txt):
  Django>=4.2,<5.0

  Bootstrap & Icons:
  - Use Bootstrap 5.3 CDN for speed
  - Bootstrap Icons CDN
  - Custom CSS for dark theme overrides

  JavaScript:
  - Smooth scroll to form on CTA click
  - Form validation enhancement
  - Scroll animations (Intersection Observer API)
  - Simple, vanilla JS - no heavy frameworks

  SEO Basics:
  - Meta tags for title, description
  - Open Graph tags for social sharing
  - Viewport meta tag
  - Favicon

  ---
  11. DEVELOPMENT CHECKLIST

  Phase 1: Setup
  - Create Django project
  - Create landing app
  - Configure settings.py
  - Set up static files

  Phase 2: Backend
  - Create Lead model
  - Create LeadForm
  - Configure admin
  - Create view and URL routing
  - Run migrations

  Phase 3: Frontend
  - Build base template structure
  - Hero section
  - Pain section
  - Features section
  - Benefits section
  - Form section
  - FAQ section
  - Footer

  Phase 4: Styling
  - Custom CSS (dark theme, gradients)
  - Responsive design
  - Animations
  - Form styling

  Phase 5: Testing
  - Form submission test
  - Mobile responsiveness
  - Cross-browser check
  - Admin panel check

  ---
  SUMMARY

  This architecture prioritizes:
  - Simplicity: Single app, minimal dependencies
  - Speed: Quick to implement, fast to load
  - Clean code: Organized structure, reusable components
  - Scalability: Easy to add features later if validated
  - Professional look: Modern SaaS aesthetic

  The approach uses Django's built-in features (forms, admin, messages) without overengineering. Bootstrap provides the responsive foundation, while custom CSS creates the premium dark mode aesthetic.

  Ready to proceed with implementation? I'll wait for your approval before creating any files.
