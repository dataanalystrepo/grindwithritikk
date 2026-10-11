# Grind With Ritik

Static website for the Instagram channel @grindwithritikk: notes, articles, job links and resources for Data Analytics.

## Files
- `index.html` - the whole website (no build step)
- `posts.json` - all your content. Edit this file to add or remove posts.

## Host it free on GitHub Pages
1. Create a new GitHub repository and upload `index.html`, `posts.json` and this README.
2. Repo Settings > Pages > Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
3. Your site goes live at `https://<your-username>.github.io/<repo-name>/` in a minute or two.

## Add a post every day (works from your phone)
Open `posts.json` on github.com, tap the pencil icon, add a new object at the TOP of the `posts` list, and commit. The site updates in about a minute.

```json
{
  "id": "unique-id-1",
  "type": "job",
  "title": "Data Analyst",
  "company": "Company name",
  "loc": "Bengaluru",
  "level": "Fresher",
  "desc": "Short description",
  "url": "https://apply-link.com",
  "date": "2026-10-12"
}
```
- `type` is one of: `note`, `article`, `job`, `resource`.
- `company`, `loc`, `level` ("Fresher" or "Experienced") are only for jobs.
- `url` is optional and must start with `https://`.
- Keep a comma between posts and make sure every `id` is unique.

## Test on your computer
Browsers block `posts.json` when opening the file directly. Run `python3 -m http.server` in this folder and open http://localhost:8000.

## Contact form
It opens the visitor's email app addressed to the email set in `const MAIL` inside `index.html`. For messages saved to an inbox automatically, connect a form service such as Formspree.
