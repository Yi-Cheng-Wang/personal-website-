"""myweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from mainsite import views

urlpatterns = [
    #中文專區
    path('', views.index, name='index'),
    path('about/me/', views.about_me, name='about_me'),
    path('about/links/', views.about_links, name='about_links'),
    path('about/card/', views.about_card, name='about_card'),
    path('history/web/', views.history_web, name='history_web'),
    
    #英文專區
    path('en/', views.index_en, name='index_en'),
    path('about/me/en/', views.about_me_en, name='about_me_en'),
    path('about/links/en/', views.about_links_en, name='about_links_en'),
    path('about/card/en/', views.about_card_en, name='about_card_en'),
    path('history/web/en/', views.history_web_en, name='history_web_en'),
    #機器人專區
    
    #搜尋引擎與 AI
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('llms.txt', views.llms_txt, name='llms_txt'),

    #其他
    path('hidden/generic/', views.generic, name='generic'),
    path('hidden/elements/', views.elements, name='elements'),
    #path('CapybaraKing_LineBot/callback', CapybaraKing_LineBotView.callback),
    #path('flying_ball/', views.flying_ball, name='flying_ball'),
    #path('admin/', admin.site.urls),
]

handler400 = views.bad_request
handler403 = views.permission_denied
handler404 = views.page_not_found
handler500 = views.server_error
