from django.db import models
from django.conf import settings
from firebase_admin import db, initialize_app

try:
    initialize_app()
except ValueError:
    pass


class Post(models.Model):
    firebase_id = models.CharField(max_length=255, unique=True, null=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.firebase_id:
            self.sync_with_firebase()
        else:
            self.update_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_with_firebase(self):
        ref = db.reference('posts').push()
        ref.set({
            'title': self.title,
            'content': self.content,
            'author_id': self.author.id
        })
        self.firebase_id = ref.key
        super().save(update_fields=['firebase_id'])

    def update_firebase(self):
        ref = db.reference('posts').child(self.firebase_id)
        ref.update({
            'title': self.title,
            'content': self.content,
            'author_id': self.author.id
        })

    def remove_from_firebase(self):
        ref = db.reference('posts').child(self.firebase_id)
        ref.delete()


class Attachment(models.Model):
    post = models.ForeignKey(Post, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_with_post()

    def delete(self, *args, **kwargs):
        self.remove_from_post()
        super().delete(*args, **kwargs)

    def sync_with_post(self):
        ref = db.reference('posts').child(self.post.firebase_id).child('attachments').push()
        ref.set({
            'file_url': self.file.url,
            'file_name': self.file.name
        })

    def remove_from_post(self):
        attachments_ref = db.reference('posts').child(self.post.firebase_id).child('attachments')
        query = attachments_ref.order_by_child('file_name').equal_to(self.file.name)
        for snapshot in query.get().items():
            attachments_ref.child(snapshot.key).delete()