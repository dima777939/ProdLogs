from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
from orders.models import Order, OrderLog
from .forms import ManePageSearchForm, AdvancedSearchForm
from .services import Search, AdvancedSearch, ExportExcel


class BaseSearchView(LoginRequiredMixin, ListView):
    template_name = "search/search.html"
    paginate_by = 10
    context_object_name = "result_search"
    search_form = ManePageSearchForm
    advanced_form_search = AdvancedSearchForm
    type_search = "search_for_order"
    len_queryset = None

    def get_form(self, *args, **kwargs):
        form = self.search_form(data=self.request.GET)
        if form.is_valid():
            return form.cleaned_data

    def get_queryset(self):
        search = Search()
        cd = self.get_form()
        search_text = cd["search_text"]
        if self.request.user.is_staff:
            result_search = search.search_for_orderlog(search_text)
            self.type_search = "search_for_orderlog"
        else:
            result_search = search.search_for_order(search_text)
        self.len_queryset = len(result_search)
        return result_search

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BaseSearchView, self).get_context_data()
        context["advanced_form_search"] = self.advanced_form_search()
        context["search_query"] = self.request.GET
        context["form_search"] = self.search_form(data=self.request.GET)
        context["len_queryset"] = self.len_queryset
        context["type_search"] = self.type_search
        return context


class AdvancedSearchListView(LoginRequiredMixin, ListView):
    template_name = "search/search.html"
    search_form = AdvancedSearchForm
    paginate_by = 10
    context_object_name = "result_search"
    advanced_form_search = AdvancedSearchForm
    type_search = "search_for_order"
    len_queryset = None
    export_to = "page"

    def get_form(self, *args, **kwargs):
        form = self.search_form(data=self.request.GET)
        if form.is_valid():
            return form.cleaned_data

    def get_queryset(self):
        cd = self.get_form()
        if cd:
            search = AdvancedSearch(cd)
            queryset = search.get_orders_filter(self.export_to)
            self.type_search = (
                "search_for_orderlog"
                if cd["operation"]
                or cd["operator"]
                or cd["start_date"]
                or cd["end_date"]
                else "search_for_order"
            )
            self.len_queryset = len(queryset)
            return queryset
        queryset = OrderLog.objects.all()[:100]
        self.len_queryset = len(queryset)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AdvancedSearchListView, self).get_context_data()
        context["advanced_form_search"] = self.search_form(data=self.request.GET)
        context["len_queryset"] = self.len_queryset
        context["type_search"] = self.type_search
        return context


class ExportExcelView(PermissionRequiredMixin, AdvancedSearchListView, ExportExcel):
    export_to = "file"
    permission_required = "orders.add_order"

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response = self.get_excel_response(queryset)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        pass
