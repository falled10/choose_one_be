from tortoise import models, fields

from slugify import slugify


class Poll(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, unique=True)
    slug = fields.CharField(max_length=255, unique=True)
    creator = fields.ForeignKeyField('models.User', related_name='polls', on_delete=fields.CASCADE)
    description = fields.TextField(null=True, default="")
    media_type = fields.CharField(max_length=255, default="IMAGE")
    places_number = fields.IntField(default=0)
    image = fields.CharField(max_length=500, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        table = 'polls'

    class PydanticMeta:
        exclude = ('slug', 'creator', 'created_at',)
