from tortoise.models import Model
from tortoise import fields


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)
    leader = fields.IntField()
    progress = fields.IntField(default=0)

    def __str__(self):
        return f'{self.id}: {self.name}'
