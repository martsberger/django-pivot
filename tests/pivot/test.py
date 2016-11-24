from __future__ import absolute_import
from django.db.models import CharField, Func, F, Avg, DecimalField

from django.conf import settings
from django.db.models import ExpressionWrapper
from django.test import TestCase
from django.utils.encoding import force_text

from .models import ShirtSales, Store, Region
from histogram import histogram
from pivot import pivot


genders = ['Boy', 'Girl']
styles = ['Tee', 'Golf', 'Fancy']
dates = ['2004-12-24',
         '2005-01-31',
         '2005-02-01',
         '2005-02-02',
         '2005-03-01',
         '2005-03-02',
         '2005-04-03',
         '2005-05-06']
store_names = [
    'ABC Shirts',
    'Shirt Emporium',
    'Just Shirts',
    'Shirts R Us',
    'Shirts N More'
]


class DateFormat(Func):
    function = 'DATE_FORMAT'
    template = '%(function)s(%(expressions)s, "%(format)s")'

    def __init__(self, *expressions, **extra):
        strf = extra.pop('format', None)
        extra['format'] = strf.replace("%", "%%")
        extra['output_field'] = CharField()
        super(DateFormat, self).__init__(*expressions, **extra)


class StrFtime(Func):
    function = 'strftime'
    template = '%(function)s("%(format)s", %(expressions)s)'

    def __init__(self, *expressions, **extra):
        strf = extra.pop('format', None)
        extra['format'] = strf.replace("%", "%%")
        extra['output_field'] = CharField()
        super(StrFtime, self).__init__(*expressions, **extra)


class Tests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(Tests, cls).setUpClass()
        # Generate a bunch of data to pivot
        Region(name='North').save()
        Region(name='South').save()
        Region(name='East').save()
        Region(name='West').save()

        regions = list(Region.objects.all())

        Store(name='ABC Shirts', region=regions[0]).save()
        Store(name='Shirt Emporium', region=regions[1]).save()
        Store(name='Just Shirts', region=regions[2]).save()
        Store(name='Shirts R Us', region=regions[3]).save()
        Store(name='Shirts N More', region=regions[0]).save()

        units = [12, 9, 10, 15, 13, 9, 15, 3, 7]
        prices = [11.04, 13.00, 11.96, 11.27, 12.12, 13.74, 11.44, 12.63, 12.06, 13.42, 11.48]

        shirt_sales = [ShirtSales(store=store,
                                  gender=g,
                                  style=s,
                                  shipped=d)
                       for store in Store.objects.all()
                       for g in genders
                       for s in styles
                       for d in dates]

        for indx, shirt_sale in enumerate(shirt_sales):
            shirt_sale.units = units[indx % len(units)]
            shirt_sale.price = prices[indx % len(prices)]

        ShirtSales.objects.bulk_create(shirt_sales)

    def test_pivot(self):
        shirt_sales = ShirtSales.objects.all()

        pt = pivot(ShirtSales.objects.all(), 'style', 'gender', 'units')

        for row in pt:
            style = row['style']
            for gender in genders:
                self.assertEqual(row[gender], sum(ss.units for ss in shirt_sales if ss.style == style and ss.gender == gender))

    def test_pivot_on_date(self):
        shirt_sales = ShirtSales.objects.all()

        pt = pivot(ShirtSales, 'style', 'shipped', 'units')

        for row in pt:
            style = row['style']
            for dt in dates:
                self.assertEqual(row[dt], sum(ss.units for ss in shirt_sales if ss.style == style and force_text(ss.shipped) == dt))

        pt = pivot(ShirtSales.objects, 'shipped', 'style', 'units')

        for row in pt:
            shipped = row['shipped']
            for style in styles:
                self.assertEqual(row[style], sum(ss.units for ss in shirt_sales if force_text(ss.shipped) == force_text(shipped) and ss.style == style))

    def test_pivot_on_foreignkey(self):
        shirt_sales = ShirtSales.objects.all()

        pt = pivot(ShirtSales, 'shipped', 'store__region__name', 'units')

        for row in pt:
            shipped = row['shipped']
            for name in ['North', 'South', 'East', 'West']:
                self.assertEqual(row[name], sum(ss.units for ss in shirt_sales if force_text(ss.shipped) == force_text(shipped) and ss.store.region.name == name))

        pt = pivot(ShirtSales, 'shipped', 'store__name', 'units')

        for row in pt:
            shipped = row['shipped']
            for name in store_names:
                self.assertEqual(row[name], sum(ss.units for ss in shirt_sales if force_text(ss.shipped) == force_text(shipped) and ss.store.name == name))

    def test_monthly_report(self):
        if settings.BACKEND == 'mysql':
            annotations = {
                'Month': DateFormat('shipped', format='%m-%Y'),
                'date_sort': DateFormat('shipped', format='%Y-%m')
            }
        elif settings.BACKEND == 'sqlite':
            annotations = {
                'Month': StrFtime('shipped', format='%m-%Y'),
                'date_sort': StrFtime('shipped', format='%Y-%m')
            }
        else:
            return

        shirt_sales = ShirtSales.objects.annotate(**annotations).order_by('date_sort')
        monthly_report = pivot(shirt_sales, 'Month', 'store__name', 'units')

        # Get the months and assert that the order by that we sent in is respected
        months = [record['Month'] for record in monthly_report]
        month_strings = ['12-2004', '01-2005', '02-2005', '03-2005', '04-2005', '05-2005']
        self.assertEqual(months, month_strings)

        # Check that the aggregations are correct too
        for record in monthly_report:
            month, year = record['Month'].split('-')
            for name in store_names:
                self.assertEqual(record[name], sum(ss.units
                                                   for ss in shirt_sales if (int(ss.shipped.year) == int(year) and
                                                                             int(ss.shipped.month) == int(month) and
                                                                             ss.store.name == name)))

    def test_histogram(self):
        hist = histogram(ShirtSales, 'units', bins=[0, 10, 15])

        d = {
            '0': 0,
            '10': 0,
            '15': 0
        }

        for s in ShirtSales.objects.all():
            if s.units < 10:
                d['0'] += 1
            elif s.units < 15:
                d['10'] += 1
            else:
                d['15'] += 1

        self.assertEqual(hist, d)

    def test_pivot_aggregate(self):
        shirt_sales = ShirtSales.objects.all()

        data = ExpressionWrapper(F('units') * F('price'), output_field=DecimalField())
        pt = pivot(ShirtSales, 'store__region__name', 'shipped', data, Avg)

        for row in pt:
            region_name = row['store__region__name']
            for dt in (key for key in row.keys() if key != 'store__region__name'):
                spends = [ss.units * ss.price for ss in shirt_sales if force_text(ss.shipped) == force_text(dt) and ss.store.region.name == region_name]
                avg = sum(spends) / len(spends) if spends else 0
                self.assertAlmostEqual(row[dt], float(avg), places=4)
