import peewee as pw

db = pw.SqliteDatabase("db.sqlite3")


class User(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    user_full_name = pw.CharField()
    user_id = pw.CharField()
    user_login = pw.CharField()
    group_url = pw.CharField()

    class Meta:
        database = db
        order_by = "id"
        db_table = "Telegram users"


class EducationalDirection(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    name = pw.CharField()
    year = pw.IntegerField()
    url = pw.CharField()

    class Meta:
        database = db
        order_by = "id"
        db_table = "Programs directions"


class GroupDirection(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    educational_program_id = pw.IntegerField()
    group_name = pw.CharField()
    url = pw.CharField()

    class Meta:
        database = db
        order_by = "id"
        db_table = "Groups directions"
