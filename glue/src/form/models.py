import logging
from urllib.parse import urlencode, urljoin

import feedparser
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.shortcuts import reverse

logger = logging.getLogger("django")


class Leads(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    preview = models.BooleanField(default=False)

    @classmethod
    def insert_lead(cls, name: str, email: str, preview_access: bool = False):
        """
        Insert a lead into the database.
        Args:
            name (str): The name of the lead.
            email (str): The email of the lead.
            preview_access (bool): Whether the lead has preview access or not.
        """
        try:
            res = cls.objects.create(name=name, email=email, preview=preview_access)
            res.save()
            logger.info(f"Lead inserted: {name}, {email}")
        except Exception as e:
            logger.error(f"Error inserting lead: {e}")
            return None
        return res

    @classmethod
    def get_lead_by_email(cls, email: str):
        """
        Get a lead by email.
        Args:
            email (str): The email of the lead.
        Returns:
            Leads: The lead object if found, else None.
        """
        try:
            return cls.objects.get(email=email)
        except cls.DoesNotExist:
            logger.warning(f"Lead not found: {email}")
            return None


class Feeds(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    summary = models.TextField()
    author = models.CharField(max_length=120)
    hits = models.BigIntegerField(default=0)

    def refresh_data(self):
        for u in settings.RSS_URLS:
            response = requests.get(u)
            try:
                feed = feedparser.parse(response.content)
                for entry in feed.entries:
                    article = Feeds.objects.create(title=entry.title, link="", summary="", author=entry.author)
                    base_link = reverse("form:hit", kwargs={"id": article.id})
                    article.link = urljoin(base_link, "?" + urlencode({"url": entry.link}))
                    summary = BeautifulSoup(entry.summary, "html.parser")
                    for anchor in summary.find_all("a"):
                        anchor["href"] = urljoin(base_link, "?" + urlencode({"url": anchor["href"]}))
                        anchor["target"] = "_blank"
                    article.summary = str(summary)
                    article.save()
                    logger.info(f'Create article "{entry.title}"')
            except Exception as e:
                logger.error(f"Feed reading error: {e}")


class ArticleHits(models.Model):
    "A user (Lead) has clicked on an article (Feed) link"

    lead = models.ForeignKey(Leads, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feeds, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.name} clicked on {self.feed.title} at {self.timestamp}"

    @classmethod
    def create_hit(cls, lead: Leads, feed: Feeds):
        """
        Create a hit record for a lead and a feed.
        Args:
            lead (Leads): The lead who clicked the link.
            feed (Feeds): The feed that was clicked.
        """
        try:
            res = cls.objects.create(lead=lead, feed=feed)
            res.save()
            logger.info(f"Hit created: {lead.name} clicked on {feed.title}")
        except Exception as e:
            logger.error(f"Error creating hit: {e}")
            return None
        return res
