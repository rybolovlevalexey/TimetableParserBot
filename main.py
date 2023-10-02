import models

with models.database:
    models.database.create_tables([models.EducationalDirection])
