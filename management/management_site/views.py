from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, AddRecordForm
from .models import Employee
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee
from django.shortcuts import get_object_or_404

# Create your views here.

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(request, username=username, password=password)
            login(request, user)

            messages.success(request, f'You have been registered successfully. Welcome {username}!')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, "register.html", {"form": form})

@login_required
def home(request):
    tenant = request.user.username
    total_employees = Employee.objects.filter(tenant_id=tenant).count()
    
    one_month_ago = timezone.now() - timedelta(days=30)
    employees_at_start = Employee.objects.filter(tenant_id=tenant, created_at__lt=one_month_ago).count()
    growth_count = total_employees - employees_at_start
   
    if employees_at_start > 0:
        growth_percentage = (growth_count / employees_at_start * 100)
    else:
        growth_percentage = 100 if growth_count > 0 else 0

    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_employees = Employee.objects.filter(tenant_id=tenant, created_at__gte=seven_days_ago).count()

    employees_by_state = list(Employee.objects.filter(tenant_id=tenant).values('state').annotate(count=Count('id')).order_by('-count')[:5])

    for state_data in employees_by_state:
        state_data['percentage'] = (state_data['count'] / total_employees * 100) if total_employees > 0 else 0

    monthly_data = []
    max_monthly_count = 0
    now = timezone.now()
    
    for i in range(5, -1, -1):
        target_month = now - relativedelta(months=i)
        month_start = target_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_end = month_start + relativedelta(months=1)

        count = Employee.objects.filter(tenant_id=tenant, created_at__gte=month_start, created_at__lt=month_end).count()
        if count > max_monthly_count:
            max_monthly_count = count
        
        monthly_data.append({
            'month': month_start.strftime('%b'),
            'count': count
        })
 
    max_monthly_count = max(max_monthly_count, 1)
    
    for data in monthly_data:
        data['percentage'] = (data['count'] / max_monthly_count * 100) if max_monthly_count > 0 else 0

    recent_employee_list = Employee.objects.filter(tenant_id=tenant).order_by('-created_at')[:5]
    
    context = {
        'total_employees': total_employees,
        'growth_count': growth_count,
        'growth_percentage': round(growth_percentage, 1),
        'employees_at_start': employees_at_start,
        'growth_new_baseline': employees_at_start == 0 and growth_count > 0,
        'recent_employees': recent_employees,
        'employees_by_state': employees_by_state,
        'monthly_data': monthly_data,
        'max_monthly_count': max_monthly_count,
        'recent_employee_list': recent_employee_list,
    }
    
    return render(request, "dashboard.html", context)

@login_required
def employee_list(request):
    tenant = request.user.username
    employees = Employee.objects.filter(tenant_id=tenant).order_by('first_name')
    return render(request, "employee_list.html", {"employees": employees})

@login_required
def employee_detail(request, pk):
    tenant = request.user.username
    employee = get_object_or_404(Employee, pk=pk, tenant_id=tenant)
    return render(request, "employee_detail.html", {"employee": employee})

@login_required
def add_employee(request):
    if request.method == "POST":
        form = AddRecordForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.tenant_id = request.user.username
            instance.save()
            messages.success(request, "Employee added successfully!")
            return redirect("employee_list")
    else:
        form = AddRecordForm()
    
    return render(request, "add_employee.html", {"form": form})

@login_required
def edit_employee(request, pk):
    tenant = request.user.username
    employee = get_object_or_404(Employee, pk=pk, tenant_id=tenant)
    if request.method == "POST":
        form = AddRecordForm(request.POST, instance=employee)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.tenant_id = tenant
            inst.save()
            messages.success(request, "Employee updated successfully!")
            return redirect("employee_detail", pk=pk)
    else:
        form = AddRecordForm(instance=employee)
    
    return render(request, "edit_employee.html", {"form": form, "employee": employee})

@csrf_exempt
@login_required
def delete_employee(request, pk):
    if request.method == "POST":
        tenant = request.user.username
        employee = get_object_or_404(Employee, pk=pk, tenant_id=tenant)
        employee.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)