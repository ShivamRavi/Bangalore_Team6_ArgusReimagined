---
name: Argus Celestial
colors:
  surface: '#f7f9fe'
  surface-dim: '#d7dadf'
  surface-bright: '#f7f9fe'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f4f9'
  surface-container: '#ebeef3'
  surface-container-high: '#e5e8ed'
  surface-container-highest: '#dfe3e8'
  on-surface: '#181c20'
  on-surface-variant: '#494550'
  inverse-surface: '#2d3135'
  inverse-on-surface: '#eef1f6'
  outline: '#7a7581'
  outline-variant: '#cac4d1'
  surface-tint: '#66529c'
  primary: '#2c155f'
  on-primary: '#ffffff'
  primary-container: '#422e76'
  on-primary-container: '#af99e9'
  inverse-primary: '#cfbdff'
  secondary: '#4f54b4'
  on-secondary: '#ffffff'
  secondary-container: '#949aff'
  on-secondary-container: '#282c8c'
  tertiary: '#461700'
  on-tertiary: '#ffffff'
  tertiary-container: '#692700'
  on-tertiary-container: '#ee8d5e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#cfbdff'
  on-primary-fixed: '#210755'
  on-primary-fixed-variant: '#4e3a82'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#bfc1ff'
  on-secondary-fixed: '#03006d'
  on-secondary-fixed-variant: '#363b9a'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#783109'
  background: '#f7f9fe'
  on-background: '#181c20'
  surface-variant: '#dfe3e8'
  mars-red: '#EF5350'
  venus-sulfur: '#FFF176'
  exp-gold: '#F9A825'
  streak-flame: '#FF5722'
  jupiter-tan: '#BCAAA4'
  neptune-indigo: '#3F51B5'
  surface-white: '#FFFFFF'
typography:
  headline-lg:
    fontFamily: Nunito Sans
    fontSize: 32px
    fontWeight: '900'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: Nunito Sans
    fontSize: 24px
    fontWeight: '900'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Nunito Sans
    fontSize: 20px
    fontWeight: '800'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Nunito Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Nunito Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.6'
  stat-exp:
    fontFamily: Nunito Sans
    fontSize: 18px
    fontWeight: '900'
    lineHeight: '1.0'
  label-caps:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '800'
    lineHeight: '1.0'
    letterSpacing: 0.08em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  gutter: 16px
  margin-sm: 12px
  margin-md: 24px
  margin-lg: 40px
  container-padding: 24px
---

## Brand & Style

Argus Celestial is an educational platform designed for a youthful, student-centric audience. The brand personality is encouraging, gamified, and vibrant, balancing academic rigor with an adventurous "space exploration" metaphor. 

The visual style is a sophisticated **Modern-Glassmorphic** hybrid. It utilizes clean, systematic layouts (Modern) combined with soft, translucent layers and backdrop blurs (Glassmorphism) to create a sense of depth and focus. The interface uses high-contrast typography and a rich, multi-hue palette to denote different subjects and achievements, ensuring the experience feels more like a rewarding journey than a standard utility.

## Colors

The palette is anchored by deep indigos and purples for high-level navigation and identity, contrasted with a functional range of subject-specific colors. 

- **Primary & Secondary:** Used for branding, active states, and primary navigational elements.
- **Tertiary:** Specifically reserved for "Open Content" actions and high-priority learning interactions.
- **Semantic & Gamified Colors:** `mars-red` is used for progress warnings or critical alerts; `exp-gold` and `streak-flame` are used exclusively for achievements, streaks, and reward systems.
- **Backgrounds:** A soft `neutral` background (#f7f9fe) provides the canvas for `surface-white` cards and containers, ensuring maximum legibility.

## Typography

Typography is a primary driver of the gamified hierarchy. 

- **Nunito Sans** serves as the workhorse for both headlines and body text. A "Heavy" (900) weight is used for primary headers and achievement stats to evoke a bold, comic-book-adjacent energy.
- **Hanken Grotesk** is used for "Label Caps"—tiny, all-caps metadata and category tags. This sharp, contemporary sans provides a technical contrast to the rounded, friendly nature of Nunito.
- **Hierarchy:** High-priority numeric values (like streaks or EXP) use the `stat-exp` style for immediate visual impact.

## Layout & Spacing

The system uses a **Fluid Grid** with a maximum content width of 1440px. 

- **Desktop:** 12-column grid with a fixed 256px (w-64) sidebar.
- **Rhythm:** Spacing follows an 8px base unit. Section-level gaps are typically 40px (margin-lg), while internal card components use 24px (margin-md) for breathing room.
- **Mobile Adaptation:** Sidebars collapse into a drawer. Horizontal padding reduces from 32px to 16px. Subject cards reflow to a single column stack.

## Elevation & Depth

Hierarchy is established through a combination of **Tonal Layering** and **Glassmorphism**.

- **Level 0 (Background):** Solid neutral wash (#f7f9fe).
- **Level 1 (Cards/Containers):** Solid white surfaces with a 1px `outline-variant` (#dfe3e8) border and a `shadow-sm`.
- **Level 2 (Overlays/App Bars):** Semi-transparent white (rgba 255, 255, 255, 0.7 or 0.8) with a 10px backdrop blur (glass-effect). This is used for the sticky Top Bar and Floating AI buttons.
- **Interaction Depth:** Active buttons use `active:scale-95` to provide tactile feedback without requiring heavy shadows.

## Shapes

The shape language is consistently **Rounded**, reinforcing the friendly and approachable brand.

- **Standard Containers:** Cards use 24px (rounded-3xl) to feel soft and modern.
- **Interactive Elements:** Buttons and Input fields use 12px (rounded-xl) or 16px (rounded-2xl).
- **Meta-tags/Pills:** Subject labels and status chips use the "Full" pill shape for distinct categorization.
- **Iconography:** Symbols are enclosed in rounded-xl containers with a 10% opacity tint of the icon color.

## Components

- **Buttons:** 
  - *Primary:* Solid tertiary color, heavy font weight, rounded-xl.
  - *Secondary:* 2px border in secondary color, transparent background, secondary text.
  - *Small/Action:* Pill-shaped with bold caps text.
- **Cards:** 24px corner radius, thin grey border, subtle shadow. Internal padding should be 20px. Includes a progress bar at the bottom for "Learning Journey" types.
- **Inputs:** Search and chat inputs are pill-shaped, using a `surface-container-low` background and a subtle border. Icons are placed inside the container at the leading edge.
- **Progress Bars:** 8px height, fully rounded tracks with high-contrast fills (e.g., Primary or Mars Red).
- **Chips (Pills):** Used for subject categories. They should have a 10% opacity background of the text color to ensure "color-coding" without overwhelming the layout.
- **Floating AI Assistant:** A distinctive, glassmorphic circular button always present in the bottom-right corner, triggering a right-side drawer.