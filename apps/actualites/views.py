from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Article, Category
from .forms import CommentForm

# Vue Liste (Déjà existante, on ne change rien sauf l'import)
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

# NOUVEAU : Vue Détail + Commentaires
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = article.comments.all()
    
    # Vérifier si l'utilisateur a déjà liké
    is_liked = False
    if request.user.is_authenticated:
        if article.likes.filter(id=request.user.id).exists():
            is_liked = True

    # Gestion du formulaire de commentaire
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login') # Redirige si pas connecté
            
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect('actualites:detail', slug=slug)
    else:
        form = CommentForm()

    context = {
        'article': article,
        'comments': comments,
        'form': form,
        'is_liked': is_liked,
        'total_likes': article.total_likes()
    }
    return render(request, 'actualites/detail.html', context)

# NOUVEAU : Fonction Like
@login_required
def like_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.likes.filter(id=request.user.id).exists():
        article.likes.remove(request.user)
    else:
        article.likes.add(request.user)
    return redirect('actualites:detail', slug=slug)