from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
  path("admin/", admin.site.urls),
  path("", include("collector.urls")),
]

if settings.DEBUG or getattr(settings, "LOCAL_TEST_MODE", False):
  urlpatterns += [
    path("assets/<path:path>", serve, {"document_root": settings.ASSETS_DIR}),
  ]
  if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
  else:
    urlpatterns += [
      re_path(r"^static/(?P<path>.*)$", staticfiles_serve, {"insecure": True}),
    ]
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
