from .models import Customer, Loan
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterCustomerSerializer, CustomerSerializer
import math
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404

class ViewLoanDetail(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        customer = loan.customer
        return Response({
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age,
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "tenure": loan.tenure
        })

class ViewCustomerLoans(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)

        result = []
        for loan in loans:
            total_paid = loan.emis_paid_on_time
            repayments_left = loan.tenure - total_paid
            result.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "repayments_left": repayments_left
            })

        return Response(result)

class CreateLoanView(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        loan_amount = float(request.data.get("loan_amount"))
        interest_rate = float(request.data.get("interest_rate"))
        tenure = int(request.data.get("tenure"))

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        loans = Loan.objects.filter(customer=customer)

        if customer.current_debt > customer.approved_limit:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Customer's current debt exceeds approved limit",
                "monthly_installment": None
            })

        total_loans = loans.count()
        loans_this_year = loans.filter(start_date__year=date.today().year).count()
        on_time_ratio = 0.0
        total_volume = 0.0

        if total_loans > 0:
            on_time_ratio = sum([l.emis_paid_on_time for l in loans]) / (total_loans * tenure)
            total_volume = sum([l.loan_amount for l in loans])

        score = 0
        score += min(40, on_time_ratio * 40)
        score += max(0, 20 - total_loans * 2)
        score += min(15, loans_this_year * 5)
        score += min(25, (total_volume / customer.approved_limit) * 25)
        score = round(score)

        # EMI calculation
        r = interest_rate / (12 * 100)
        emi = loan_amount * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)
        emi = round(emi, 2)

        corrected_rate = interest_rate
        approved = False

        if score > 50:
            approved = True
        elif 30 < score <= 50:
            if interest_rate >= 12:
                approved = True
            else:
                corrected_rate = 12
        elif 10 < score <= 30:
            if interest_rate >= 16:
                approved = True
            else:
                corrected_rate = 16
        else:
            approved = False

        existing_emis = sum([l.monthly_repayment for l in loans])
        if (existing_emis + emi) > 0.5 * customer.monthly_salary:
            approved = False

        if not approved:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Loan conditions not satisfied",
                "monthly_installment": emi
            })

        start = date.today()
        end = date(start.year + (tenure // 12), start.month + (tenure % 12), start.day)
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_rate,
            monthly_repayment=emi,
            emis_paid_on_time=0,
            start_date=start,
            end_date=end
        )

        customer.current_debt += loan_amount
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan approved and created",
            "monthly_installment": emi
        })
    
class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_data = CustomerSerializer(customer).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CheckEligibilityView(APIView):
    def post(self, request):
        customer_id = request.data.get("customer_id")
        loan_amount = float(request.data.get("loan_amount"))
        interest_rate = float(request.data.get("interest_rate"))
        tenure = int(request.data.get("tenure"))

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        if customer.current_debt > customer.approved_limit:
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "corrected_interest_rate": None,
                "interest_rate": interest_rate,
                "tenure": tenure,
                "monthly_installment": None
            })

        loans = Loan.objects.filter(customer=customer)
        total_loans = loans.count()
        loans_this_year = loans.filter(start_date__year=date.today().year).count()
        on_time_ratio = 0.0
        total_volume = 0.0

        if total_loans > 0:
            on_time_ratio = sum([l.emis_paid_on_time for l in loans]) / (total_loans * tenure)
            total_volume = sum([l.loan_amount for l in loans])

        score = 0
        score += min(40, on_time_ratio * 40)
        score += max(0, 20 - total_loans * 2)
        score += min(15, loans_this_year * 5)
        score += min(25, (total_volume / customer.approved_limit) * 25)
        score = round(score)

        r = interest_rate / (12 * 100)
        emi = loan_amount * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)
        emi = round(emi, 2)

        approval = False
        corrected_rate = interest_rate

        if score > 50:
            approval = True
        elif 30 < score <= 50:
            if interest_rate >= 12:
                approval = True
            else:
                corrected_rate = 12
        elif 10 < score <= 30:
            if interest_rate >= 16:
                approval = True
            else:
                corrected_rate = 16
        else:
            approval = False

        existing_emis = sum([l.monthly_repayment for l in loans])
        if (existing_emis + emi) > 0.5 * customer.monthly_salary:
            approval = False

        return Response({
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_rate,
            "tenure": tenure,
            "monthly_installment": emi
        })