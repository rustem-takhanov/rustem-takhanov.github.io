# Rustem Takhanov — GitHub Pages publishing guide

This folder contains the preliminary academic website: 29 publications, Talks
(including AIST 2026), Links, the teaching archive, all local images and assets (including 29 original research illustrations),
and editable source in `_source/`. The site is already built; no installation
or build command is needed to publish it. Linked papers, videos, and other
external resources remain hosted by their original providers.

The package is configured for **https://rustem-takhanov.github.io/** and includes canonical
URLs for all 34 HTML pages, page descriptions, `sitemap.xml`, and `robots.txt`.

## If the site is currently at /takhanov/

Open the `takhanov` repository owned by `rustem-takhanov`, then go to
**Settings → General**. Change **Repository name** to
**rustem-takhanov.github.io** and click **Rename**. Upload the contents of this
updated package to the renamed repository and commit to main. Under
**Settings → Pages**, confirm **Deploy from a branch → main → /(root)**.
The site should publish at **https://rustem-takhanov.github.io/** after the
Pages deployment finishes. Renaming the repository preserves its files.

## Publish using the GitHub website

1. Sign in to GitHub and create a repository with **rustem-takhanov** as its
   owner (your account or organization). Name the repository exactly
   **rustem-takhanov.github.io**. Choose **Public**, enable **Add README**, and create it.
   If that repository already exists, use the existing repository and preserve
   any files or settings you still need.
2. Extract the downloaded ZIP on your computer.
3. In the repository, choose **Add file → Upload files**. Open the extracted
   folder and drag **its contents** into the upload area. Include the folders
   `assets`, `publications`, `talks`, `links`, `teaching`, and `_source`, and the
   files `index.html`, `sitemap.xml`, `robots.txt`, `README.md`, and `.nojekyll`.
   The root `index.html` must appear at the top level of the repository.
   Do not upload the ZIP itself or put everything inside an extra outer folder.
4. Use the commit message **Publish preliminary academic website** and commit
   directly to **main**. If you chose a new branch, merge its pull request into
   main before continuing.
5. Check that `.nojekyll` appears in the repository. If the upload omitted it,
   choose **Add file → Create new file**, name it `.nojekyll`, enter a blank
   line, and commit it. This tells GitHub to serve the already-built HTML.
6. Open **Settings → Pages**. Under **Build and deployment**, choose
   **Deploy from a branch**, select **main** and **/(root)**, then **Save**.
   Enable **Enforce HTTPS** if the option is available and not already enabled.
7. Allow up to ten minutes, then open **https://rustem-takhanov.github.io/** in a private
   browser window to confirm that visitors can see it without signing in.
   Also check `/publications/`, `/talks/`, and `/sitemap.xml`.
   If publishing fails, inspect the repository's **Actions** tab for the
   Pages deployment status and error message.

## Help Google discover the website

1. Open https://search.google.com/search-console/ and add a **URL-prefix**
   property for **https://rustem-takhanov.github.io/**.
2. Choose **HTML file** verification. Download the file Google supplies, upload
   it unchanged to the repository root alongside `index.html`, and commit it.
   After GitHub publishes the file, click **Verify** in Search Console. Keep
   that file in the repository during future updates.
3. In Search Console's **Sitemaps** report, submit **sitemap.xml**.
4. Use **URL Inspection** for **https://rustem-takhanov.github.io/** and select
   **Request indexing**. You can also request indexing for the Publications page.
5. Add a link to the new website on your existing Google Site and update the
   website link on your GitHub and Google Scholar profiles when ready.

Publishing makes the site publicly accessible and eligible for indexing.
Search results are not immediate: Google says crawling can take days to weeks,
and submitting a sitemap or requesting indexing does not guarantee inclusion.

## Continue editing after publication

You can keep refining the site at the same address. Updated files committed to
the selected publishing branch are published automatically.

The editable JSON, templates, styles, and scripts are in `_source/`. To rebuild
locally with Python 3.9 or newer, run this from the extracted folder:

```bash
python _source/build.py
```

On Windows, `py _source/build.py` is an alternative. The script creates an
updated publishing package at
`_source/dist/downloads/rustem-takhanov-github-pages.zip`. Extract that package
and upload its contents to the repository root. Use this generated ZIP so
the sitemap and canonical URLs are included. Preserve any Google verification
file already uploaded to the repository.

If you choose a different GitHub username, a project subpath, or a custom
domain, first change `github_pages_url` in `_source/content/site.json` to the
full intended website address, including its trailing slash, then rebuild.
Internal links are relative and support either a user site or project subpath.

## Official instructions

- GitHub Pages quickstart: https://docs.github.com/en/pages/quickstart
- Uploading files: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
- Choosing the publishing source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- Static HTML and `.nojekyll`: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- Search Console ownership verification: https://support.google.com/webmasters/answer/9008080
- Sitemaps: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Requesting indexing: https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
