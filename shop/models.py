from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.utils import timezone
import datetime as dt
import os
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.core.files.base import ContentFile
from PIL import Image
import fitz
import io


def getFileName(request, filename):
    now = dt.datetime.now().strftime("%Y%m%d%H%S")
    new_filename = f"{now}_{filename}"
    return os.path.join("uploads/", new_filename)


class Folder(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders",
    )

    def __str__(self):
        return self.name

    def get_path(self):
        path = []
        folder = self
        while folder:
            path.append(folder.name)
            folder = folder.parent
        return "/".join(reversed(path))


class File(models.Model):
    file = models.FileField(upload_to=getFileName)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, null=True, blank=True, related_name="files"
    )
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)

    def __str__(self):
        return self.file.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file:
            self.generate_thumbnail()
            if self.thumbnail:
                self.thumbnail.save(self.thumbnail.name, self.thumbnail, save=False)
        super().save(*args, **kwargs)

    def generate_thumbnail(self):
        if self.file.name.lower().endswith(".pdf"):
            self.generate_pdf_thumbnail()
        else:
            self.generate_image_thumbnail()

    def generate_pdf_thumbnail(self):
        try:
            document = fitz.open(self.file.path)
            page = document.load_page(0)  # Load the first page
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            thumbnail_io = io.BytesIO()
            image.save(thumbnail_io, format="JPEG")
            thumbnail_content = ContentFile(thumbnail_io.getvalue())
            self.thumbnail.save(
                f"{self.file.name}.thumbnail.jpg", thumbnail_content, save=False
            )
        except Exception as e:
            print(f"Error generating PDF thumbnail: {e}")

    def generate_image_thumbnail(self):
        try:
            image = Image.open(self.file.path)
            image.thumbnail((100, 100), Image.ANTIALIAS)
            thumbnail_io = io.BytesIO()
            image.save(thumbnail_io, format="JPEG")
            thumbnail_content = ContentFile(thumbnail_io.getvalue())
            self.thumbnail.save(
                f"{self.file.name}.thumbnail.jpg", thumbnail_content, save=False
            )
        except Exception as e:
            print(f"Error generating image thumbnail: {e}")


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    like_count = models.ManyToManyField(User, related_name="blog_post")

    def total_likes(self):
        return self.like_count.count()

    def __str__(self):
        return self.title


class Like(models.Model):
    post = models.ForeignKey(BlogPost, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Like by {self.user} on {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost, related_name="comments", on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")


class Video(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    caption = models.TextField()
