KORUM-OS — Temporary Full-Screen Splash

What I changed:
- Replaced `index.html` with a minimal full-screen splash page that displays the existing PNG asset:
  - `assets/77ae7210-59a6-4a03-bbc2-aa3ec7f8c745.png`
- This is a temporary change per request to show the provided logo as the whole page.

Files affected:
- index.html  (replaced with a full-screen splash)

Why:
- You asked to use the long-named PNG as the entire page for tonight.

How to revert:
- If you want to restore the interactive version, replace `index.html` with the previous content (the interactive demo uses `styles.css` and `script.js`).
- A quick way to restore is to checkout the file from version control or copy the previous `index.html` backup if available.

Next recommended steps:
- Commit these changes to your Git branch once you confirm the splash looks correct:

  git add index.html
  git commit -m "Temporary: full-screen splash with provided logo"

- Later, we should replace the placeholder SVG assets with cleaned SVG/wor dmark files and add raster fallbacks (PNG/WebP) for production.

Preview locally:
- Start a local server in the `KORUM-OS` folder and open http://localhost:8000

If you want, I can:
- Restore the previous interactive `index.html` (I still have the interactive content in the workspace history), or
- Create raster fallbacks and a favicon from the provided high-res image.

Good night — ping me when you want to continue.
