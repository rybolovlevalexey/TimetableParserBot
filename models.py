import peewee as pw

database = pw.SqliteDatabase("db.sqlite3")


class EducationalDirection(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    name = pw.CharField()
    year = pw.IntegerField()
    url = pw.CharField()

    class Meta:
        database = database
        order_by = "id"
        db_table = "directions"
