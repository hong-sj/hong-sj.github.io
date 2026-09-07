---
layout: page
permalink: /publications/
title: publications
description: Journal articles in biomedical statistics, clinical data science, machine learning, and digital health.
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

{% if site.data.citations.metadata.total_citations %}
{% assign stats = site.data.citations.metadata %}

  <div class="scholar-stats d-flex flex-wrap align-items-center" style="gap: 0.5rem 1rem; margin: 1rem 0; font-size: 0.9rem;">
    <a href="https://scholar.google.com/citations?user={{ site.data.socials.scholar_userid }}" target="_blank" rel="noopener" aria-label="Google Scholar profile">
      <img src="https://img.shields.io/badge/citations-{{ stats.total_citations }}-4285F4?logo=googlescholar&labelColor=beige" alt="Total citations: {{ stats.total_citations }}">
    </a>
    <span class="text-muted">h-index {{ stats.h_index }} &middot; i10-index {{ stats.i10_index }}{% if stats.last_updated %} &middot; Updated {{ stats.last_updated }}{% endif %}</span>
  </div>
{% endif %}

<p class="text-muted" style="font-size: 0.9rem;"><sup>†</sup> First (or co-first) author &nbsp;·&nbsp; <sup>*</sup> Corresponding author</p>

<h2 id="journal-articles">Journal Articles</h2>

<div class="publications">

{% bibliography --query @article %}

</div>
