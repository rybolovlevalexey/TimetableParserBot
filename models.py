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
        db_table = "programs directions"


class GroupDirection(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    educational_program_id = pw.IntegerField()
    group_name = pw.CharField()
    url = pw.CharField()

    class Meta:
        database = database
        order_by = "id"
        db_table = "groups directions"
