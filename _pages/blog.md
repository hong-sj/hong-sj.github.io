---
layout: page
permalink: /blog/
title: blog
nav: true
nav_order: 6
---

<div class="header-bar">
  <h1>{{ site.blog_name }}</h1>
  <h2>{{ site.blog_description }}</h2>
</div>

{% if site.posts.size > 0 %}
  <ul class="post-list">
    {% for post in site.posts %}
      <li>
        <h3>
          <a class="post-title" href="{{ post.url | relative_url }}">
            {{ post.title }}
          </a>
        </h3>
        <p>{{ post.description }}</p>
        <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
      </li>
    {% endfor %}
  </ul>
{% else %}
  <p><em>No posts yet.</em></p>
{% endif %}