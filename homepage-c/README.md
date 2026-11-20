# Tungal Schools & Colleges · Homepage Option C "Nightfall"

A dark, editorial homepage. Static HTML, CSS and vanilla JS (GSAP + ScrollTrigger self-hosted). No build step.

Open `index.html` through any static server (for example `python3 -m http.server`). The admissions form posts to `forms/admission-enquiry.php`.

## What is different from Options A and B
- Palette: ink, iris, coral, marigold. Type: Manrope + Instrument Serif italic.
- All imagery is new, generated artwork (`assets/art/*.webp`, made by `gen_art_c.py`). No photographs, no people, none of the earlier photos.
- Interactions: live aurora hero, 3-slide hero with pause, two-row velocity marquee, "Find your fit" campus finder, programme explorer, expanding campus panels, draggable student-life strip, counters, spotlight cards, custom cursor (fine pointers only), in-form progress.

## Content rules kept
Every fact comes from the brief or tungalschools.com (About, Contact, Results). Programme-to-campus mapping is in `assets/js/site-data.js` and in the finder. Hostels are shown for PUC at Hulyal, Bagalkot and Vijayapura only.

## Before going live
1. Set the admissions inbox in `forms/admission-enquiry.php` (`$to`).
2. The Voices section has no testimonials yet. Add real ones, with permission.
3. Student-life cards are illustrations. Replace `assets/art/life-*.webp` with campus photographs when ready.
4. Hulyal has no listed phone number.
5. Confirm "25 years" against the About page's 2003 founding date, and the Jamkhandi school range (brief says Std V, Contact page says Std 10).
6. Student names in Wall of Fame come from published result posters; confirm consent.
7. Kannada ತುಂಗಳ in the logo should be checked by a Kannada reader before print.

## Accessibility and motion
Skip link, ARIA tabs and expanding panels, focus-trapped menu, 44px targets, visible focus. With `prefers-reduced-motion`, autoplay, marquee, cursor, reveals and count-ups are off.
