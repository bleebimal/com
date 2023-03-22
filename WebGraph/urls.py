from django.contrib import admin
from django.urls import path
from WebGraph import views
from . import views, settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login),
    path("login/", views.validate_login),
    path("main/", views.index),
    path("analyze_data/", views.analyze_data),
    path("result/", views.result),
    path("logout/", views.logout_system),
    path("ajax/getData/", views.get_data),
    path("patent/", views.patent_quality),
    path("singleDomain/", views.single_domain),
    path("multipleDomain/", views.multiple_domain),
    path("relevance/", views.relevance),
    path("single_domain_analyze/", views.single_domain_analyze),
    path("multiple_domain_analyze/", views.multiple_domain_analyze),
    path("relevance_analyze/", views.relevance_analyze),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)