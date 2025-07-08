from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import Book
from .serializers import BookSerializer, BookFilterSerializer


class BookFilterAPI(APIView):
    """
    API endpoint for filtering books based on various criteria.

    Filters:
        - book_id (Gutenberg IDs)
        - language codes
        - mime types
        - title (partial, case-insensitive)
        - author name (partial, case-insensitive)
        - topic (partial, case-insensitive across subjects and bookshelves)

    Supports pagination and sorting by specified field and order.
    """

    serializer_class = BookSerializer

    @swagger_auto_schema(request_body=BookFilterSerializer)
    def post(self, request, *args, **kwargs):
        try:
            # Validate input filters
            filter_serializer = BookFilterSerializer(data=request.data)
            filter_serializer.is_valid(raise_exception=True)
            filters = filter_serializer.validated_data

            books = Book.objects.all()

            # Mapping of filters to ORM paths for exact matches
            exact_filters = {
                "book_id": "gutenberg_id__in",
                "language": "book_languages__language__code__in",
                "mime_type": "book_format_books__mime_type__in",
            }

            # Mapping of filters to ORM paths for icontains matches
            icontains_filters = {
                "title": "title__icontains",
                "author": "book_authors__author__name__icontains",
                "topic": [
                    "book_subjects__subject__name__icontains",
                    "book_bookshelves__shelf__name__icontains",
                ],
            }

            # Apply exact match filters
            for field, orm_path in exact_filters.items():
                if field in filters:
                    books = books.filter(**{orm_path: filters[field]})

            # Apply icontains (partial match) filters
            for field, orm_paths in icontains_filters.items():
                if field in filters:
                    if isinstance(orm_paths, str):
                        orm_paths = [orm_paths]

                    query = Q()
                    for value in filters[field]:
                        for orm_path in orm_paths:
                            query |= Q(**{orm_path: value})
                    books = books.filter(query)

            books = books.distinct()

            # Prefetch related objects to reduce DB queries
            books = books.prefetch_related(
                "book_authors__author",
                "book_languages__language",
                "book_subjects__subject",
                "book_bookshelves__shelf",
                "book_format_books",
            )

            # Handle ordering
            order_by_field = filters.get("order_by", "download_count")
            order_type = filters.get("order_type", "desc")

            order_prefix = "-" if order_type == "desc" else ""
            books = books.order_by(f"{order_prefix}{order_by_field}")

            # Pagination
            page_number = filters.get("page", 1)
            page_size = filters.get("page_size", 25)
            paginator = Paginator(books, page_size)
            page_obj = paginator.get_page(page_number)

            serialized_books = BookSerializer(page_obj.object_list, many=True)

            return Response({
                "total_books": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page_obj.number,
                "results": serialized_books.data
            }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
