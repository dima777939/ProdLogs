from .forms import ManePageSearchForm


def form_search(request):
    form = ManePageSearchForm(data=request.GET.get("search_text"))
    return {"form_search": form}
