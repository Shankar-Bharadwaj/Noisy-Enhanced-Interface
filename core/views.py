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

        # Iterate through all audio sets and collect responses
        responses = {}
        for key, value in request.POST.items():
            if key.startswith('option_'):
                audio_set_index = key.split('_')[1]
                responses[f'set_{audio_set_index}'] = value

        # Reference to the Firebase RTDB
        ref = db.reference(f'responses/{user_name}')
        ref.set({
            'user_name': user_name,
            'responses': responses
        })

        return render(request, 'thank_you.html')

    return render(request, 'audio_player.html')
