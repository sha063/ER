from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import Ocr
from pdf2image import convert_from_path, convert_from_bytes
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.views import View
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login as auth_login, logout
from django.db import models
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
    user_passes_test,
)
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage  # Import FileSystemStorage
from io import BytesIO
from pdf2image import convert_from_path
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpRequest, HttpResponse
from pdf2image import convert_from_path
import numpy as np
import cv2


def superuser_required(view_func):
    actual_decorator = user_passes_test(
        lambda user: user.is_superuser,
        login_url=reverse("admin"),  # Use reverse to get the admin login URL
    )
    return actual_decorator(view_func)


# links
Accounts = "Accounts"

Home = "Home"
Profile = "Profile"
About = "About"
PagesFaq = "PagesFaq"

Add_Post = "Add Post"
Post_Details = "Post Details"
Edit_Post = "Edit Post"
Review_Post = "Review Post"

File_Manager = "File Manager"
Create_Folder = "Create Folder"

Login = "account_login"
Logout = "account_logout"

Me = "Me"


class profile_header:
    def __init__(self, icon, name, link):
        self.icon = icon
        self.name = name
        self.link = link


class a:
    def __init__(self, name, icon, list):
        self.name = name
        self.list = list
        self.icon = icon


class b:
    def __init__(self, name, link):
        self.name = name
        self.link = link


class c:
    def __init__(self, icon, field, subject1, subject2):
        self.icon = icon
        self.field = field
        self.subject1 = subject1
        self.subject2 = subject2


class part:
    def __init__(self, name, image, description):
        self.name = name
        self.image = image
        self.description = description


# utils.py


def superuser_required(view_func):
    actual_decorator = user_passes_test(
        lambda user: user.is_superuser,
        login_url="Home",  # Replace with your desired login URL
    )
    return actual_decorator(view_func)


def email_check(user):
    return user.email.endswith("@example.com")


ProfileHeader = [
    profile_header("person", "My Profile", Profile),
    profile_header("question-circle", "Need Help?", PagesFaq),
    profile_header("box-arrow-right", "Sign In", Login),
    profile_header("box-arrow-left", "Sign Out", Logout),
]

alist = [
    a(
        "Dashboard",
        "menu-button-wide",
        [
            b("Home", "Home"),
            b("About", "About"),
            b("Pages FAQ", "PagesFaq"),
            b("Resources", "File"),
            b("Ocr", "Ocr"),
            b("Me", "Me"),
        ],
    ),
    a(
        "Home",
        "house",
        [
            b("Blogs", "#blog"),
        ],
    ),
]

ids = {
    "home": False,
    "profile": False,
    "about": False,
    "pages_faq": False,
    "post_add": False,
    "post_review": False,
    "post_details": False,
    "post_edit": False,
    "comment_edit": False,
    "file_list": False,
    "create_folder": False,
    "ocr": False,
}


def convert_to_images_and_ocr(file_path, output_dir, dpi=300, lang="eng"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        text_file_path = os.path.join(output_dir, "extracted_text.txt")

        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(file_path, dpi=dpi)
        elif file_path.lower().endswith(
            (".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp")
        ):
            images = [Image.open(file_path)]
        else:
            raise ValueError(
                "Unsupported file type. Supported types are PDF, JPG, JPEG, PNG, GIF, TIFF, and BMP."
            )

        def preprocess_image(image):
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Apply dilation and erosion to remove some noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            gray = cv2.dilate(gray, kernel, iterations=1)
            gray = cv2.erode(gray, kernel, iterations=1)
            # Apply blur to smooth out the edges
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            # Apply thresholding to get a binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary

        with open(text_file_path, "w", encoding="utf-8") as text_file:
            for i, image in enumerate(images):
                if len(images) > 1:
                    image_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
                    image.save(image_path, "JPEG")
                    print(f"Saved {image_path}")

                # Convert PIL image to OpenCV format
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                preprocessed_image = preprocess_image(open_cv_image)

                # Convert back to PIL image
                preprocessed_pil_image = Image.fromarray(preprocessed_image)

                custom_config = r"--oem 3 --psm 1"
                text = pytesseract.image_to_string(
                    preprocessed_pil_image, lang=lang, config=custom_config
                )

                text_file.write(text)

                if len(images) > 1:
                    os.remove(image_path)
                    print(f"Deleted {image_path}")

        print(f"OCR completed, and text saved to {text_file_path}.")
        return text_file_path
    except Exception as e:
        print(f"Error processing file: {e}")
        return None


def ocr(request):
    for i in ids:
        ids[i] = False
    ids["ocr"] = True
    if request.method == "POST":
        form = Ocr(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            file_name = file.name
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
            ]  # Adjust as needed
            if file.content_type not in allowed_types:
                return render(
                    request,
                    "shop/habf.html",
                    {
                        "form": form,
                        "error_message": "File type not supported.",
                        "idn": ids,
                        "alist": alist,
                        "title": "E-Resource",
                        "page_title": Home,
                        "profile_header": ProfileHeader,
                    },
                )
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file_path = os.path.join(upload_dir, file_name)
            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            text_file_path = convert_to_images_and_ocr(file_path, upload_dir)
            if text_file_path:
                with open(text_file_path, "r", encoding="utf-8") as text_file:
                    content = text_file.read()
                os.remove(text_file_path)
                os.remove(file_path)
                return render(
                    request,
                    "shop/habf.html",
                    {
                        "file_name": file_name,
                        "content": content,
                        "idn": ids,
                        "alist": alist,
                        "title": "E-Resource",
                        "page_title": Home,
                        "profile_header": ProfileHeader,
                    },
                )
            else:
                return render(
                    request,
                    "shop/habf.html",
                    {
                        "form": form,
                        "error_message": "Error processing file.",
                        "idn": ids,
                        "alist": alist,
                        "title": "E-Resource",
                        "page_title": Home,
                        "profile_header": ProfileHeader,
                    },
                )
    else:
        form = Ocr()
    return render(
        request,
        "shop/habf.html",
        {
            "form": form,
            "idn": ids,
            "alist": alist,
            "title": "E-Resource",
            "page_title": Home,
            "profile_header": ProfileHeader,
        },
    )


def home(request):
    posts = BlogPost.objects.filter(approved=True).order_by("-created_at")
    videos = Video.objects.all()
    files = File.objects.all()
    try:
        response = requests.get("https://api.quotable.io/random")
        response.raise_for_status()
        response.status_code == 200
        data = response.json()
        quote = data['content']
        author = data['author']
    except (requests.ConnectionError, requests.Timeout, requests.RequestException):
        quote = "There is no quote can make you up unless you make your quote"
        author = "By you"
    pre = "assets/img/slides-"
    suf = ".jpg"
    l = ["active", "", ""]
    m = ['aria-current="true"', "", ""]
    z = []

    def stringify():
        for i, j, k in zip(range(1, 4), l, m):
            list = {}
            list["loc"] = pre + str(i) + suf
            list["stat"] = j
            list["n"] = str(i)
            list["nu"] = str(i - 1)
            list["ac"] = k
            z.append(list)
        return z

    template = loader.get_template("shop/habf.html")
    for i in ids:
        ids[i] = False
    ids["home"] = True
    context = {
        "title": "E-Resource",
        "page_title": Home,
        "profile_header": ProfileHeader,
        "dict": stringify(),
        "list": ["prev", "next"],
        "posts": posts,
        "idn": ids,
        "alist": alist,
        "videos": videos,
        "files":files,
        'quote': quote, 'author': author
    }
    return HttpResponse(template.render(context, request))


def tetris_game(request):
    return render(request, "shop/layouts/game/brick.html")


@login_required(login_url="Login")
def profile(request):
    for i in ids:
        ids[i] = False
    ids["profile"] = True
    posts = BlogPost.objects.filter(author=request.user).order_by("-created_at")
    template = loader.get_template("shop/habf.html")
    context = {
        "posts": posts,
        "page_title": Profile,
        "profile_header": ProfileHeader,
        "alist": alist,
        "title": "E-Resource",
        "idn": ids,
    }
    return HttpResponse(template.render(context, request))


def about(request):
    for i in ids:
        ids[i] = False
    ids["about"] = True
    d = [
        c(
            "geo-alt",
            "Address",
            "South Eastern University of Sri Lanka | SEUSL",
            "University Park, Oluvil, #32360, Sri Lanka.",
        ),
        c("telephone", "Call Us", "+94 764 791 874", "+94 764 791 874"),
    ]
    template = loader.get_template("shop/habf.html")
    context = {
        "title": "E-Resource",
        "page_title": About,
        "idn": ids,
        "profile_header": ProfileHeader,
        "alist": alist,
        "list": d,
    }
    return HttpResponse(template.render(context, request))


def pages_faq(request):
    for i in ids:
        ids[i] = False
    ids["pages_faq"] = True
    template = loader.get_template("shop/habf.html")
    context = {
        "title": "E-Resource",
        "page_title": PagesFaq,
        "profile_header": ProfileHeader,
        "alist": alist,
        "idn": ids,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="Login")
def file_list(request, folder_id=None):
    for i in ids:
        ids[i] = False
    ids["file_list"] = True
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id)
        parent_folder = current_folder.parent
        folders = current_folder.subfolders.all()
        files = current_folder.files.all()
        current_path = current_folder.get_path()
    else:
        current_folder = None
        parent_folder = None
        folders = Folder.objects.filter(parent=None)
        files = File.objects.filter(folder__isnull=True)
        current_path = "Root"

    is_superuser = request.user.is_superuser  # Check if user is superuser

    return render(
        request,
        "shop/habf.html",
        {
            "title": "E-Resource",
            "current_folder": current_folder,
            "parent_folder": parent_folder,
            "folders": folders,
            "files": files,
            "is_superuser": is_superuser,  # Pass is_superuser flag to template
            "page_title": File_Manager,
            "profile_header": ProfileHeader,
            "alist": alist,
            "idn": ids,
            "current_path": current_path,
        },
    )


@superuser_required
@login_required(login_url="Login")
def upload_file(request, folder_id=None, parent_id=None):
    if not request.user.is_superuser:
        messages.error(request, "This action requires superuser privileges.")
        return redirect("file_list")  # Redirect to file_list if not superuser

    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            if folder_id:
                file_instance.folder = get_object_or_404(Folder, id=folder_id)
            elif parent_id:
                file_instance.folder = get_object_or_404(Folder, id=parent_id)
            else:
                root_folder, created = Folder.objects.get_or_create(
                    name="Root", parent=None
                )
                file_instance.folder = root_folder
            file_instance.save()
            return redirect("file_list", folder_id=file_instance.folder.id)
    else:
        form = FileForm()
    return render(
        request,
        "shop/layouts/file&folder/upload_file.html",
        {
            "title": "E-Resource",
            "form": form,
            "folder_id": folder_id,
            "page_title": Profile,
            "profile_header": ProfileHeader,
            "alist": alist,
        },
    )


@superuser_required
@login_required(login_url="Login")
def create_folder(request, parent_id=None):
    for i in ids:
        ids[i] = False
    ids["create_folder"] = True
    if not request.user.is_superuser:
        messages.error(request, "This action requires superuser privileges.")
        return redirect("file_list")  # Redirect to file_list if not superuser

    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            folder_instance = form.save(commit=False)
            if parent_id:
                folder_instance.parent = get_object_or_404(Folder, id=parent_id)
            folder_instance.save()
            return redirect(
                "file_list", folder_id=parent_id if parent_id else folder_instance.id
            )
    else:
        form = FolderForm()
    return render(
        request,
        "shop/habf.html",
        {
            "title": "E-Resource",
            "form": form,
            "parent_id": parent_id,
            "page_title": File_Manager,
            "profile_header": ProfileHeader,
            "alist": alist,
            "idn": ids,
        },
    )


@login_required(login_url="Login")
def download_file(request, file_id):
    file = File.objects.get(id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = (
                f"inline; filename={os.path.basename(file_path)}"
            )
            return response
    raise Http404


@superuser_required
@login_required(login_url="Login")
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    file.delete()
    messages.success(request, "File deleted successfully.")
    return redirect("file_list", folder_id=file.folder.id if file.folder else None)


@superuser_required
@login_required(login_url="Login")
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    parent_folder_id = folder.parent.id if folder.parent else None
    folder.delete()
    messages.success(request, "Folder and all its contents deleted successfully.")
    # Redirect to the root folder if there is no parent folder
    if parent_folder_id:
        return redirect("file_list", folder_id=parent_folder_id)
    else:
        return redirect("file_list")  # Redirect to root or base file list


@login_required(login_url="Login")
def blog_detail(request, pk):
    for i in ids:
        ids[i] = False
    ids["post_details"] = True
    post = get_object_or_404(BlogPost, pk=pk)
    comments = post.comments.all()
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("blog_detail", pk=post.pk)
    else:
        comment_form = CommentForm()
    return render(
        request,
        "shop/habf.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "alist": alist,
            "profile_header": ProfileHeader,
            "page_title": Post_Details,
            "idn": ids,
            "title": "E-Resource",
        },
    )


@login_required(login_url="Login")
def add_blog_post(request):
    for i in ids:
        ids[i] = False
    ids["post_add"] = True
    if request.method == "POST":
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(
                request, "Your post has been submitted and is awaiting review."
            )
            return redirect("Home")
    else:
        form = BlogPostForm()
    return render(
        request,
        "shop/habf.html",
        {
            "title": "E-Resource",
            "form": form,
            "alist": alist,
            "profile_header": ProfileHeader,
            "page_title": Add_Post,
            "idn": ids,
        },
    )


@login_required(login_url="Login")
def ajax_like_post(request, pk):
    if request.method == "POST":
        post = get_object_or_404(BlogPost, id=pk)
        if request.user in post.like_count.all():
            post.like_count.remove(request.user)
            liked = False
        else:
            post.like_count.add(request.user)
            liked = True
        return JsonResponse({"total_likes": post.total_likes(), "liked": liked})


@superuser_required
@login_required(login_url="Login")
def review_posts(request):
    for i in ids:
        ids[i] = False
    ids["post_review"] = True
    posts = BlogPost.objects.filter(approved=False).order_by("-created_at")
    if request.method == "POST":
        post_ids = request.POST.getlist("post_ids")
        BlogPost.objects.filter(id__in=post_ids).update(approved=True)
        return redirect("review_posts")
    return render(
        request,
        "shop/habf.html",
        {
            "posts": posts,
            "alist": alist,
            "profile_header": ProfileHeader,
            "title": "E-Resource",
            "page_title": Review_Post,
            "idn": ids,
        },
    )


def superuser_or_author_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        post = get_object_or_404(BlogPost, pk=kwargs["pk"])
        if request.user.is_superuser or request.user == post.author:
            return view_func(request, *args, **kwargs)
        return redirect("Home")

    return _wrapped_view


@superuser_or_author_required
@login_required(login_url="Login")
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    referrer = request.META.get("HTTP_REFERER", "")
    if "Home" in referrer:
        previous_page = "Home"
    else:
        previous_page = "review_posts"
    if request.method == "POST":
        post.delete()
        return redirect(previous_page)
    return render(
        request,
        "shop/layouts/post/post_detail.html",
        {
            "post": post,
            "alist": alist,
            "profile_header": ProfileHeader,
            "previous_page": previous_page,
        },
    )


@login_required(login_url="Login")
def edit_post(request, pk):
    for i in ids:
        ids[i] = False
    ids["post_edit"] = True
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user != post.author:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("Home")

    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Your post has been updated.")
            return redirect("blog_detail", pk=post.pk)
    else:
        form = BlogPostForm(instance=post)
    return render(
        request,
        "shop/habf.html",
        {
            "form": form,
            "post": post,
            "alist": alist,
            "profile_header": ProfileHeader,
            "page_title": Edit_Post,
            "idn": ids,
        },
    )


def blog_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        instance = UploadedFile(file=uploaded_file)
        instance.save()
        return JsonResponse({"location": instance.file.url})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required(login_url="Login")
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author or request.user.is_staff:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    return redirect("blog_detail", pk=comment.post.pk)


@login_required(login_url="Login")
def edit_comment(request, pk):
    for i in ids:
        ids[i] = False
    ids["comment_edit"] = True
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect("blog_detail", pk=comment.post.pk)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully.")
            return redirect("blog_detail", pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "shop/habf.html",
        {
            "form": form,
            "comment": comment,
            "idn": ids,
        },
    )


def me(request):
    return render(request, "shop/layouts/me.html")

import requests
from django.shortcuts import render

def fetch_news(request):
    api_key = 'YOUR_NEWSAPI_KEY'  # Replace with your NewsAPI key
    keyword = request.GET.get('keyword', '')  # Get keyword from query parameters
    url = f'https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}' if keyword else f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        news_articles = response.json().get('articles', [])
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        news_articles = []

    context = {"news_articles": news_articles,"keyword": keyword}
    return render(request, "shop/layouts/news/news.html", context)
