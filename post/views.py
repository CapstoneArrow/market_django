from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Attachment
from .forms import PostForm
from .serializers import PostSerializer, AttachmentSerializer
from firebase_admin import db
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import JsonResponse
from django.middleware.csrf import get_token

def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post_create(self, serializer):
        post = serializer.save(author=self.request.user)
        post.sync_with_firebase()

    def post_update(self, serializer):
        post = serializer.save()
        post.update_firebase()

    def post_delete(self, instance):
        instance.remove_from_firebase()
        instance.delete()


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        attachment = serializer.save()
        attachment.sync_with_post()

    def perform_delete(self, instance):
        instance.remove_from_post()
        instance.delete()


# 게시글 생성
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            attachments = request.FILES.getlist('attachments')
            for attachment in attachments:
                Attachment.objects.create(post=post, file=attachment)
            return redirect('post:view_post', post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'post/create_post.html', {'form': form})    
    


# 게시글 수정
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        if request.method == 'POST':
            post.title = request.POST.get('title')
            post.content = request.POST.get('content')
            attachments = request.FILES.getlist('attachments')
            
            for attachment in post.attachments.all():
                attachment.file.delete()  # 실제 파일 시스템에서 삭제
                attachment.delete()
            for attachment in attachments:
                Attachment.objects.create(post=post, file=attachment)
            post.save()
            edit_post_to_firebase(post)

            return redirect('post:view_post', post_id=post.id)
        return render(request, 'post/edit_post.html', {'post': post})
    else:
        messages.error(request, "게시글 수정 권한이 없습니다.")
        return redirect('post:view_post', post_id=post.id)


# Firebase 정보 수정
def edit_post_to_firebase(post):
    # 게시글 정보 수정
    post_ref = db.reference('posts').child(post.firebase_id)
    post_ref.update({
        'title': post.title,
        'content': post.content,
        'author_id': post.author.id
    })
    
    # 게시글에 대한 첨부 파일 정보 수정
    attachments_ref = post_ref.child('attachments')
    existing_attachments = attachments_ref.get() or {}
    for key in existing_attachments:
        attachments_ref.child(key).delete()  # 기존 첨부 파일 정보 삭제
    
    for attachment in post.attachments.all():
        attachment_ref = attachments_ref.push()
        attachment_ref.set({
            'file_url': attachment.file.url,
            'file_name': attachment.file.name
        })


# 게시글 삭제
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        ref = db.reference('posts')
        ref.child(post.firebase_id).delete()
        post.delete()
    return redirect('post:post_list')

# 게시글 읽기
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post/view_post.html', {'post': post})


# 게시글 목록
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post/post_list.html', {'posts': posts})