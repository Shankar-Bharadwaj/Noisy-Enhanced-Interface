from django.shortcuts import render, redirect
from firebase_admin import db, storage
import os
from django.conf import settings
from urllib.parse import quote
import random


def home(request):
    return render(request, 'home.html')


def get_user_details(request):
    if request.method == "POST":
        user_name = request.POST.get('name')
        user_email = request.POST.get('email')
        request.session['user_name'] = user_name
        request.session['user_email'] = user_email

        # Get audio files from Firebase Storage
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix='media/audio/')
        
        audio_files = {}
        for blob in blobs:
            if not blob.name.endswith('/'):
                parts = blob.name.split('/')
                if len(parts) > 2:
                    folder = parts[2]
                    file_name = '/'.join(parts[3:])
                    
                    # Extract the word (assuming it is the second element split by '_')
                    word = file_name.split('_')[1] if len(file_name.split('_')) > 1 else ''
                    
                    # Construct the URL
                    encoded_name = quote(blob.name, safe='')
                    url = f"{settings.MEDIA_URL}{encoded_name}?alt=media"


                    
                    # Add to the dictionary
                    if folder not in audio_files:
                        audio_files[folder] = []
                    
                    if '-' in folder:
                        language = 'ITA'
                    else:
                        language = 'GER'

                    audio_files[folder].append({
                        'name': file_name,
                        'url': url,
                        'word': word,
                        'language': language
                    })

        # Shuffle the order of audio folders
        folder_keys = list(audio_files.keys())
        random.shuffle(folder_keys)

        # Group files for pagination, each folder is one group
        grouped_files = [audio_files[folder] for folder in folder_keys]
        request.session['grouped_files'] = grouped_files  # Store in session for pagination

        return redirect('audio_player', page_number=1)

    return render(request, 'get_user_details.html')


def audio_player(request, page_number=1):
    grouped_files = request.session.get('grouped_files')
    if not grouped_files:
        return redirect('get_user_details')

    page_number = int(page_number)
    total_pages = len(grouped_files)

    if page_number > total_pages or page_number < 1:
        return redirect('audio_player', page_number=1)
    
    audio_set = grouped_files[page_number - 1]

    # Randomise the audio options
    optional_audios = audio_set[1:]
    random.shuffle(optional_audios)

    audio_set = [audio_set[0]] + optional_audios

    request.session['audio_set'] = audio_set
    
    context = {
        'user_name': request.session.get('user_name'),
        'user_email': request.session.get('user_email'),
        'audio_set': audio_set,
        'page_number': page_number,
        'has_next': page_number < total_pages,
        'previous_page': page_number - 1,
        'next_page': page_number + 1 if page_number < total_pages else None
    }
    
    return render(request, 'audio_player.html', context)


def sanitize(email):
    """Sanitize email to remove illegal characters for Firebase."""
    ind = email.index('@')
    return email[:ind]


def submit_response(request, page_number=None):
    if request.method == "POST":
        user_name = request.session.get('user_name')
        user_email = request.session.get('user_email')
        grouped_files = request.session.get('grouped_files')
        audio_set = request.session.get('audio_set')

        # Iterate through all audio sets and collect responses
        responses = {}
        for key, value in request.POST.items():
            if key.startswith('option_'):
                audio_set_index = key.split('_')[1]
                if value!='None':
                    audio_details = audio_set[int(value)]
                    selected_audio = audio_details['name']
                    language = audio_details['language']
                else:
                    selected_audio = audio_set[0]['name']
                    language = 'None'
                responses[f'set_{audio_set_index}'] = {
                    'selected_option': value,
                    'file_name': selected_audio,
                    'language': language
                }

        # Reference to the Firebase RTDB
        mail = sanitize(user_email)
        ref = db.reference(f'responses/{mail}')
        existing_data = ref.get()
        if existing_data:
            existing_responses = existing_data.get('responses', {})
            existing_responses.update(responses)
            ref.update({
                'responses': existing_responses
            })
        else:
            ref.set({
                'user_name': user_name,
                'responses': responses
            })


        # Pagination handling
        grouped_files = request.session.get('grouped_files')
        if page_number:
            next_page = int(page_number) + 1
            if next_page <= len(grouped_files):
                return redirect('audio_player', page_number=next_page)
        
        return redirect('success_page')

    return redirect('audio_player', page_number=page_number)


def success_page(request):
    return render(request, 'thank_you.html')
