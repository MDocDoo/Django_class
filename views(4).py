
from docslist.models import Docsads, Comment, Fav
from docslist.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from docslist.forms import CreateForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from docslist.forms import CommentForm
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from django.http import FileResponse, HttpRequest
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.db.models import Q


class DocsadsListView(View):
    model = Docsads
    template_name = "docslist/docsads_list.html"
    # By convention:
    # template_name = "myarts/article_list.html"


    def get(self, request) :
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().distinct().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__in=[strval]), Q.OR)
            docsads_list = Docsads.objects.filter(query).select_related().distinct().order_by('-updated_at')[:10]
        else :
            docsads_list = Docsads.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in docsads_list:
            obj.natural_updated = naturaltime(obj.updated_at)

        favorites = list()
        if request.user.is_authenticated:
                rows = request.user.favorite_docslist.values('id')
                favorites = [row['id'] for row in rows]

        ctx = {'docsads_list' : docsads_list , 'search': strval, 'favorites': favorites}
        return render(request, self.template_name, ctx)



class DocsadsDetailView(OwnerDetailView, View):
    model = Docsads
    template_name = "docslist/docsads_detail.html"
    fields = ['title', 'price', 'text', 'tags']
    def get(self, request, pk) :
        x = get_object_or_404(Docsads, id=pk)
        comments = Comment.objects.filter(docsads=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'docsads' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

class DocsadsCreateView(LoginRequiredMixin, View):
    template_name = "docslist/docsads_form.html"
    success_url = reverse_lazy('docslist:all')
    # List the fields to copy from the Article model to the Article form
    fields = ['title', 'price', 'text', 'tags']

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        docsads = form.save(commit=False)
        docsads.owner = self.request.user
        docsads.save()
        form.save_m2m()
        return redirect(self.success_url)

class DocsadsUpdateView(LoginRequiredMixin, View):

    fields = ['title', 'price', 'text', 'tags']
    # This would make more sense
    # fields_exclude = ['owner', 'created_at', 'updated_at']
    template_name = 'docslist/docsads_form.html'
    success_url = reverse_lazy('docslist:all')

    def get(self, request, pk):
        docsads = get_object_or_404(Docsads, id=pk, owner=self.request.user)
        form = CreateForm(instance=docsads)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        docsads = get_object_or_404(Docsads, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=docsads)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        docsads = form.save(commit=False)
        docsads.save()
        form.save_m2m()
        return redirect(self.success_url)

class DocsadsDeleteView(OwnerDeleteView):
    model = Docsads
    template_name = "docslist/delete.html"

def stream_file(request, pk):
    docsads = get_object_or_404(Docsads, id=pk)
    response = HttpResponse()
    response['Content-Type'] = docsads.content_type
    response['Content-Length'] = len(docsads.picture)
    response.write(docsads.picture)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Docsads, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, docsads=f)
        comment.save()
        return redirect(reverse('docslist:docsads_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "docslist/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        docsads = self.object.docsads
        return reverse('docslist:docsads_detail', args=[docsads.id])

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError


@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Docsads, id=pk)
        fav = Fav(user=request.user, docsads=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError:
            pass
        return HttpResponse("Favorite added")

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Docsads, id=pk)
        try:
            Fav.objects.get(user=request.user, docsads=t).delete()
        except Fav.DoesNotExist:
            pass

        return HttpResponse("Favorite deleted")

@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    path = (settings.BASE_DIR / "static" / "favicon.ico")
    return FileResponse(path.open("rb"), content_type = "image/x-icon")
