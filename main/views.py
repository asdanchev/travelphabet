from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, TemplateDoesNotExist
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator

import os
from PIL import Image, ExifTags
from bs4 import BeautifulSoup
from unidecode import unidecode

from .models import Article, ArticleImage
from .forms import ArticleForm

# Alphabet and categories
LETTERS = "abcdefghijklmnopqrstuvwxyz"

CATEGORY_SLUG_MAP = {
    'abudhabi': 'Abu Dhabi',
    'dubai': 'Dubai',
    'istanbul': 'Istanbul',
    'almaty': 'Almaty',
    'burabay': 'Burabay',
    # Add more as needed
}
REVERSE_CATEGORY_SLUG_MAP = {v.lower(): k for k, v in CATEGORY_SLUG_MAP.items()}

# Home page
def index(request):
    letter = 'a'
    articles = Article.objects.filter(letter=letter).order_by('-created_at')
    category_name = "Abu Dhabi"

    return render(request, 'main/index.html', {
        'letter': letter.upper(),
        'articles': articles,
        'category': category_name,
    })

# Letter-based archive
def letter_view(request, letter):
    letter = letter.lower()
    if letter not in LETTERS:
        raise Http404("Invalid letter.")

    index = LETTERS.index(letter) + 1
    template_name = f"main/letter_{index}.html"

    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        raise Http404("Template for this letter not found.")

    articles = Article.objects.filter(letter=letter)
    category_name = "Abu Dhabi" if letter == 'a' else f"Travel destinations starting with “{letter.upper()}”"

    return render(request, template_name, {
        'letter': letter.upper(),
        'articles': articles,
        'category': category_name,
    })

# Article detail view
def article_detail(request, letter, slug):
    article = get_object_or_404(Article, letter=letter.lower(), slug=slug)

    if article.category and article.category.strip():
        other_articles = Article.objects.filter(
            category=article.category.strip()
        ).exclude(id=article.id).order_by('?')[:5]
        category_key = article.category.strip().lower()
        category_slug = REVERSE_CATEGORY_SLUG_MAP.get(category_key)
        category_url = reverse('articles_by_category', kwargs={'category': category_slug}) if category_slug else None
    else:
        other_articles = []
        category_slug = None
        category_url = None

    paragraphs = [p.strip() for p in article.content.split('\n') if p.strip()]
    images = list(article.images.all())

    blocks = []
    for i, paragraph in enumerate(paragraphs):
        blocks.append({'type': 'paragraph', 'content': paragraph})
        if i < len(images):
            blocks.append({'type': 'image', 'content': images[i]})
    blocks.extend({'type': 'image', 'content': img} for img in images[len(paragraphs):])

    return render(request, 'main/article_detail.html', {
        'article': article,
        'other_articles': other_articles,
        'category_slug': category_slug,
        'category_url': category_url,
        'blocks': blocks,
    })

# Category articles view
def articles_by_category(request, category):
    category_name = CATEGORY_SLUG_MAP.get(category.lower())
    if not category_name:
        raise Http404("Category not found.")

    articles = Article.objects.filter(category=category_name)

    for article in articles:
        soup = BeautifulSoup(article.content, 'html.parser')
        img_tag = soup.find('img')

        if img_tag and 'src' in img_tag.attrs:
            src = img_tag['src']
            relative_path = src.replace(settings.MEDIA_URL, '').lstrip('/')
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            if os.path.exists(full_path):
                article.preview_image = src
            else:
                article.preview_image = None
        else:
            article.preview_image = None

    return render(request, 'main/articles_by_category.html', {
        'category': category_name,
        'articles': articles,
    })

# Admin dashboard
@login_required
def dashboard(request):
    articles = Article.objects.filter(author=request.user)
    return render(request, 'main/dashboard.html', {'articles': articles})

# Create new article
@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()

            for uploaded_file in request.FILES.getlist('images'):
                process_and_save_image(uploaded_file, article)

            return redirect('dashboard')
    else:
        form = ArticleForm()
    return render(request, 'main/create_article.html', {'form': form})

# Edit article
@login_required
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()

            for uploaded_file in request.FILES.getlist('images'):
                process_and_save_image(uploaded_file, article)

            return redirect('dashboard')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'main/edit_article.html', {'form': form})

# Delete article
@login_required
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        article.delete()
        return redirect('dashboard')
    return render(request, 'main/delete_article_confirm.html', {'article': article})

# 🔧 Image processing
def process_and_save_image(uploaded_file, article):
    img = Image.open(uploaded_file)

    try:
        exif = img._getexif()
        if exif:
            orientation = exif.get(274)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass

    img.thumbnail((1200, 1200))
    width, height = img.size
    orientation = 'vertical' if height > width else 'horizontal'

    image_folder = os.path.join(settings.MEDIA_ROOT, 'article_images')
    os.makedirs(image_folder, exist_ok=True)
    image_path = os.path.join('article_images', uploaded_file.name)
    full_path = os.path.join(settings.MEDIA_ROOT, image_path)

    img.save(full_path, optimize=True, quality=70)

    ArticleImage.objects.create(
        article=article,
        image=image_path,
        orientation=orientation
    )

    # Static pages
def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

# All articles list (with pagination)
def article_list(request):
    qs = Article.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/article_list.html', {'page_obj': page_obj})