from django.http import HttpResponse
from django.shortcuts import render
from django.urls import URLPattern, get_resolver, reverse

# Create your views here.

# 中英文頁面對照，用於右上角的語言切換
LANGUAGE_PAIRS = {
    'index': 'index_en',
    'about_me': 'about_me_en',
    'about_links': 'about_links_en',
    'history_web': 'history_web_en',
}
LANGUAGE_PAIRS.update({en: tw for tw, en in LANGUAGE_PAIRS.items()})

def _is_en(request):
    return '/en' in request.path

def _page(request, template_name, status=200):
    match = request.resolver_match
    page = match.url_name if match else ''
    alt = LANGUAGE_PAIRS.get(page) or ('index' if _is_en(request) else 'index_en')
    return render(request, template_name, {'page': page, 'alt_url': reverse(alt)}, status=status)

#中文專區
def index(request):
    return _page(request, 'tw/index.html')
def about_me(request):
    return _page(request, 'tw/about_me.html')
def about_links(request):
    return _page(request, 'tw/about_links.html')
def history_web(request):
    return _page(request, 'tw/history_web.html')

#英文專區
def index_en(request):
    return _page(request, 'en/index.html')
def about_me_en(request):
    return _page(request, 'en/about_me.html')
def about_links_en(request):
    return _page(request, 'en/about_links.html')
def history_web_en(request):
    return _page(request, 'en/history_web.html')

#錯誤專區
def bad_request(request, exception):
    return _page(request, 'error/page_400_en.html' if _is_en(request) else 'error/page_400.html', 400)
def permission_denied(request, exception):
    return _page(request, 'error/page_403_en.html' if _is_en(request) else 'error/page_403.html', 403)
def page_not_found(request, exception):
    return _page(request, 'error/not_support_en.html' if _is_en(request) else 'error/page_404.html', 404)
def server_error(request):
    return _page(request, 'error/page_500_en.html' if _is_en(request) else 'error/page_500.html', 500)

#搜尋引擎
SITE_URL = 'https://yichengs.tw'

def _public_pages():
    """從 urls.py 自動找出公開頁面：有名稱、沒有網址參數、不在 hidden/ 底下。"""
    for pattern in get_resolver().url_patterns:
        if (isinstance(pattern, URLPattern) and pattern.name
                and pattern.name not in ('sitemap', 'robots_txt')
                and pattern.pattern.regex.groups == 0
                and not str(pattern.pattern).startswith('hidden/')):
            yield pattern.name

def sitemap(request):
    pages = []
    for name in _public_pages():
        alternates = []
        if name in LANGUAGE_PAIRS:
            tw, en = (LANGUAGE_PAIRS[name], name) if name.endswith('_en') else (name, LANGUAGE_PAIRS[name])
            alternates = [
                {'lang': 'zh-Hant', 'href': SITE_URL + reverse(tw)},
                {'lang': 'en', 'href': SITE_URL + reverse(en)},
                {'lang': 'x-default', 'href': SITE_URL + reverse(tw)},
            ]
        pages.append({'loc': SITE_URL + reverse(name), 'alternates': alternates})
    return render(request, 'sitemap.xml', {'pages': pages}, content_type='application/xml')

def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /hidden/',
        '',
        f"Sitemap: {SITE_URL}{reverse('sitemap')}",
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')

#其他
def generic(request):
    return render(request, 'tw/generic.html')
def elements(request):
    return render(request, 'tw/elements.html')
def flying_ball(request):
    return render(request, 'tw/flying ball.html')
