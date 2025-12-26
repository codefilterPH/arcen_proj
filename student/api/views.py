from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from student.models import Student
from student.api.serializers import StudentSerializer
from schools.models import SchoolOrg
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from django.db import transaction, models
import uuid


class StudentPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'school').all()
    serializer_class = StudentSerializer
    pagination_class = StudentPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'student_id']

    @action(
        detail=False,
        methods=["get"],
        url_path=r"schools/(?P<school_id>[^/.]+)/students",
    )
    def students_by_school(self, request, school_id=None):
        """
        GET /api/students/schools/{id}/students/
        """

        if not school_id:
            raise NotFound("School ID is required.")

        try:
            school = SchoolOrg.objects.get(pk=school_id)
        except SchoolOrg.DoesNotExist:
            raise NotFound("School not found.")

        queryset = (
            Student.objects
            .filter(school=school)
            .select_related("user")
            .order_by("user__last_name")
        )

        # 🔍 Search
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(user__first_name__icontains=search)
                | models.Q(user__last_name__icontains=search)
                | models.Q(student_id__icontains=search)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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

    @action(
        detail=False,
        methods=["get"],
        url_path=r"schools/(?P<school_id>[^/.]+)/available",
    )
    def available_students(self, request, school_id=None):
        """
        GET /api/students/schools/{id}/available/
        Returns users NOT yet enrolled in this school.
        Uses UserProfile.__str__() for display name.
        """

        if not school_id:
            raise NotFound("School ID is required.")

        try:
            school = SchoolOrg.objects.get(pk=school_id)
        except SchoolOrg.DoesNotExist:
            raise NotFound("School not found.")

        # 🔹 IDs of users already enrolled in this school
        enrolled_user_ids = Student.objects.filter(
            school=school
        ).values_list("user_id", flat=True)

        # 🔹 Users NOT yet students of this school
        queryset = (
            User.objects
            .exclude(id__in=enrolled_user_ids)
            .select_related("userprofile")
            .order_by("last_name", "first_name")
        )

        # 🔍 Optional search
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
                | models.Q(username__icontains=search)
            )

        # 🔢 Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            data = [
                {
                    "id": u.id,
                    "full_name": (
                        str(u.userprofile)
                        if hasattr(u, "userprofile")
                        else (f"{u.first_name} {u.last_name}".strip() or u.username)
                    ),
                    "username": u.username,
                    "email": u.email,
                }
                for u in page
            ]
            return self.get_paginated_response(data)

        data = [
            {
                "id": u.id,
                "full_name": (
                    str(u.userprofile)
                    if hasattr(u, "userprofile")
                    else (f"{u.first_name} {u.last_name}".strip() or u.username)
                ),
                "username": u.username,
                "email": u.email,
            }
            for u in queryset
        ]

        return Response(data)

        # ------------------------------------------------------------
        # 🔹 Get Student Profile by ID
        # ------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
        url_path=r"get-student-profile/(?P<student_id>[^/.]+)",
    )
    def get_student_profile(self, request, student_id=None):
        """
        GET /api/students/get-student-profile/{student_id}/
        """

        student = get_object_or_404(
            Student.objects.select_related("user", "school")
            .prefetch_related("designations"),
            pk=student_id
        )

        serializer = self.get_serializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(
        detail=False,
        methods=["patch"],
        url_path=r"update-student-profile/(?P<student_id>[^/.]+)",
    )
    def update_student_profile(self, request, student_id=None):
        """
        PATCH /api/students/update-student-profile/{student_id}/
        Partially update student snapshot & status fields.
        """

        student = get_object_or_404(
            Student.objects.prefetch_related("designations"),
            pk=student_id
        )

        serializer = self.get_serializer(
            student,
            data=request.data,
            partial=True,  # 🔥 allows partial updates
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            {
                "message": "Student profile updated successfully.",
                "student": serializer.data
            },
            status=status.HTTP_200_OK
        )