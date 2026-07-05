# Product Requirements Document: Argus LMS

## 1. Project Overview
**Product Name:** Argus LMS (Argus Celestial)
**Vision:** A gamified, student-centric Learning Management System that transforms academic rigor into an adventurous "space exploration" journey.
**Target Audience:** Students, Staff, and Parents within the Lighthouse Learning ecosystem.

---

## 2. Brand Identity & Visual Language (Argus Celestial)
The platform follows the **Argus Celestial** design system, characterized by a "Modern-Glassmorphic" hybrid aesthetic.

### 2.1 Core Principles
- **Luminous Engine:** The interface should feel powered by light and energy, using vibrant gradients and glass-like surfaces.
- **Academic Adventure:** Using space exploration metaphors (e.g., "Welcome back, Explorer," "Learning Journey," "Mission Control") to drive engagement.
- **Tactile Feedback:** Subtle scaling effects and soft transitions rather than heavy drop shadows.

### 2.2 Design Tokens
- **Primary Palette:** Deep Indigos (#2c155f) and Purples for identity; Subject-specific colors for categorization.
- **Typography:** 
    - **Nunito Sans:** Primary typeface for headings (Heavy 900) and body text.
    - **Hanken Grotesk:** Technical metadata and category labels (Caps 800).
- **Shapes:** Consistently rounded (24px for cards, 12-16px for buttons) to maintain a friendly, approachable feel.
- **Elevation:** Level 1 cards (White, solid) vs. Level 2 overlays (Glassmorphic, semi-transparent with 10px backdrop blur).

---

## 3. User Flows & Key Screens

### 3.1 Authentication (The Front Door)
- **Login Experience:** A balanced split-screen layout.
    - **Left:** High-contrast, clean functional form with role selection (Student/Staff/Parent) and OTP support.
    - **Right:** A refined, "whiter" illustrative brand panel featuring cosmic/educational vector artwork.
- **Mobile Access Wall:** A dedicated interstitial for mobile web users, directing them to the native app via a centered, glassmorphic pop-in dialog.

### 3.2 Main Dashboard (Mission Control)
- **Learning Journey:** A prioritized list of active courses/lessons with integrated progress tracking.
- **Quiz Center:** Access to timed math challenges and science trivia.
- **Newton AI Integration:** A persistent, glassmorphic floating assistant for instant academic help.
- **Synchronized Navigation:** A fixed 256px sidebar (desktop) that provides global access to Courses, Curriculum, Performance, and Fees.

### 3.3 Learning Content
- **Course Search:** A robust search interface with multi-category filters (History, Science, etc.) and AI-generated "Digest" flashcards.
- **Argus Podcasts:** Audio-based lessons with live synchronized transcripts and interactive waveform visualizations.

### 3.4 Error States
- **404 Page:** A thematic "Lost in Space" screen featuring an astronaut search illustration, maintaining brand tone even during failure.

---

## 4. Technical Requirements
- **Responsive Layout:** 12-column fluid grid for desktop (max 1440px) scaling down to portrait mobile stacks.
- **Performance:** CSS-based animations for "Liquid Glass" effects and GPU-accelerated backdrop blurs.
- **Localization:** Support for multi-role terminology and potential regional language adaptations.

---

## 5. Success Metrics
- **Engagement:** Increased quiz completion rates via gamified "EXP" and "Streaks."
- **Accessibility:** High-contrast ratios for all functional text components (Lighthouse Learning standards).
- **Usability:** Reduced time-to-task for lesson access via the "Learning Journey" dashboard component.
