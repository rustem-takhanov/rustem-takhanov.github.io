# Rustem Takhanov — academic website

A custom, dependency-free static site inspired by the AcademicPages layout. The top navigation is Publications, Talks, Teaching, Miscellaneous, and Links, in that order. The name returns to the home page.

## Editing

- `content/publications.json`: all 29 publications, short descriptions, authors, topics, resource links, and optional media.
- `content/talks.json`: additional talks, conference links, and video recordings.
- `content/teaching.json`: the lecture archive from the original website.
- `content/lecture_videos.json`: COVID-era lecture recordings, grouped by topic, with Russian-language recordings identified.
- `content/press.json`: the In Press list, with original headlines, publishers, dates, and article links.
- `content/site.json`: the intended GitHub Pages URL used in the downloadable package's canonical links and sitemap.
- `build.py`: page templates, profile information, and general page content.
- `illustrations/`: original SVG research diagrams, captions, and source links for all 29 paper pages. Generated figures are written to `dist/assets/papers/` during the build; no extra dependencies are required.
- `illustrations/kissing.py` and `illustrations/kissing_svg/`: the figure plates of the four kissing-number papers (captions, ledgers, notes and pre-generated SVG files). The SVG files are produced by `tools/kissing_figures/` (NumPy and fontTools needed there only); see its README.
- `assets/style.css`: typography, color, spacing, and responsive layout.
- `assets/site.js`: publication filters, citation copying, opt-in media previews, and the interactive 24-cell.

Each build replaces the generated `dist/` directory to exclude obsolete pages,
figures, and temporary preview files. Make edits in the source directories above.
All text reads and writes use UTF-8 explicitly. The package contains 36 research
SVGs: 11 figures across four kissing-number pages and one on each of the other 25 pages.

Run `python3 build.py`. The output is in `dist/`. It includes a portable GitHub Pages download in `dist/downloads/`.

Publication pages are real static HTML and work without JavaScript. JavaScript progressively adds search and filters, citation copying, and multimedia. All internal paths are relative, supporting both GitHub user sites and project sites. There are no analytics, cookies, external fonts, frameworks, or runtime dependencies. YouTube and Google Drive embeds load only when the visitor opens them.

## GitHub Pages

Extract `dist/downloads/rustem-takhanov-github-pages.zip` and upload its contents to the root of the intended repository. Set Settings → Pages → Deploy from a branch → main → /(root). Preserve `.nojekyll`. The package is configured for `https://rustem-takhanov.github.io/`; change `content/site.json` before exporting for a different public URL. The archive includes canonical URLs, a sitemap, and robots.txt; the private Sites preview remains unchanged. No GitHub repository was created or modified. See `GITHUB_PAGES.md` for the publishing and indexing steps.

The download includes editable source in `_source/`. Running its build script creates `_source/dist/downloads/rustem-takhanov-github-pages.zip`; extract and upload that new package to publish an update with refreshed sitemap and canonical URLs.

## Preview and hosting

The private Sites preview uses `dist/`. The tracked `.openai/hosting.json` preserves the preview project identity. Source is maintained in this project's Git repository.

## Extending multimedia

Add a `video` field with a YouTube video ID, a `poster` field with a Google Drive file ID, or resources labeled Slides, Poster, or Code. The quaternionic paper uses `interactive: "24cell"`. Add custom figures to `assets/` and extend the relevant page template as needed.
