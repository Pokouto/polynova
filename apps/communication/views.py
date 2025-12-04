from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Thread, Message
from .forms import MessageForm

User = get_user_model()

@login_required
def start_thread(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.user == target_user: return redirect('dashboard')

    threads = Thread.objects.filter(participants=request.user).filter(participants=target_user)
    if threads.exists():
        thread = threads.first()
    else:
        thread = Thread.objects.create()
        thread.participants.add(request.user, target_user)
    
    return redirect('thread_detail', pk=thread.pk)

@login_required
def inbox(request):
    threads = request.user.threads.all().prefetch_related('participants', 'messages')
    threads_data = []
    for thread in threads:
        other_user = thread.get_other_participant(request.user)
        last_msg = thread.messages.last()
        threads_data.append({'thread': thread, 'other': other_user, 'last_msg': last_msg})
    return render(request, 'communication/inbox.html', {'threads_data': threads_data})

@login_required
def thread_detail(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    if request.user not in thread.participants.all():
        return redirect('inbox')

    thread.messages.exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.sender = request.user
            msg.save()
            thread.save() 
            return redirect('thread_detail', pk=pk)
    else:
        form = MessageForm()

    return render(request, 'communication/thread_detail.html', {
        'thread': thread,
        'messages_list': thread.messages.all(),
        'form': form,
        'other_user': thread.get_other_participant(request.user)
    })