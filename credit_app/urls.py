from django.urls import path
from .views import (
    RegisterCustomerView,
    CheckEligibilityView,
    CreateLoanView,
    ViewLoanDetail,
    ViewCustomerLoans
)

urlpatterns = [
    path('register', RegisterCustomerView.as_view()),
    path('check-eligibility', CheckEligibilityView.as_view()),
    path('create-loan', CreateLoanView.as_view()),
    path('view-loan/<int:loan_id>', ViewLoanDetail.as_view()),
    path('view-loans/<int:customer_id>', ViewCustomerLoans.as_view()),
]
