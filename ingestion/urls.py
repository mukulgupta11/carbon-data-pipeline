from django.urls import path
from .views import DashboardStatsView, UploadRawDataView, EmissionRecordListView, EmissionRecordDetailView, SyncConcurTravelView, ClientListView, DataSourceListView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('data-sources/', DataSourceListView.as_view(), name='datasource_list'),
    path('upload/', UploadRawDataView.as_view(), name='upload_raw_data'),
    path('sync-travel/', SyncConcurTravelView.as_view(), name='sync_travel'),
    path('records/', EmissionRecordListView.as_view(), name='record_list'),
    path('records/<uuid:pk>/', EmissionRecordDetailView.as_view(), name='record_detail'),
]
