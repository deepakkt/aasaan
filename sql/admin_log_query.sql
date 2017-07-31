select * from django_admin_log where content_type_id = '42' and
object_repr like 'Uyir%'

-- above, we are querying the admin log. to determine content type ID
-- go to python

-- >>> from django.contrib.admin.models import ContentType
-- >>> [(x.id, x.name) for x in ContentType.objects.all() if x.name == 'Program Schedule']
-- [(42, 'Program Schedule')]

-- in addition, action flag is 1 for insert, 2 for update and 3 for delete
