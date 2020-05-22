import requests

from isodate import parse_duration

from django.shortcuts import render, redirect
from django.conf import settings

def human_format(num):
    if num is not None:
        num = int(num)
        magnitude = 0
        temp=num
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        if temp <= 999:
            return '%d' % num
        else:
            return '%.2f%s' % (num, ['', 'k', 'M', 'B', 't', 'p'][magnitude])
    else:
        return 0
def convo(num):
    if num <= 59.0:
        return '%dsec'% num
    else:
        return '%dmin'% (num //60)

#int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),

def index(request):
    videos, search = [], []

    if request.method == 'POST':
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        try:
            search_params = {
                'part': 'snippet',
                'q': request.POST['search'],
                'key': settings.YOUTUBE_DATA_API_KEY,
                'maxResults': 12,
                'type': 'video',
                'eventType': "completed"
            }
            search = search_params
            r = requests.get(search_url, params=search_params)
            results = r.json()['items']

            video_ids = []
            for result in results:
                video_ids.append(result['id']['videoId'])

            if request.POST['submit'] == 'lucky':
                return redirect(f'https://www.youtube.com/watch?v={video_ids[0]}')

            video_params = {
                'key': settings.YOUTUBE_DATA_API_KEY,
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(video_ids),
                'maxResults': 12,
            }

            r = requests.get(video_url, params=video_params)

            results = r.json()['items']

            for result in results:
                video_data = {
                    'title': result['snippet']['title'],
                    'id': result['id'],
                    'likes': human_format(result['statistics'].get('likeCount')),
                    'views': human_format(result['statistics'].get('viewCount')),
                    'url': f'https://www.youtube.com/watch?v={result["id"]}',
                    'duration': convo(int(parse_duration(result['contentDetails']['duration']).total_seconds())),
                    'thumbnail': result['snippet']['thumbnails']['high']['url'],
                    'live': result['snippet']['liveBroadcastContent']
                }
                #print("Like count is", video_data['likes']) #Yayyy I did it Thank god ;-;
                videos.append(video_data)
        except KeyError as e:
            print("Warning: Check Quota limit", e)

    context = {
        'videos': videos,
        'search': search
    }
    return render(request, 'search/index.html', context)
