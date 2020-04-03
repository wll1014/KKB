"""ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.documentation import include_docs_urls

from hosts.views import Login, ShowIndex, Check, IsLogin, Logout
from django.conf import settings
from django.conf.urls.static import static
from ops.settings import MEDIA_ROOT
from django.views.static import serve

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'^api/(?P<version>v\d+)/ops/login/$', Login.as_view()),  # 测试使用,获取ssoToken
    re_path(r'^api/(?P<version>v\d+)/ops/logout/$', Logout.as_view()),  # 注销
    re_path(r'^api/(?P<version>v\d+)/ops/islogin/$', IsLogin.as_view()),  # 验证是否登录
    re_path(r'^api/(?P<version>v\d+)/ops/sidebar/', include('sidebar.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/hosts/', include('hosts.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/maintenance/', include('maintenance.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/faq/', include('faq.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/oplog/', include('oplog.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/alarms/', include('warning.urls')),

    re_path(r'^api/(?P<version>v\d+)/ops/overview/', include('overview.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/statistics/', include('ops_statistics.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/confs/', include('platmonitor.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/hosts_oper/', include('hosts_oper.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/diagnose/', include('diagnose.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/issuetracking/', include('issue_tracking.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/versions/', include('version_control.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/report/', include('platreport.urls')),
    re_path(r'^api/(?P<version>v\d+)/ops/', include('overview.urls')),

    re_path(r'^api/v1/ops/media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    re_path(r'^api/(?P<version>v\d+)/ops/', include('ops_statistics.urls')),
    re_path(r'^ops$', ShowIndex.as_view()),
    re_path(r'^ops/$', ShowIndex.as_view()),
    re_path(r'^ops/check$', Check.as_view()),

    # path("api-docs/", include_docs_urls("API文档")),
    # ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
]
