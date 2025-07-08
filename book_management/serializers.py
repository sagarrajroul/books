from rest_framework import serializers
from .models import Book, Author, Subject, Shelf, Format, Language


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name']


class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = ['name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code']


class FormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Format
        fields = ['mime_type', 'url']
class BookFilterSerializer(serializers.Serializer):
    bok_id = serializers.ListField(child=serializers.IntegerField(),required=False, allow_null=True)
    language =  serializers.ListField(child=serializers.CharField(),required=False, allow_null=True)
    meme_type = serializers.ListField(child=serializers.CharField(),required=False, allow_null=True)
    topic = serializers.ListField(child=serializers.CharField(),required=False, allow_null=True)
    author = serializers.ListField(child=serializers.CharField(),required=False, allow_null=True)
    title = serializers.ListField(child=serializers.CharField(),required=False, allow_null=True)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=25)
    order_by = serializers.CharField(required=False, default='download_count')
    order_type = serializers.ChoiceField(choices=['asc', 'desc'],required=False,default='desc')


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    bookshelves = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    formats = FormatSerializer(source='book_format_book', many=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'authors',
            'subjects',
            'bookshelves',
            'languages',
            'formats',
            'download_count'
        ]

    @staticmethod
    def get_authors(obj):
        return [author.author.name for author in obj.book_authors.all()]

    @staticmethod
    def get_subjects(obj):
        return [sub.subject.name for sub in obj.book_subjects.all()]

    @staticmethod
    def get_bookshelves(obj):
        return [shelf.shelf.name for shelf in obj.book_bookshelves.all()]

    @staticmethod
    def get_languages(obj):
        return [lang.language.code for lang in obj.book_languages.all()]
