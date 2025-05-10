from django.contrib import admin
from docslist.models import Docsads

# Register your models here.
class DocsadsAdmin(admin.ModelAdmin):
    exclude = ('picture', 'content_type')


admin.site.register(Docsads, DocsadsAdmin)