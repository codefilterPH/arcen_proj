# from celery import shared_task
# from student.models import Student
#
# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
# def regenerate_student_qr_codes(self, force=False):
#     """
#     Ensure all students have valid QR codes.
#     Runs daily via Celery Beat.
#     """
#
#     qs = Student.objects.all().only("id", "qr_code")
#
#     updated = 0
#     for student in qs.iterator(chunk_size=200):
#         if force or not student.qr_code:
#             student.generate_qr_code(force=True)
#             student.save(update_fields=["qr_code"])
#             updated += 1
#
#     return {
#         "total_students": qs.count(),
#         "updated_qr_codes": updated,
#     }
