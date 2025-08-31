import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nom du produit')
    category = django_filters.ModelChoiceFilter(queryset=Product.objects.values_list('category', flat=True).distinct(), label='Catégorie')
    team = django_filters.ModelChoiceFilter(queryset=Product.objects.values_list('team', flat=True).distinct(), label='Équipe')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Prix minimum')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Prix maximum')
    on_sale = django_filters.BooleanFilter(method='filter_on_sale', label='En promotion')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock', label='En stock')
    size = django_filters.CharFilter(method='filter_by_size', label='Taille')

    class Meta:
        model = Product
        fields = ['name', 'category', 'team', 'min_price', 'max_price', 'on_sale', 'in_stock', 'size']

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(sale_price__isnull=False)
        return queryset

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset

    def filter_by_size(self, queryset, name, value):
        if value:
            return queryset.filter(available_sizes__contains=[value])
        return queryset
