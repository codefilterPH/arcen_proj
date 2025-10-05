from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from schools.models import SchoolOrg
from schools.api.serializers import SchoolOrgSerializer

class SchoolOrgPagination(PageNumberPagination):
    page_size = 6  # 👈 cards per page
    page_size_query_param = "page_size"
    max_page_size = 50


class SchoolOrgViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing schools/organizations.
    Supports list, retrieve, create, update, delete.
    """
    queryset = SchoolOrg.objects.all().order_by("-created_at")
    serializer_class = SchoolOrgSerializer
    permission_classes = [IsAuthenticated]

    # ✅ Add pagination + search filter
    pagination_class = SchoolOrgPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "address"]  # 👈 fields to search

    def create(self, request, *args, **kwargs):
        """
        Handle school creation with optional logo upload.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)