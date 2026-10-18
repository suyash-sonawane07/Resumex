"""
Resumex Design System — Minimalist & Modern Theme
=================================================
Owner: Member 3

Translates modern minimal visual language into CSS custom properties
and Streamlit-compatible styles:
  - Clean porcelain off-white canvas (#fafaf9, #ffffff)
  - Refined quad-color harmony (Blue #4285F4, Red #EA4335, Yellow #FBBC04, Green #34A853)
  - Bold, clean display typography (Google Sans Flex / Inter)
  - Minimal pill-shaped buttons with dark primary actions (#111827)
  - Spacious cards with hairline borders (#e5e7eb) and zero neon clutter
"""

ANTIGRAVITY_LIGHT_TOKENS = {
    # System Tokens (Google Antigravity Foundations)
    "--font-family-primary": "'Google Sans Flex', 'Google Sans', sans-serif",
    "--font-size-base": "16px",
    "--font-weight-base": "400",
    "--font-line-height-base": "24px",
    "--font-size-xs": "12.5px",
    "--font-size-sm": "13px",
    "--font-size-md": "14.5px",
    "--font-size-lg": "16px",
    "--font-size-xl": "17.5px",
    "--font-size-2xl": "20px",
    "--font-size-3xl": "28px",
    "--font-size-4xl": "32px",
    "--color-text-primary": "#121317",
    "--color-text-secondary": "#45474d",
    "--color-text-tertiary": "#ffffff",
    "--color-text-inverse": "#6a6a71",
    "--color-surface-base": "#000000",
    "--color-surface-raised": "#b7bfd9",
    "--space-1": "4px",
    "--space-2": "6px",
    "--space-3": "8px",
    "--space-4": "10px",
    "--space-5": "16px",
    "--space-6": "24px",
    "--space-7": "36px",
    "--space-8": "55px",
    "--radius-xs": "4px",
    "--radius-sm": "36px",
    "--radius-md": "1584px",
    "--radius-lg": "9999px",
    "--motion-duration-instant": "150ms",
    "--motion-duration-fast": "200ms",
    "--motion-duration-normal": "300ms",

    # Semantic UI Component Aliases
    "--bui-text-primary": "#121317",
    "--bui-text-secondary": "#45474d",
    "--bui-text-tertiary": "#6a6a71",
    "--bui-text-error": "#ea4335",
    "--bui-bg-page": "#ffffff",
    "--bui-bg-card": "#ffffff",
    "--bui-bg-subtle": "#fafaf9",
    "--bui-bg-muted": "#f4f4f5",
    "--bui-border": "#e5e7eb",
    "--bui-border-strong": "#d1d5db",
    "--bui-separator": "#f3f4f6",
    "--bui-accent": "#000000",
    "--bui-accent-strong": "#121317",
    "--bui-accent-soft": "#f3f4f6",

    # Google Iconic Quad-Color Palette
    "--agy-blue": "#4285f4",
    "--agy-red": "#ea4335",
    "--agy-yellow": "#fbbc04",
    "--agy-green": "#34a853",

    # Semantic Status Tints
    "--bui-success-bg": "#e6f4ea",
    "--bui-success-text": "#137333",
    "--bui-warning-bg": "#fef7e0",
    "--bui-warning-text": "#b06000",
    "--bui-danger-bg": "#fce8e6",
    "--bui-danger-text": "#c5221f",
    "--bui-info-bg": "#e8f0fe",
    "--bui-info-text": "#1967d2",

    # Antigravity Chart Tokens
    "--bui-chart-1": "#34a853",  # Google Green (Core Met)
    "--bui-chart-2": "#4285f4",  # Google Blue (Context Met)
    "--bui-chart-3": "#ea4335",  # Google Red (Core Missing)
    "--bui-chart-4": "#fbbc04",  # Google Yellow
    "--bui-chart-5": "#e5e7eb",  # Neutral Track
    "--bui-focus-ring": "#000000",
    "--bui-sidebar-bg": "#fafaf9",
    "--bui-shadow-card": "0 1px 3px rgba(0, 0, 0, 0.03), 0 4px 16px rgba(0, 0, 0, 0.02)",
}

ANTIGRAVITY_DARK_TOKENS = {
    "--bui-text-primary": "#f9fafb",
    "--bui-text-secondary": "#9ca3af",
    "--bui-text-tertiary": "#6b7280",
    "--bui-text-error": "#f87171",
    "--bui-bg-page": "#111215",
    "--bui-bg-card": "#181a20",
    "--bui-bg-subtle": "#20232b",
    "--bui-bg-muted": "#2b2f3a",
    "--bui-border": "rgba(255, 255, 255, 0.09)",
    "--bui-border-strong": "rgba(255, 255, 255, 0.18)",
    "--bui-separator": "rgba(255, 255, 255, 0.06)",
    "--bui-accent": "#ffffff",
    "--bui-accent-strong": "#e5e7eb",
    "--bui-accent-soft": "rgba(255, 255, 255, 0.08)",
    "--agy-blue": "#8ab4f8",
    "--agy-red": "#f28b82",
    "--agy-yellow": "#fdd663",
    "--agy-green": "#81c995",
    "--bui-success-bg": "rgba(52, 168, 83, 0.15)",
    "--bui-success-text": "#81c995",
    "--bui-warning-bg": "rgba(251, 188, 4, 0.15)",
    "--bui-warning-text": "#fdd663",
    "--bui-danger-bg": "rgba(234, 67, 53, 0.15)",
    "--bui-danger-text": "#f28b82",
    "--bui-info-bg": "rgba(66, 133, 244, 0.15)",
    "--bui-info-text": "#8ab4f8",
    "--bui-chart-1": "#81c995",
    "--bui-chart-2": "#8ab4f8",
    "--bui-chart-3": "#f28b82",
    "--bui-chart-4": "#fdd663",
    "--bui-chart-5": "#374151",
    "--bui-focus-ring": "#8ab4f8",
    "--bui-sidebar-bg": "#14161b",
    "--bui-shadow-card": "0 4px 20px rgba(0, 0, 0, 0.35)",
}

# Alias for backwards compatibility
LIGHT_TOKENS = ANTIGRAVITY_LIGHT_TOKENS
DARK_TOKENS = ANTIGRAVITY_DARK_TOKENS

BASE_CSS = """
/* Antigravity Global Canvas & Viewport Rules */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stVerticalBlock"] {
  background-color: #ffffff !important;
  color: #121317 !important;
  font-family: 'Google Sans Flex', 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
  letter-spacing: -0.01em;
}

[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
  background-color: #fafaf9 !important;
  border-right: 1px solid #e5e7eb !important;
  color: #121317 !important;
}

/* Hide default streamlit header background */
header[data-testid="stHeader"] {
  background-color: rgba(255, 255, 255, 0.95) !important;
  border-bottom: 1px solid rgba(229, 231, 235, 0.6) !important;
}

/* Subtle Antigravity Ambient Orbital Background */
.stApp::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 520px;
  background:
    radial-gradient(ellipse 600px 300px at 50% -80px, rgba(66, 133, 244, 0.05) 0%, transparent 70%),
    radial-gradient(circle 350px at 15% 150px, rgba(52, 168, 83, 0.03) 0%, transparent 70%),
    radial-gradient(circle 350px at 85% 180px, rgba(251, 188, 4, 0.035) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* ─── Resumex Clean Intro Container ─── */
.rx-intro-container {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 4px 14px rgba(0, 0, 0, 0.02);
  padding: 1.6rem 2rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.rx-intro-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.85rem;
}

.rx-intro-brand {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.rx-brand-name {
  font-family: var(--font-family-primary);
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: #121317;
  line-height: 1.2;
}

.rx-brand-sub {
  font-size: 0.82rem;
  font-weight: 450;
  color: #6b7280;
  margin-top: 2px;
}

.rx-intro-tags {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.rx-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 550;
  padding: 4px 11px;
  border-radius: 9999px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #374151;
}

.rx-tag-sla {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #15803d;
}

.rx-tag-dpdp {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.rx-tag-explain {
  background: #fefce8;
  border-color: #fef08a;
  color: #a16207;
}

.rx-intro-desc {
  font-size: 0.92rem;
  line-height: 1.55;
  color: #4b5563;
  margin: 0;
}

/* Antigravity Hero Container (Legacy fallback) */
.bui-hero-container, .agy-hero-container {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}

/* Antigravity Dotted Orbital Pattern in Hero */
.agy-orbital-backdrop {
  position: absolute;
  top: -80px;
  right: -80px;
  width: 380px;
  height: 380px;
  border: 1px dashed rgba(66, 133, 244, 0.15);
  border-radius: 50%;
  pointer-events: none;
  animation: agy-spin 120s linear infinite;
}

.agy-orbital-backdrop-inner {
  position: absolute;
  top: 50px;
  left: 50px;
  width: 280px;
  height: 280px;
  border: 1px dashed rgba(234, 67, 53, 0.12);
  border-radius: 50%;
}

@keyframes agy-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Floating Google Accent Particles */
.agy-particle-blue {
  position: absolute;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #4285f4;
  opacity: 0.65;
  top: 25%;
  right: 18%;
  animation: agy-float 6s ease-in-out infinite;
}

.agy-particle-green {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34a853;
  opacity: 0.65;
  bottom: 22%;
  left: 4%;
  animation: agy-float 7s ease-in-out infinite 1s;
}

.agy-particle-yellow {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fbbc04;
  opacity: 0.7;
  top: 60%;
  right: 6%;
  animation: agy-float 8s ease-in-out infinite 2s;
}

.agy-particle-red {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ea4335;
  opacity: 0.65;
  top: 15%;
  left: 12%;
  animation: agy-float 5s ease-in-out infinite 0.5s;
}

@keyframes agy-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* Antigravity Minimal Navbar */
.bui-nav-bar, .agy-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.5rem;
  margin-bottom: 1.6rem;
  border-bottom: 1px solid var(--bui-separator);
  position: relative;
  z-index: 3;
}

.bui-brand-lockup, .agy-brand-lockup {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bui-brand-title, .agy-brand-title {
  font-family: var(--font-family-primary);
  font-size: 1.15rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

.bui-brand-title span, .agy-brand-title span {
  font-weight: 400;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
  margin-left: 6px;
}

.bui-nav-links, .agy-nav-links {
  display: flex;
  align-items: center;
  gap: 1.8rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  font-weight: 450;
}

.bui-nav-links span, .agy-nav-links span {
  cursor: pointer;
  transition: color var(--motion-duration-instant) ease;
}

.bui-nav-links span:hover, .agy-nav-links span:hover {
  color: var(--color-text-primary);
}

.bui-nav-link-active, .agy-nav-link-active {
  color: var(--color-text-primary);
  font-weight: 600;
}

.agy-nav-download-pill {
  background: var(--color-surface-base);
  color: var(--color-text-tertiary) !important;
  border-radius: var(--radius-lg);
  padding: 7px 18px;
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none !important;
  transition: all var(--motion-duration-instant) ease;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.agy-nav-download-pill:hover {
  background: #1f2937;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.agy-nav-lang-pill {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--bui-border);
  border-radius: var(--radius-lg);
  padding: 6px 13px;
  font-size: 0.82rem;
  font-weight: 450;
  cursor: pointer;
}

/* Antigravity Announcement Capsule */
.agy-announcement-capsule {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  background: #ffffff;
  border: 1px solid var(--bui-border);
  border-radius: var(--radius-lg);
  padding: 4px 14px;
  font-size: 0.85rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.agy-badge-new {
  background: var(--color-surface-base);
  color: var(--color-text-tertiary);
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: var(--radius-lg);
  letter-spacing: 0.04em;
}

.agy-announcement-text {
  color: var(--color-text-secondary);
  font-weight: 400;
}

.agy-announcement-link {
  color: var(--color-text-primary);
  font-weight: 500;
  text-decoration: none !important;
  margin-left: 0.4rem;
  padding-left: 0.65rem;
  border-left: 1px solid var(--bui-border);
}

.agy-announcement-link:hover {
  text-decoration: underline !important;
}

/* Antigravity Radial Particle Burst Canvas */
.agy-particle-burst-canvas {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 0;
  max-width: 1050px;
  opacity: 0.92;
}

/* Centered Hero Lockup */
.agy-center-lockup {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 1rem 1rem 1.6rem 1rem;
}

.agy-brand-center {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 1.15rem;
  font-weight: 500;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  margin-bottom: 0.75rem;
}

.agy-hero-title-center {
  font-family: var(--font-family-primary);
  font-size: clamp(2.4rem, 4.4vw, 4.2rem);
  font-weight: 500;
  line-height: 1.08;
  letter-spacing: -0.035em;
  color: var(--color-text-primary);
  margin: 0 auto 1rem auto;
  max-width: 820px;
}

.agy-hero-desc-center {
  font-size: 1.08rem;
  color: var(--color-text-secondary);
  line-height: 1.55;
  margin: 0 auto 1.5rem auto;
  max-width: 660px;
}

.agy-hero-desc-center strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

/* Antigravity Pill Buttons */
.stButton > button {
  border-radius: 9999px !important;
  font-family: var(--font-family-primary) !important;
  font-weight: 500 !important;
  font-size: 0.92rem !important;
  padding: 8px 22px !important;
  transition: all 0.15s ease-out !important;
  letter-spacing: -0.01em !important;
  border: 1px solid var(--bui-border) !important;
}

.stButton > button:hover {
  transform: translateY(-1px) !important;
}

/* Dark Primary Pill Action */
.stButton > button[kind="primary"] {
  background: var(--color-surface-base) !important;
  color: #ffffff !important;
  border: 1px solid var(--color-surface-base) !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08) !important;
}

.stButton > button[kind="primary"]:hover {
  background: #1f2937 !important;
  border-color: #1f2937 !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.14) !important;
  color: #ffffff !important;
}

/* Secondary Subtle Action */
.stButton > button[kind="secondary"] {
  background: var(--bui-bg-card) !important;
  color: var(--bui-text-primary) !important;
  border: 1px solid var(--bui-border) !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
}

.stButton > button[kind="secondary"]:hover {
  background: var(--bui-bg-subtle) !important;
  border-color: var(--bui-border-strong) !important;
  color: var(--bui-text-primary) !important;
}

/* Antigravity Capability Spotlight Cards */
.bui-spotlight-card, .agy-spotlight-card {
  background: var(--bui-bg-card);
  border: 1px solid var(--bui-border);
  border-radius: 20px;
  padding: 1.4rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 4px 12px rgba(0, 0, 0, 0.015);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.bui-spotlight-card:hover, .agy-spotlight-card:hover {
  border-color: var(--bui-border-strong);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
}

.bui-card-top-row, .agy-card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
}

.bui-card-role-title, .agy-card-role-title {
  font-size: 0.96rem;
  font-weight: 600;
  color: var(--bui-text-primary);
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.bui-card-badge-gold, .agy-card-badge {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 9999px;
  background: var(--bui-bg-subtle);
  color: var(--bui-text-secondary);
  border: 1px solid var(--bui-border);
}

.bui-card-route, .agy-card-route {
  color: var(--bui-text-secondary);
  font-size: 0.84rem;
  font-weight: 450;
  margin-bottom: 0.85rem;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bui-flight-track, .agy-track {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0.75rem 0 1.1rem 0;
  color: var(--bui-text-tertiary);
  font-size: 0.78rem;
}

.bui-flight-track-dots, .agy-track-dots {
  flex-grow: 1;
  border-bottom: 1.5px dashed var(--bui-border);
  height: 1px;
}

/* Pagination Dots */
.bui-pagination-dots, .agy-pagination-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 1.5rem;
}

.bui-pag-dot, .agy-pag-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: var(--bui-border-strong);
  opacity: 0.5;
  transition: all 0.2s ease;
}

.bui-pag-dot-active, .agy-pag-dot-active {
  background: var(--bui-text-primary);
  opacity: 1;
  width: 18px;
  border-radius: 9999px;
}

/* Universal Cards & Containers */
.bui-card, .agy-card {
  background: var(--bui-bg-card);
  border: 1px solid var(--bui-border);
  border-radius: 20px;
  box-shadow: var(--bui-shadow-card);
  padding: 1.8rem 2rem;
  margin-bottom: 1.5rem;
}

.bui-card-title, .agy-card-title {
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: -0.015em;
  color: var(--bui-text-primary);
  margin-bottom: 0.35rem;
}

/* Section Headings */
.bui-section-title, .agy-section-title {
  font-size: 1.6rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--bui-text-primary);
  margin-bottom: 0.25rem;
}

.bui-section-sub, .agy-section-sub {
  font-size: 0.95rem;
  color: var(--bui-text-secondary);
  line-height: 1.5;
  margin-bottom: 1.4rem;
}

/* Stat Cards (Google Metric Pattern) */
.bui-stat-card, .agy-stat-card {
  background: var(--bui-bg-card);
  border: 1px solid var(--bui-border);
  border-radius: 18px;
  box-shadow: var(--bui-shadow-card);
  overflow: hidden;
}

.bui-stat-body, .agy-stat-body {
  padding: 1.25rem 1.4rem;
}

.bui-stat-header, .agy-stat-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.6rem;
}

.bui-stat-icon-tile, .agy-stat-icon-tile {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}

.bui-icon-blue { background: #e8f0fe; color: #1967d2; }
.bui-icon-purple { background: #f3e8fd; color: #9333ea; }
.bui-icon-emerald { background: #e6f4ea; color: #137333; }
.bui-icon-amber { background: #fef7e0; color: #b06000; }

.bui-kpi-label, .agy-kpi-label {
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--bui-text-tertiary);
  margin: 0;
}

.bui-kpi, .agy-kpi {
  font-size: 1.9rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: var(--bui-text-primary);
  margin: 0;
  line-height: 1.15;
}

.bui-stat-footer, .agy-stat-footer {
  background: var(--bui-bg-subtle);
  border-top: 1px solid var(--bui-separator);
  padding: 0.55rem 1.4rem;
  font-size: 0.78rem;
  color: var(--bui-text-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Antigravity Chips & Badges */
.bui-chip, .agy-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.22rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.3;
}

.bui-chip-success { background: #e6f4ea; color: #137333; border: 1px solid rgba(52, 168, 83, 0.2); }
.bui-chip-warning { background: #fef7e0; color: #b06000; border: 1px solid rgba(251, 188, 4, 0.25); }
.bui-chip-danger  { background: #fce8e6; color: #c5221f; border: 1px solid rgba(234, 67, 53, 0.2); }
.bui-chip-info    { background: #e8f0fe; color: #1967d2; border: 1px solid rgba(66, 133, 244, 0.2); }
.bui-chip-neutral { background: var(--bui-bg-subtle); color: var(--bui-text-secondary); border: 1px solid var(--bui-border); }

/* Evidence Matrix Cards */
.bui-evidence-card, .agy-evidence-card {
  background: var(--bui-bg-card);
  border: 1px solid var(--bui-border);
  border-radius: 14px;
  padding: 1.1rem 1.3rem;
  margin-bottom: 0.85rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.bui-evidence-quote, .agy-evidence-quote {
  border-left: 3px solid #4285f4;
  background: #f8fafc;
  border-radius: 0 8px 8px 0;
  padding: 0.65rem 1rem;
  margin: 0.6rem 0 0.2rem 0;
  font-size: 0.88rem;
  color: var(--bui-text-primary);
  font-style: italic;
  line-height: 1.5;
}

/* DPDP Act 2023 Compliance Callout */
.bui-callout, .agy-callout {
  border: 1px solid var(--bui-border);
  background: var(--bui-bg-subtle);
  border-radius: 16px;
  padding: 1.1rem 1.4rem;
  margin: 1.2rem 0;
  font-size: 0.88rem;
  color: var(--bui-text-secondary);
  line-height: 1.55;
}

.bui-callout-strong, .agy-callout-strong {
  color: var(--bui-text-primary);
  font-weight: 600;
}

/* File Cards */
.bui-file-card, .agy-file-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bui-bg-card);
  border: 1px solid var(--bui-border);
  border-radius: 14px;
  padding: 0.85rem 1.2rem;
  margin-bottom: 0.6rem;
}

.bui-file-info {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.bui-file-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #f1f3f4;
  color: #ea4335;
  font-weight: 700;
  font-size: 0.72rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bui-file-name {
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--bui-text-primary);
}

.bui-file-meta {
  font-size: 0.78rem;
  color: var(--bui-text-tertiary);
}

.bui-empty {
  padding: 2.5rem;
  text-align: center;
  border: 1px dashed var(--bui-border);
  border-radius: 16px;
  color: var(--bui-text-secondary);
  font-size: 0.92rem;
  line-height: 1.5;
  background: var(--bui-bg-subtle);
}

/* Right Sidebar Links (Subtle Google Antigravity Rail) */
.bui-hero-sidebar-socials, .agy-hero-rail {
  position: absolute;
  right: 1.4rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  align-items: center;
  color: var(--bui-text-tertiary);
  font-size: 1rem;
  z-index: 5;
}

.bui-hero-sidebar-socials a, .agy-hero-rail a {
  color: var(--bui-text-tertiary);
  text-decoration: none;
  transition: all 0.15s ease;
}

.bui-hero-sidebar-socials a:hover, .agy-hero-rail a:hover {
  color: var(--bui-text-primary);
  transform: scale(1.1);
}
"""


def get_theme_css(mode: str = "light") -> str:
    """Return <style> block declaring tokens and layout CSS for `mode`."""
    tokens = ANTIGRAVITY_DARK_TOKENS if mode == "dark" else ANTIGRAVITY_LIGHT_TOKENS
    declarations = "\n".join(f"  {k}: {v};" for k, v in tokens.items())
    return f"<style>\n:root {{\n{declarations}\n}}\n{BASE_CSS}\n</style>"
