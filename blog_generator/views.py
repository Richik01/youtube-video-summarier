from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
from groq import Groq
from .models import BlogPost
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")
# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # use GROQ to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)
        try:
            new_blog_article = BlogPost.objects.create(
                user=request.user,
                youtube_title=title,
                youtube_link=yt_link,
                generated_content=blog_content,
            )
            new_blog_article.save()
        except:
            pass

        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    foo = ''
    for i in title:
        if i.isalnum():
            foo += i
        else:
            break
    return foo



def get_transcription(link):
    yt = YouTube(link, on_progress_callback = on_progress)
    try:
        caption = yt.captions['en']
    except KeyError:
        try:
            caption = yt.captions['a.en']
        except KeyError:
            raise KeyError
    caption.save_captions('caption.txt')

    # Open the caption file
    with open("caption.txt", "r") as file:
        lines = file.readlines()

    # Initialize a list to hold caption lines
    captions = []

    # Process the lines
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        # Skip lines that are timestamps or numbering
        if not line or line.isdigit() or "-->" in line:
            continue
        # Add remaining lines to captions list
        captions.append(line)

    # Combine the lines into a single paragraph
    output = " ".join(captions)

    # Optionally save to a new file
    with open("caption.txt", "w") as outfile:
        outfile.write(output)
    return output

def generate_blog_from_transcription(transcription):
    client = Groq(
        api_key=API_KEY,
    )
    prompt = f"Instruction: Write a blog article for following youtube transcript \n\n{transcription}\n\nArticle:"
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    generated_content = chat_completion.choices[0].message.content

    return generated_content



def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
