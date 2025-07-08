from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer, BookFilterSerializer
from django.core.paginator import Paginator
from rest_framework import serializers, status


class BookFilterAPI(APIView):
    serializer_class = BookSerializer

    @swagger_auto_schema(request_body=BookFilterSerializer)
    def post(self, request, *args, **kwargs):
        try:
            serializer = BookFilterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            filters = serializer.validated_data

            books = Book.objects.all()

            # Config: field name in request -> ORM path & filter mode
            exact_filters = {
                "book_id": "gutenberg_id__in",
                "language": "book_languages__language__code__in",
                "mime_type": "book_format_books__mime_type__in"
            }

            icontains_filters = {
                "title": "title__icontains",
                "author": "book_authors__author__name__icontains",
                "topic": [
                    "book_subjects__subject__name__icontains",
                    "book_bookshelves__shelf__name__icontains"
                ]
            }

            # Apply exact match filters
            for field, orm_path in exact_filters.items():
                if field in filters:
                    books = books.filter(**{orm_path: filters[field]})

            # Apply icontains filters
            for field, orm_paths in icontains_filters.items():
                if field in filters:
                    if isinstance(orm_paths, str):
                        orm_paths = [orm_paths]
                    q_obj = Q()
                    for val in filters[field]:
                        for orm_path in orm_paths:
                            q_obj |= Q(**{orm_path: val})
                    books = books.filter(q_obj)

            books = books.distinct()
            books = books.prefetch_related(
                "book_authors__author",
                "book_languages__language",
                "book_subjects__subject",
                "book_bookshelves__shelf",
                "book_format_book",
            )

            # Ordering
            order_by = filters.get("order_by", "download_count")
            if filters.get("order_type", "desc") == "desc":
                order_by = f"-{order_by}"
            books = books.order_by(order_by)

            # Pagination
            page = filters.get("page", 1)
            page_size = filters.get("page_size", 25)
            paginator = Paginator(books, page_size)
            page_obj = paginator.get_page(page)

            serialized_books = BookSerializer(page_obj.object_list, many=True)

            return Response({
                "total_books": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page_obj.number,
                "results": serialized_books.data
            }, status=status.HTTP_200_OK)
        except Exception as ee:
            return Response({"error": str(ee)}, status=status.HTTP_400_BAD_REQUEST)
