from .models import Company

def company_context(request):
    company, _ = Company.objects.get_or_create(
        pk=1,
        defaults={"name": "Mi Empresa"}
    )
    return {
        "company": company
    }