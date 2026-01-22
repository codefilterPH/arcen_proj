import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class QRScannerPageView(View):
    """
    Renders the client-side QR scanner page.
    Uses the browser camera (NOT the server camera).
    """

    def get(self, request, *args, **kwargs):
        return render(request, "qrscanner/qr_scan.html")

@method_decorator(csrf_exempt, name="dispatch")
class QRScanAPIView(View):
    """
    Receives QR data scanned from the client browser.
    """

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            qr_data = payload.get("qr_data")

            if not qr_data:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "QR data is required"
                    },
                    status=400
                )

            # ==================================================
            # 🔒 BUSINESS LOGIC GOES HERE
            # Examples:
            # - Attendance check-in
            # - Enrollment activation
            # - MFA bootstrap
            # - Asset verification
            # ==================================================
            print("📥 QR RECEIVED:", qr_data)

            return JsonResponse(
                {
                    "success": True,
                    "qr_data": qr_data
                }
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON payload"
                },
                status=400
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e)
                },
                status=500
            )
