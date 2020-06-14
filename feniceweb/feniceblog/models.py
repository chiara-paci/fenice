from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()

from django.utils.functional import cached_property

from django.urls import reverse_lazy
from django.utils.text import slugify

from fenicemisc import functions,fields as misc_fields

from crum import get_current_user

class ArticleManager(models.Manager):
    def deserialize(self,ser):
        ser_created=functions.date_deserialize(ser["created"])
        ser_created_by=User.objects.deserialize(ser["created_by"])
        ser_last_modified_by=User.objects.deserialize(ser["last_modified_by"])
        defaults={
            "publishing_date": functions.date_deserialize(ser["publishing_date"]),
            "content": ser["content"],
            "visible": ser["visible"],
        }

        obj,created=self.update_or_create(title=ser["title"],
                                          defaults=defaults)
        if created:
            obj.created=ser_created
            obj.created_by=ser_created_by
            obj.last_modified_by=ser_last_modified_by
            obj.save()

        return obj

class Article(models.Model):
    title = models.CharField(max_length=1024,unique=True)
    content = misc_fields.CleanHtmlRichTextUploadingField()
    publishing_date = models.DateTimeField()
    visible = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,on_delete=models.PROTECT,
                                   editable=False,related_name="article_created_set", 
                                   blank=True, null=True,
                                   default=None)
    last_modified_by = models.ForeignKey(User,on_delete=models.PROTECT,
                                         editable=False,related_name="article_edited_set",
                                         blank=True, null=True,
                                         default=None)

    objects=ArticleManager()

    def __str__(self): return self.title

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if user:
            if not self.pk:
                self.created_by = user
            self.modified_by = user
        models.Model.save(self,*args, **kwargs)

    @cached_property
    def slug(self):
        return slugify(self.title)

    def get_absolute_url(self):
        #return "/magazine/article/%d-%s/" % (self.pk,slugify(self.title))
        return reverse_lazy("feniceblog:article",kwargs={"pk": self.pk, "slug": self.slug})

    def __serialize__(self):
        return {
            "title": self.title,
            "content": self.content,
            "publishing_date": functions.date_serialize(self.publishing_date),
            "visible": self.visible,
            "created": functions.date_serialize(self.created),
            "last_modified": functions.date_serialize(self.last_modified),
            "created_by": self.created_by.__serialize__(),
            "last_modified_by": self.last_modified_by.__serialize__(),
        }

