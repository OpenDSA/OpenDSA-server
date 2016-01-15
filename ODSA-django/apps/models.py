"""
Plugins and tabs make it possible to customize the behavior and appearance of pages in this
system. Plugins are rendered as small "boxes" on the side of a page, where tabs have their own
pages which can be accessed through a tab-like user interface.

To be able to add tabs and plugins to a Model, the model must inherit 'ModelWithPlugins' class.
Superclasses Tab and Plugin are related to ModelWithPlugin Models through foreign key relations.
Other plugin and tab classes inherit the properties in the super classes.

All tabs and plugins have a method 'render' which is called when the contents of that model
should be displayed. This method should be defined in each subclass.
"""

# Python
import feedparser
import urlparse
import urllib2
import cookielib
import datetime

# Django
from django.db import models
from django.core.cache import cache
from django.template import loader
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

# A+
from inheritance.models import ModelWithInheritance
from oauth_provider.models import Consumer
from lib.BeautifulSoup import BeautifulSoup

class AbstractApp(ModelWithInheritance):

    # Generic foreign key implementation from Django commenting framework
    container_type      = models.ForeignKey(ContentType)
    container_pk        = models.TextField(_('object ID'))
    container           = generic.GenericForeignKey(ct_field="container_type", fk_field="container_pk")


    # A Plugin can be tied to an OAuth consumer, which makes it possible to sign requests
    # with secret keys between this service and the consumer service.
    oauth_consumer      = models.ForeignKey(Consumer, null=True, blank=True)

    class Meta:
        abstract        = True

class BaseTab(AbstractApp):
    # Label is the word displayed on the tab
    label               = models.CharField(max_length=12)

    # Title is displayed on the top of the tab page
    title               = models.CharField(max_length=64)
    order               = models.IntegerField(default=100)

    # A Tab can be opened in a new window, in the same window,
    opening_method      = models.CharField(max_length=32, blank=True)

    def render(self):
        return "No content for this tab..."

    def get_absolute_url(self):
        return reverse("plugins.views.view_tab", kwargs={"tab_id": self.id})

    def get_label(self):
        return self.label

    def __unicode__(self):
        return self.label

    def get_container(self):
        return self.container.as_leaf_class()

    class Meta:
        ordering        = ['order', 'id']

class HTMLTab(BaseTab):
    content             = models.TextField()

    def render(self):
        return self.content

class ExternalTab(BaseTab):
    content_url         = models.URLField(max_length=128)

class EmbeddedTab(BaseTab):
    content_url         = models.URLField(max_length=128)
    element_id          = models.CharField(max_length=32, blank=True)

    def render(self):
        content         =  cache.get(self.content_url)

        # If the page is not cached, retrieve it
        if content == None:
            opener      = urllib2.build_opener()
            content     = opener.open(self.content_url, timeout=5).read()

            # Save the page in cache
            cache.set(self.content_url, content)

        soup            = BeautifulSoup(content)

        # Make links absolute, quoted from http://stackoverflow.com/a/4468467:
        for tag in soup.findAll('a', href=True):
            tag['href'] = urlparse.urljoin(self.content_url, tag['href'])

        # If there's no element specified, use the BODY.
        # Otherwise find the element with given id.
        if self.element_id == "":
            html        = soup.find("body").renderContents()
        else:
            html        = str(soup.find(id=self.element_id))

        return html

class BasePlugin(AbstractApp):
    title               = models.CharField(max_length=64)

    def render(self):
        leaf = self.as_leaf_class()
        if leaf != self:
            return leaf.render()
        else:
            return "<strong>Base plug-in does not have a render-method.</strong>"

class RSSPlugin(BasePlugin):
    feed_url                = models.URLField(max_length=256, blank=False)

    def render(self):
        doc             = feedparser.parse(self.feed_url)
        feed            = doc.feed

        sorted_entries  = sorted(doc["entries"], key=lambda entry: entry.date_parsed)
        sorted_entries.reverse()
        sorted_entries  = sorted_entries[:5]

        # Set timestamps in a format that Django knows how to handle in templates
        for entry in sorted_entries:
            entry.django_timestamp = datetime.datetime(*entry.date_parsed[:7])

        out             = loader.render_to_string("plugins/rss.html",
                                                  {"entries": sorted_entries,
                                                   "title": self.title,
                                                   "feed": feed,
                                                   "plugin": self})
        return out

class IFramePlugin(BasePlugin):
    pass

class EmbeddedPlugin(BasePlugin):
    pass

class HTMLPlugin(BasePlugin):
    content = models.TextField(blank=False)

    def render(self):
        return mark_safe(self.content)

class ChatPlugin(BasePlugin):
    pass
