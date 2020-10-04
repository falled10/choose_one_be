from tortoise import fields, models


class User(models.Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    is_active = fields.BooleanField(default=False)
    username = fields.CharField(max_length=20, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)

    class PydanticMeta:
        exclude = ('is_active', 'created_at',)

    class Meta:
        table = 'users'
