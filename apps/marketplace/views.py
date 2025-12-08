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
    Affiche l'annuaire des professeurs avec filtres.
    """
    tutors = TutorProfile.objects.filter(status='validated')

    subject_id = request.GET.get('subject')
    city_id = request.GET.get('city')
    level_id = request.GET.get('level')

    if subject_id:
        tutors = tutors.filter(subjects__id=subject_id)
    
    if level_id:
        tutors = tutors.filter(levels__id=level_id)
        
    # Note: Pour filtrer par ville, il faudrait lier City au TutorProfile dans le futur
    # if city_id: tutors = tutors.filter(city_id=city_id)

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
    Affiche le profil public complet d'un prof avec Paywall et Avis.
    """
    tutor = get_object_or_404(TutorProfile, pk=pk, status='validated')
    
    # --- Gestion du Paywall ---
    is_unlocked = False
    if request.user.is_authenticated:
        if request.user == tutor.user or request.user.is_superuser:
            is_unlocked = True
        elif ContactUnlock.objects.filter(parent_user=request.user, tutor_profile=tutor).exists():
            is_unlocked = True

    # --- Gestion des Avis ---
    reviews = tutor.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Formulaire d'avis (si autorisé)
    review_form = None
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
        'avg_rating': round(avg_rating, 1),
        'review_count': reviews.count(),
        'review_form': review_form,
    }
    return render(request, 'marketplace/tutor_detail.html', context)


@login_required
def create_request(request):
    """
    Permet à un parent de poster une nouvelle demande.
    Applique l'algorithme de SCORING pour qualifier le lead.
    """
    is_parent = hasattr(request.user, 'role') and request.user.role == 'parent'
    if not is_parent and not request.user.is_superuser:
        messages.error(request, "Seuls les parents peuvent déposer des demandes.")
        return redirect('home')

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.parent = request.user
            
            # --- ALGORITHME DE SCORING (Règles CDC) ---
            # 1. Budget suffisant (>= 30 000)
            strong_budget = req.budget_range in ['standard', 'high', 'premium']
            
            # 2. Délai court (Immédiat ou < 4 semaines)
            strong_start = req.start_time in ['asap', '1-4weeks']
            
            # 3. Intention déclarée
            wants_to_start = req.intention == 'start'

            # Route A : Intention Forte
            if wants_to_start and strong_start and strong_budget:
                req.qualification = "Intention Forte"
                req.save()
                form.save_m2m()
                messages.success(request, "Excellent ! Votre demande est prioritaire. Les enseignants vont vous contacter.")
            
            # Route B : Intention Tiède
            elif (req.intention == 'info' or req.start_time == 'later') and strong_budget:
                req.qualification = "Intention Tiède"
                req.save()
                form.save_m2m()
                messages.info(request, "Demande enregistrée. Vous recevrez des informations par email.")
            
            # Route C : Budget Faible / Autre
            else:
                req.qualification = "Budget Limité / Autre"
                req.save()
                form.save_m2m()
                messages.warning(request, "Votre budget est un peu bas pour trouver rapidement un professeur, mais votre annonce est en ligne.")

            return redirect('dashboard')
    else:
        form = RequestForm()

    return render(request, 'marketplace/create_request.html', {'form': form})


@login_required
def edit_request(request, pk):
    """
    Permet au parent de modifier sa propre demande.
    """
    course_req = get_object_or_404(CourseRequest, pk=pk)

    if course_req.parent != request.user:
        messages.error(request, "Vous ne pouvez pas modifier cette demande.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=course_req)
        if form.is_valid():
            req = form.save(commit=False)
            if req.status != 'active':
                req.status = 'active' # Réactivation si modifiée
            req.save()
            form.save_m2m()
            messages.success(request, "Votre demande a été mise à jour.")
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
    Place de marché pour les ENSEIGNANTS (Voir les offres).
    """
    is_tutor = hasattr(request.user, 'role') and request.user.role == 'tutor'
    if not is_tutor and not request.user.is_superuser:
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('home')

    # Récupère les demandes ACTIVES
    requests = CourseRequest.objects.filter(status='active').order_by('-created_at')

    # Filtre ville
    city_id = request.GET.get('city')
    if city_id:
        requests = requests.filter(city_id=city_id)

    context = {
        'requests': requests,
        'cities': City.objects.all(),
    }
    return render(request, 'marketplace/request_list.html', context)