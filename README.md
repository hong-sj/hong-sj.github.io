# Sungjun Hong — Personal Homepage

Source for [hong-sj.github.io](https://hong-sj.github.io), an academic and professional homepage.

The site uses the design and structure of [Jovinus/Jovinus.github.io](https://github.com/Jovinus/Jovinus.github.io), built on the [al-folio](https://github.com/alshedivat/al-folio) Jekyll theme.

## Local development

```bash
docker compose pull && docker compose up
```

The local site is served at `http://localhost:8080`.

## Deployment

Pushes to `main` trigger a GitHub Pages build. The live URL is configured in `_config.yml`.

## Main content

- `_pages/` — About, publications, projects, teaching, CV, and news pages
- `_projects/` — Research project entries
- `_bibliography/papers.bib` — Publications
- `_data/cv.yml` — CV content
- `_data/citations.yml` — Google Scholar citation data
- `_news/` — Homepage announcements

## License

Site content © Sungjun Hong. The underlying al-folio theme is MIT-licensed.
