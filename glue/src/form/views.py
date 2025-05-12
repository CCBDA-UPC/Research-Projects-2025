import datetime
import logging
from urllib.parse import parse_qs, urlparse

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import HttpResponseRedirect

from .models import ArticleHits, Feeds, Leads

logger = logging.getLogger("django")


def home(request):
    if Feeds.objects.all().count() == 0:
        Feeds().refresh_data()
    feeds = Feeds.objects.all().order_by("?")[:14]
    return render(request, "form/index.html", {"feeds": feeds, "email": request.COOKIES.get("email", "")})


def signup(request):
    leads = Leads()
    lead = leads.insert_lead(request.POST["name"], request.POST["email"], request.POST["previewAccess"] == "Yes")
    if lead is None:
        status = 500
    else:
        status = 200
    response = HttpResponse("", status=status)
    expiry_date = datetime.datetime.utcnow() + datetime.timedelta(weeks=520)
    response.set_cookie("email", request.POST["email"], expires=expiry_date)
    return response


def hit(request, id):
    article = Feeds.objects.get(pk=id)
    article.hits += 1
    article.save()
    lead = Leads.get_lead_by_email(request.COOKIES.get("email"))
    if lead is not None:
        ArticleHits.create_hit(lead, article)
    url_article = parse_qs(urlparse(article.link).query).get("url", ["--missing--"])[0]
    logger.info("", {"user": request.COOKIES.get("email"), "article": url_article})
    return HttpResponseRedirect(redirect_to=request.GET.get("url", "#"))

