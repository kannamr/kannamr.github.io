# AI Infrastructure / Platform Engineering Portfolio

A responsive, static personal portfolio with a premium dark theme and subtle blue accents. It can be hosted on GitHub Pages, Netlify, Vercel, or any static web host.

## Preview locally
Open `index.html` in a browser. For a local server, run:
```bash
python3 -m http.server 8000
```
Then visit `http://localhost:8000`.

## Before publishing — personalize these placeholders
Search the project for `YOUR_` and replace:
- `YOUR NAME` / `Your Name`: your preferred professional name
- `YOUR_GITHUB`: your GitHub username
- `YOUR_LINKEDIN`: your LinkedIn profile slug
- `YOUR_EMAIL@example.com`: professional contact email
- `Employer name`, `Location`, and `DATES OF EMPLOYMENT`: accurate work-history details

## Add your résumé
Place your PDF résumé at `assets/resume.pdf`. The current link points to that location. Do not publish until the file is present and up to date.

## Project and blog integrity
The three project cards and article cards are starter briefs / ideas, not claims that the projects or posts already exist. Replace repository links with real public repositories and link only to articles you have actually written. Remove or rewrite any item that does not accurately represent your work.

For each completed project, add:
1. The problem and intended users
2. Architecture diagram and key components
3. Setup / deployment steps and source code
4. Engineering trade-offs and security considerations
5. Tests, observed metrics, and lessons learned (only real measurements)

## Deploy with GitHub Pages
1. Create a repository, for example `portfolio`.
2. Add the contents of this folder to the repository root.
3. Replace the placeholders and add `assets/resume.pdf`.
4. In GitHub, open **Settings → Pages**, select **Deploy from a branch**, choose `main` and `/ (root)`, then save.
5. Add a custom domain in Pages settings if desired and configure the DNS records shown by GitHub.

## Suggested next improvements
- Add actual role-by-role experience entries and defensible impact metrics.
- Add project case-study pages as the repositories mature.
- Replace article ideas with published technical notes.
- Add a favicon and custom domain.
- Consider removing the external Google Fonts import if you prefer a fully self-hosted page.
