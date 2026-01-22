from django.urls import path
from .views import QRScannerPageView, QRScanAPIView

urlpatterns = [
    # UI
    path("scan/page/", QRScannerPageView.as_view(), name="qr_scanner"),

    # API
    path("qr/scan/", QRScanAPIView.as_view(), name="scan_qr"),
]
