from django.shortcuts import render
from firebase_admin import db
import os
from django.conf import settings


def get_user_details(request):
    if request.method == "POST":
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        request.session['user_name'] = user_name
        request.session['user_email'] = user_email
        return render(request, 'audio_player.html', {'user_name': user_name})

    # if return != 'POST'
    return render(request, 'get_user_details.html')


def audio_player(request):
    audio_dir = os.path.join('media', 'audio')
    folders = sorted(os.listdir(audio_dir))
    folders.remove('.DS_Store')

    audio_files = []
    for folder in folders:
        folder_path = os.path.join(audio_dir, folder)
        if os.path.isdir(folder_path):
            files = sorted(os.listdir(folder_path))
            audio_files.append([os.path.join(folder, f) for f in files])

    return render(request, 'audio_player.html', {
        'audio_files': audio_files,
        'user_name': request.session.get('user_name'),
        'user_email': request.session.get('user_email'),
        'MEDIA_URL': settings.MEDIA_URL
    })


def submit_response(request):
    if request.method == "POST":
        user_name = request.session.get('user_name')
        user_email = request.session.get('user_email')
        selected_option = request.POST.get('option')
        audio_set_index = request.POST.get('audio_set_index')

        ref = db.reference(f'responses/{user_email}/set_{audio_set_index}')
        ref.set({
            'user_name': user_name,
            'selected_option': selected_option
        })

        return render(request, 'thank_you.html')

    return render(request, 'audio_player.html')
