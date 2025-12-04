from .models import Message

def unread_count(request):
    """
    Ajoute la variable 'unread_messages_count' à tous les templates.
    Compte les messages non lus où l'utilisateur est participant mais PAS l'expéditeur.
    """
    count = 0
    if request.user.is_authenticated:
        # On cherche les messages dans les conversations du user
        # Qui ne sont PAS envoyés par lui-même
        # Et qui sont marqués comme non lus
        count = Message.objects.filter(
            thread__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    
    return {'unread_messages_count': count}