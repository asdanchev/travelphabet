from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.filter
def first_image(html):
    """Извлекает путь к первому <img> из HTML-содержимого."""
    soup = BeautifulSoup(html, 'html.parser')
    img = soup.find('img')
    if img and img.get('src'):
        return img['src']
    return None

@register.filter
def strip_tags_except_img(html):
    """Удаляет все теги, кроме <img> и текстового содержимого."""
    soup = BeautifulSoup(html, 'html.parser')

    # Удаляем все теги, кроме <img>
    for tag in soup.find_all():
        if tag.name != 'img':
            tag.unwrap()

    return str(soup)
