from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Article, Category

def list_articles(request, category_slug=None):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    cat = None
    if category_slug:
        cat = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=cat)
    
    paginator = Paginator(articles, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'actualites/list.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'current_cat': cat
    })