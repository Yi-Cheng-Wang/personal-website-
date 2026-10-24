import logging

from django.db import DatabaseError, connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import URLPattern, get_resolver, reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

logger = logging.getLogger(__name__)

# Create your views here.

# 中英文頁面對照，用於右上角的語言切換
LANGUAGE_PAIRS = {
    'index': 'index_en',
    'about_me': 'about_me_en',
    'about_links': 'about_links_en',
    'about_card': 'about_card_en',
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
def about_card(request):
    return _page(request, 'tw/about_card.html')
def history_web(request):
    return _page(request, 'tw/history_web.html')

#英文專區
def index_en(request):
    return _page(request, 'en/index.html')
def about_me_en(request):
    return _page(request, 'en/about_me.html')
def about_links_en(request):
    return _page(request, 'en/about_links.html')
def about_card_en(request):
    return _page(request, 'en/about_card.html')
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

#健康檢查
@require_safe
@never_cache
def healthcheck(request):
    """給監控用：網站正常回 200；資料庫連不上回 503（不公開錯誤細節）。"""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        logger.exception('healthcheck: database unavailable')
        return JsonResponse({'status': 'error', 'database': 'error'}, status=503)
    return JsonResponse({'status': 'ok', 'database': 'ok'})

#搜尋引擎與 AI
SITE_URL = 'https://yichengs.tw'
# 不是頁面的路由，不列進 sitemap / llms.txt
NON_PAGE_ROUTES = ('sitemap', 'robots_txt', 'llms_txt', 'healthcheck')
# llms.txt 的連結名稱；沒列到的頁面會用網址代替
PAGE_LABELS = {
    'index': '首頁', 'about_me': '關於我', 'about_links': '相關連結', 'about_card': '電子名片', 'history_web': '網站歷史',
    'index_en': 'Home', 'about_me_en': 'About', 'about_links_en': 'Links', 'about_card_en': 'Business card',
    'history_web_en': 'Site history',
}

def _public_pages():
    """從 urls.py 自動找出公開頁面：有名稱、沒有網址參數、不在 hidden/ 底下。"""
    for pattern in get_resolver().url_patterns:
        if (isinstance(pattern, URLPattern) and pattern.name
                and pattern.name not in NON_PAGE_ROUTES
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
    # 所有搜尋引擎與 AI 爬蟲（GPTBot、ClaudeBot、Google-Extended 等）一律允許
    lines = [
        '# All search engines and AI crawlers are welcome.',
        'User-agent: *',
        'Allow: /',
        '',
        f"Sitemap: {SITE_URL}{reverse('sitemap')}",
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')

def llms_txt(request):
    pages = [{'label': PAGE_LABELS.get(name, reverse(name)), 'url': SITE_URL + reverse(name), 'en': name.endswith('_en')}
             for name in _public_pages()]
    context = {'tw_pages': [p for p in pages if not p['en']], 'en_pages': [p for p in pages if p['en']]}
    return render(request, 'llms.txt', context, content_type='text/plain; charset=utf-8')

#其他
def generic(request):
    return render(request, 'tw/generic.html')
def elements(request):
    return render(request, 'tw/elements.html')
def flying_ball(request):
    return render(request, 'tw/flying ball.html')
