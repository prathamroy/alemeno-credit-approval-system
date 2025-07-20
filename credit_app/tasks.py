import pandas as pd
from .models import Customer, Loan
from datetime import datetime
from celery import shared_task

@shared_task
def load_data():
    customer_df = pd.read_excel("customer_data.xlsx")
    loan_df = pd.read_excel("loan_data.xlsx")

    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row["Customer ID"],
            defaults={
                "first_name": row["First Name"],
                "last_name": row["Last Name"],
                "phone_number": str(row["Phone Number"]),
                "monthly_salary": row["Monthly Salary"],
                "approved_limit": row["Approved Limit"],
                "current_debt": 0.0,
            }
        )

    for _, row in loan_df.iterrows():
        try:
            customer = Customer.objects.get(customer_id=row["Customer ID"])
            Loan.objects.update_or_create(
                loan_id=row["Loan ID"],
                defaults={
                    "customer": customer,
                    "loan_amount": row["Loan Amount"],
                    "tenure": row["Tenure"],
                    "interest_rate": row["Interest Rate"],
                    "monthly_repayment": row["Monthly payment"],
                    "emis_paid_on_time": row["EMIs paid on Time"],
                    "start_date": pd.to_datetime(row["Date of Approval"]).date(),
                    "end_date": pd.to_datetime(row["End Date"]).date(),
                }
            )
        except Customer.DoesNotExist:
            continue