from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from student.models import Student
from django.contrib.auth.models import User
from attendance.models import Attendance
from attendance.api.serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["post"], url_path="submit")
    def submit(self, request):
        """
        Expected payload:
        {
            "user_id": 15,
            "status": "PRESENT" | "TIME_OUT" | ...
        }
        """

        user_id = request.data.get("user_id")
        status_value = request.data.get("status")

        if not user_id or not status_value:
            return Response({"error": "user_id and status are required."}, status=400)

        # -------------------------
        # FETCH USER
        # -------------------------
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=404)

        try:
            student = user.student_profile
        except:
            return Response({"error": "Student profile not found for this user"}, status=404)

        today = timezone.now().date()

        # -------------------------
        # CHECK IF RECORD EXISTS
        # -------------------------
        attendance = Attendance.objects.filter(student=student, date=today).first()

        # ------------------------------------------------
        # CASE 1: FIRST SCAN OF THE DAY → TIME IN
        # ------------------------------------------------
        if attendance is None:
            attendance = Attendance.objects.create(
                student=student,
                date=today,
                status=status_value,
                time_in=timezone.now().time()
            )
            return Response({
                "message": "Time-in recorded.",
                "attendance": AttendanceSerializer(attendance).data
            }, status=200)

        # ------------------------------------------------
        # CASE 2: SECOND SCAN → TIME OUT
        # ------------------------------------------------
        if attendance.time_out is None:
            attendance.time_out = timezone.now().time()
            attendance.status = status_value
            attendance.save(update_fields=["time_out", "status"])
            return Response({
                "message": "Time-out recorded.",
                "attendance": AttendanceSerializer(attendance).data
            }, status=200)

        # ------------------------------------------------
        # CASE 3: Already Time-Out
        # ------------------------------------------------
        return Response({
            "error": "Attendance already completed for today.",
            "attendance": AttendanceSerializer(attendance).data
        }, status=400)
