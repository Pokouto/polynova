from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg

from apps.profiles.models import TutorProfile
from apps.education.models import Subject, Level
from apps.core.models import City
from apps.billing.models import ContactUnlock
from .models import CourseRequest, Review
from .forms import RequestForm, ReviewForm

def tutor_list(request):
    """
    Affiche l'annuaire des professeurs avec filtres (Matière, Niveau, Ville).
    """
    # On ne prend QUE les profs validés
    tutors = TutorProfile.objects.filter(status='validated')

    # Récupération des filtres depuis l'URL
    subject_id = request.GET.get('subject')
    city_id = request.GET.get('city')
    level_id = request.GET.get('level')

    if subject_id:
        tutors = tutors.filter(subjects__id=subject_id)
    
    if level_id:
        tutors = tutors.filter(levels__id=level_id)
        
    # Note: Si on avait lié la ville au profil pour le filtre, on l'ajouterait ici
    # if city_id: tutors = tutors.filter(city_id=city_id)

    # Listes pour les menus déroulants
    subjects = Subject.objects.all()
    levels = Level.objects.all()
    cities = City.objects.all()

    context = {
        'tutors': tutors.distinct(),
        'subjects': subjects,
        'levels': levels,
        'cities': cities,
    }
    return render(request, 'marketplace/tutor_list.html', context)


def tutor_detail(request, pk):
    """
    Affiche le profil public complet d'un prof.
    Gère :
    1. Le Paywall (Contact masqué/affiché)
    2. L'affichage des avis
    3. Le formulaire de dépôt d'avis (si contact débloqué)
    """
    tutor = get_object_or_404(TutorProfile, pk=pk, status='validated')
    
    # --- 1. Gestion du Paywall ---
    is_unlocked = False
    if request.user.is_authenticated:
        if request.user == tutor.user:
            is_unlocked = True
        elif request.user.is_superuser:
            is_unlocked = True
        elif ContactUnlock.objects.filter(parent_user=request.user, tutor_profile=tutor).exists():
            is_unlocked = True

    # --- 2. Gestion des Avis (Affichage) ---
    reviews = tutor.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # --- 3. Gestion du Formulaire d'Avis (Ajout) ---
    review_form = None
    
    # Un parent ne peut noter que s'il est connecté ET a débloqué le contact
    if request.user.is_authenticated and request.user.role == 'parent' and is_unlocked:
        if request.method == 'POST' and 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.tutor = tutor
                review.author = request.user
                review.save()
                messages.success(request, "Votre avis a été publié avec succès !")
                return redirect('tutor_detail', pk=pk)
        else:
            review_form = ReviewForm()

    context = {
        'tutor': tutor,
        'is_unlocked': is_unlocked,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1), # Arrondi à 1 décimale (ex: 4.5)
        'review_count': reviews.count(),
        'review_form': review_form,
    }
    return render(request, 'marketplace/tutor_detail.html', context)


@login_required
def create_request(request):
    """
    Permet à un parent de poster une nouvelle demande de cours.
    """
    # Sécurité : Seuls les parents (ou admin) peuvent poster
    is_parent = hasattr(request.user, 'role') and request.user.role == 'parent'
    is_admin = request.user.is_superuser

    if not is_parent and not is_admin:
        messages.error(request, "Seuls les parents peuvent déposer des demandes.")
        return redirect('home')

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            course_req = form.save(commit=False)
            course_req.parent = request.user
            course_req.save()
            form.save_m2m() # Sauvegarde des relations ManyToMany (Matières)
            
            messages.success(request, "Votre demande a été publiée ! Les professeurs vont vous contacter.")
            return redirect('dashboard')
    else:
        form = RequestForm()

    return render(request, 'marketplace/create_request.html', {'form': form})


@login_required
def edit_request(request, pk):
    """
    Permet au parent de modifier sa propre demande existante.
    """
    course_req = get_object_or_404(CourseRequest, pk=pk)

    # Sécurité : On vérifie que c'est bien le propriétaire
    if course_req.parent != request.user:
        messages.error(request, "Vous ne pouvez pas modifier cette demande.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=course_req)
        if form.is_valid():
            req = form.save(commit=False)
            # Si la demande était expirée/fermée, on la réactive en cas de modification
            if req.status != 'active':
                req.status = 'active'
            req.save()
            form.save_m2m()
            messages.success(request, "Votre demande a été mise à jour et validée !")
            return redirect('dashboard')
    else:
        form = RequestForm(instance=course_req)

    return render(request, 'marketplace/edit_request.html', {
        'form': form, 
        'course_req': course_req
    })


@login_required
def request_list(request):
    """
    Place de marché pour les ENSEIGNANTS.
    Affiche toutes les demandes actives des parents.
    """
    # Sécurité : Seuls les profs (ou admins) peuvent voir ça
    is_tutor = hasattr(request.user, 'role') and request.user.role == 'tutor'
    if not is_tutor and not request.user.is_superuser:
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('home')

    # On récupère toutes les demandes ACTIVES, triées par date récente
    requests = CourseRequest.objects.filter(status='active').order_by('-created_at')

    # Filtre par ville (si sélectionné dans le formulaire)
    city_id = request.GET.get('city')
    if city_id:
        requests = requests.filter(city_id=city_id)

    context = {
        'requests': requests,
        'cities': City.objects.all(), # Pour le menu déroulant du filtre
    }
    return render(request, 'marketplace/request_list.html', context)