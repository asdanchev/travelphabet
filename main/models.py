from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from unidecode import unidecode
from ckeditor_uploader.fields import RichTextUploadingField

class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextUploadingField(blank=True, null=True)
    letter = models.CharField(max_length=1)
    category = models.CharField(max_length=100, default='Abu Dhabi')
    category_en = models.CharField(max_length=100, blank=True, verbose_name="Category (EN)")
    category_slug = models.SlugField(max_length=100, blank=True, verbose_name="Category slug")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Additional fields
    location_info = models.TextField(blank=True, verbose_name="Location")
    how_to_get = models.TextField(blank=True, verbose_name="How to get there")
    travel_tips = models.TextField(blank=True, verbose_name="Useful tips")
    location_map_embed = models.TextField(blank=True, verbose_name="Map embed (iframe from Google Maps)")

    def save(self, *args, **kwargs):
        # Auto-generate article slug
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            num = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug

        # Auto-generate category slug
        if self.category_en:
            self.category_slug = slugify(self.category_en.strip())
        elif self.category:
            self.category_slug = slugify(unidecode(self.category.strip()))

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ArticleImage(models.Model):
    ORIENTATION_CHOICES = [
        ('horizontal', 'Horizontal'),
        ('vertical', 'Vertical'),
    ]

    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/')
    orientation = models.CharField(max_length=10, choices=ORIENTATION_CHOICES, blank=True)

    def __str__(self):
        return f"Image for {self.article.title}"