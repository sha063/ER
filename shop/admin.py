from django.contrib import admin
from .models import *
from .forms import *


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "approved", "created_at")
    list_filter = ("approved", "created_at", "updated_at")
    search_fields = ("title", "author__username", "content")
    actions = ["approve_posts"]

    def approve_posts(self, request, queryset):
        queryset.update(approved=True)

    approve_posts.short_description = "Approve selected posts"


admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Folder)
admin.site.register(File)
admin.site.register(UploadedFile)
admin.site.register(Video)
