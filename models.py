import peewee

database = peewee.SqliteDatabase("db.sqlite3")


class EducationalDirection(peewee.Model):
    id = peewee.PrimaryKeyField(unique=True)
    name = peewee.CharField()
    year = peewee.IntegerField()
    url = peewee.CharField(max_length=512)

    class Meta:
        database = database
        order_by = "id"
        db_table = "directions"
