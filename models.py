import peewee as pw

db = pw.SqliteDatabase("db.sqlite3")


class WebUser(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    login = pw.CharField()
    group_name = pw.CharField()

    class Meta:
        database = db
        order_by = "id"
        db_table = "WebUser from Api"


class DuplicateSubject(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    subject_name = pw.CharField()
    teacher_name = pw.CharField()
    place = pw.CharField()

    class Meta:
        database = db
        order_by = "id"
        db_table = "Duplicate subjects"


class User(pw.Model):
    id = pw.PrimaryKeyField(unique=True)
    user_full_name = pw.CharField()
    user_id = pw.CharField()
    user_login = pw.CharField()
    group_url = pw.CharField(default="default_url")
    admission_year = pw.CharField(default="default_year")
    user_faculty = pw.CharField(default="default_faculty")
    group_number = pw.CharField(default="default_group_number")
    education_degree = pw.CharField(default="default_degree")
    education_program = pw.CharField(default="default_program")

    def __str__(self):
        return f"User: id-{self.user_id} user_login-{self.user_login}\n" \
               f"{self.admission_year} {self.user_faculty} {self.group_number}"

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
