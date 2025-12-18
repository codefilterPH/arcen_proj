from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from student.models import Student
from student.api.serializers import StudentSerializer
from schools.models import SchoolOrg
from rest_framework.pagination import PageNumberPagination
from django.db import transaction, models
import uuid


class StudentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'school').all()
    serializer_class = StudentSerializer
    pagination_class = StudentPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'student_id']

    # ------------------------------------------------------------
    # 🔹 Paginated Students by School + Filters + Search
    # ------------------------------------------------------------
    @action(detail=True, methods=['get'], url_path='students')
    def students_by_school(self, request, pk=None):
        """
        GET /api/schools/{id}/students/
        Supports pagination, search, and filters.
        """
        try:
            school = SchoolOrg.objects.get(pk=pk)
        except SchoolOrg.DoesNotExist:
            return Response({"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND)

        queryset = Student.objects.filter(school=school).select_related('user').order_by('user__last_name')

        # 🔍 Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(user__first_name__icontains=search)
                | models.Q(user__last_name__icontains=search)
                | models.Q(student_id__icontains=search)
            )

        # 🎓 Filters
        school_year = request.query_params.get('school_year')
        semester = request.query_params.get('semester')
        flight = request.query_params.get('flight')

        if school_year:
            queryset = queryset.filter(classification__name__icontains=school_year)
        if semester:
            queryset = queryset.filter(preferred_initial__icontains=semester)
        if flight:
            queryset = queryset.filter(extension_name__icontains=flight)

        # ✅ Proper Pagination (fully functional)
        paginator = self.paginator  # uses pagination_class
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # fallback if pagination disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------
    # 🔹 Bulk Add Students (unchanged)
    # ------------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='add-bulk')
    @transaction.atomic
    def add_bulk(self, request):
        school_id = request.data.get('school_id')
        user_ids = request.data.get('user_ids', [])

        if not school_id or not isinstance(user_ids, list):
            return Response({"detail": "Missing or invalid school_id/user_ids"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            school = SchoolOrg.objects.get(pk=school_id)
        except SchoolOrg.DoesNotExist:
            return Response({"detail": "Invalid school_id"}, status=status.HTTP_404_NOT_FOUND)

        created_students = []
        skipped_users = []

        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                if Student.objects.filter(user=user, school=school).exists():
                    skipped_users.append(user.username)
                    continue

                student_id = f"STD-{uuid.uuid4().hex[:8].upper()}"
                student = Student.objects.create(user=user, school=school, student_id=student_id)
                student.generate_qr_code()
                student.save()
                created_students.append(student)
            except User.DoesNotExist:
                skipped_users.append(f"UnknownID:{user_id}")

        serializer = self.get_serializer(created_students, many=True)
        return Response({
            "created_count": len(created_students),
            "skipped": skipped_users,
            "created_students": serializer.data
        }, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------
    # 🔹 Remove Student(s)
    # ------------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='remove')
    @transaction.atomic
    def remove_students(self, request):
        """
        POST /api/students/remove/
        Removes one or multiple students from a school.

        Example payload:
        {
            "school_id": 12,
            "student_ids": [45, 46, 47]
        }
        """
        school_id = request.data.get('school_id')
        student_ids = request.data.get('student_ids', [])

        if not school_id or not isinstance(student_ids, list):
            return Response(
                {"detail": "Missing or invalid 'school_id' or 'student_ids'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            school = SchoolOrg.objects.get(pk=school_id)
        except SchoolOrg.DoesNotExist:
            return Response({"detail": "Invalid school_id"}, status=status.HTTP_404_NOT_FOUND)

        # --- Fetch only students belonging to that school
        students = Student.objects.filter(id__in=student_ids, school=school)

        if not students.exists():
            return Response(
                {"detail": "No valid students found for this school."},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_count = students.count()
        deleted_usernames = [s.user.username for s in students]

        # --- Perform deletion
        students.delete()

        return Response(
            {
                "deleted_count": deleted_count,
                "deleted_students": deleted_usernames,
                "message": f"Successfully removed {deleted_count} student(s) from {school.name}."
            },
            status=status.HTTP_200_OK
        )
