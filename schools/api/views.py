from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from schools.models import SchoolOrg, SchoolYear
from schools.api.serializers import SchoolOrgSerializer, SchoolYearSerializer
from django.db import models
from student.models import Student
from student.api.serializers import StudentSerializer
from django.shortcuts import get_object_or_404

class SchoolYearPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class SchoolYearViewSet(viewsets.ModelViewSet):
    queryset = SchoolYear.objects.select_related('school').all().order_by('-start_date')
    serializer_class = SchoolYearSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SchoolYearPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'school__name']

    # ✅ DELETE /api/academic-years/{pk}/remove/
    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_school_year(self, request, pk=None):
        """Remove an academic year by ID"""
        try:
            year = SchoolYear.objects.get(pk=pk)
            year.delete()
            return Response({"message": "School year removed successfully."}, status=status.HTTP_204_NO_CONTENT)
        except SchoolYear.DoesNotExist:
            return Response({"detail": "School year not found."}, status=status.HTTP_404_NOT_FOUND)

    # ✅ PUT /api/academic-years/{pk}/update/
    @action(detail=True, methods=['put', 'patch'], url_path='update')
    def update_school_year(self, request, pk=None):
        """Update an existing academic year"""
        try:
            year = SchoolYear.objects.get(pk=pk)
        except SchoolYear.DoesNotExist:
            return Response({"detail": "School year not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(year, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "School year updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 Custom action to fetch academic years for a single school
    @action(detail=True, methods=['get'], url_path='school-years')
    def school_years(self, request, pk=None):
        """
        GET /api/academic-years/{school_id}/school-years/
        Return paginated academic years for a given school.
        """
        try:
            school = SchoolOrg.objects.get(pk=pk)
        except SchoolOrg.DoesNotExist:
            return Response({"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND)

        queryset = SchoolYear.objects.filter(school=school).order_by('-start_date')

        # 🔍 Optional search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        # 🔢 Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

        # 🔹 Create a new academic year for a school

    @action(detail=True, methods=['post'], url_path='add-year')
    def add_academic_year(self, request, pk=None):
        """
        POST /api/academic-years/{school_id}/add-year/
        Create a new academic year entry for the specified school.
        Expected fields:
          - name (e.g., "SY 2025-2026")
          - start_date
          - end_date
        """
        try:
            school = SchoolOrg.objects.get(pk=pk)
        except SchoolOrg.DoesNotExist:
            return Response({"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['school'] = school.id  # ensure proper linkage

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(school=school)
            return Response(
                {"message": "Academic year added successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


    # ------------------------------------------------------------
    # 🔹 CUSTOM ACTION: Retrieve school by slug
    # ------------------------------------------------------------
    @action(
        detail=False,
        methods=["get"],
        url_path=r"by-slug/(?P<slug>[-\w]+)"
    )
    def by_slug(self, request, slug=None):
        """
        GET /api/schools/by-slug/{slug}/
        """
        school = get_object_or_404(SchoolOrg, slug=slug)
        serializer = self.get_serializer(school)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Handle school creation with optional logo upload.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------
    # 🔹 UPDATE — edit school info (PUT/PATCH)
    # ------------------------------------------------------------
    def update(self, request, *args, **kwargs):
        """
        Full update (PUT) or partial update (PATCH) for an existing school.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            updated_school = serializer.save()
            return Response(
                SchoolOrgSerializer(updated_school).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Allow PATCH for partial updates
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # ------------------------------------------------------------
    # 🔹 DELETE — custom response
    # ------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        """
        Delete a school by ID with confirmation message.
        """
        instance = self.get_object()
        instance_name = instance.name
        instance.delete()
        return Response(
            {"message": f"School '{instance_name}' deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    # ------------------------------------------------------------
    # 🔹 RETRIEVE SINGLE SCHOOL (DETAIL)
    # ------------------------------------------------------------
    def retrieve(self, request, *args, **kwargs):
        """
        Get detailed school info (by ID or slug if applicable).
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------
    # # 🔹 CUSTOM ACTION: Get students for this school
    # # ------------------------------------------------------------
    # @action(detail=True, methods=['get'], url_path='students')
    # def students(self, request, pk=None):
    #     """
    #         GET /api/schools/{id}/students/
    #         Returns paginated list of students for this school.
    #         Supports filters: search, school_year, semester, flight.
    #     """
    #     try:
    #         school = self.get_object()
    #     except SchoolOrg.DoesNotExist:
    #         return Response({"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND)
    #
    #     # Base query
    #     queryset = Student.objects.filter(school=school).select_related('user').order_by('user__last_name')
    #
    #     # 🔍 Search
    #     search = request.query_params.get('search')
    #     if search:
    #         queryset = queryset.filter(
    #             models.Q(user__first_name__icontains=search) |
    #             models.Q(user__last_name__icontains=search) |
    #             models.Q(student_id__icontains=search)
    #         )
    #
    #     # 🎓 Filters
    #     school_year = request.query_params.get('school_year')
    #     semester = request.query_params.get('semester')
    #     flight = request.query_params.get('flight')
    #
    #     if school_year:
    #         queryset = queryset.filter(classification__name__icontains=school_year)
    #     if semester:
    #         queryset = queryset.filter(preferred_initial__icontains=semester)
    #     if flight:
    #         queryset = queryset.filter(extension_name__icontains=flight)
    #
    #     # 🔢 Pagination
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = StudentSerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = StudentSerializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)