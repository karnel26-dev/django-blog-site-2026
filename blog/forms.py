from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """
    Форма создания и редактирования поста.

    Поле tags будет показано как список чекбоксов, чтобы студентам было проще
    увидеть работу ManyToManyField без дополнительных JavaScript-библиотек.
    """

    class Meta:
        model = Post
        fields = ('title', 'text', 'tags', 'image1', 'image2', 'image3')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 8}),
            'tags': forms.CheckboxSelectMultiple(),
        }
