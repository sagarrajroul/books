from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Author(models.Model):
    birth_year = models.PositiveIntegerField(null=True)
    death_year = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=128)

    objects = models.Manager()

    class Meta:
        db_table = "books_author"


class Book(models.Model):
    download_count = models.IntegerField(null=True,validators=[MinValueValidator(0)])
    gutenberg_id = models.IntegerField(unique=True,validators=[MinValueValidator(0)])
    media_type = models.CharField(max_length=16 )
    title = models.CharField(max_length=1024,null=True,blank=True)
    objects = models.Manager()

    class Meta:
        db_table = 'books_book'

class Shelf(models.Model):
    name = models.CharField(max_length=64, unique=True)
    objects = models.Manager()

    class Meta:
        db_table = 'books_bookshelf'

class Format(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE,db_column="book_id", related_name="book_format_book")
    url = models.CharField(max_length=256)
    mime_type = models.CharField(max_length=32)
    objects = models.Manager()

    class Meta:
        db_table = 'books_format'

class Language(models.Model):
    code = models.CharField(max_length=4, unique=True)
    objects = models.Manager()

    class Meta:
        db_table = 'books_language'

class Subject(models.Model):
    name = models.CharField(max_length=256, unique=True)
    objects = models.Manager()

    class Meta:
        db_table = 'books_subject'

class BookAuthor(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE,db_column='book_id',related_name='book_authors')
    author = models.ForeignKey(Author,on_delete=models.CASCADE,db_column='author_id',related_name='author_books')
    objects = models.Manager()

    class Meta:
        db_table = 'books_book_authors'
        unique_together = (('book', 'author'),)

class BookShelves(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE,db_column='book_id',related_name='book_bookshelves')
    shelf = models.ForeignKey(Shelf,on_delete=models.CASCADE,db_column='bookshelf_id',related_name='bookshelves_shelf')
    objects = models.Manager()

    class Meta:
        db_table = 'books_book_bookshelves'
        unique_together = (('book', 'shelf'),)

class BookLanguages(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE,db_column='book_id', related_name="book_languages")
    language = models.ForeignKey(Language,on_delete=models.CASCADE,db_column='language_id',related_name="language_book")
    objects = models.Manager()

    class Meta:
        db_table = 'books_book_languages'
        unique_together = (('book', 'language'),)

class BookSubjects(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE,db_column='book_id',related_name="book_subjects")
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,db_column='subject_id',related_name="subject_book")
    objects = models.Manager()

    class Meta:
        db_table = 'books_book_subjects'
        unique_together = (('book', 'subject'),)