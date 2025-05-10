from django.urls import path, reverse_lazy
from . import views
from . import models
# from mysite.owners import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView








app_name='docslist'
urlpatterns = [
    path('', views.DocsadsListView.as_view(), name='all'),

    path('docsads/<int:pk>/detail',
        views.DocsadsDetailView.as_view(), name='docsads_detail'),
    path('docsads/create', views.DocsadsCreateView.as_view(), name='docsads_create'),
    path('docsads/<int:pk>/update',
        views.DocsadsUpdateView.as_view(success_url=reverse_lazy('docslist:all')), name='docsads_update'),
    path('docsads/<int:pk>/delete',
        views.DocsadsDeleteView.as_view(success_url=reverse_lazy('docslist:all')), name='docsads_delete'),
    path('docsads_picture/<int:pk>', views.stream_file, name='docsads_picture'),
    path('docsads/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='docsads_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('docslist:all')), name='docsads_comment_delete'),
    path('docsads/<int:pk>/favorite',
        views.AddFavoriteView.as_view(), name='docsads_favorite'),
    path('docsads/<int:pk>/unfavorite',
        views.DeleteFavoriteView.as_view(), name='docsads_unfavorite'),

        ]
