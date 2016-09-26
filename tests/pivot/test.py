from django.test import TestCase

from models import ShirtSales, Store, Region
from pivot import pivot


genders = ['Boy', 'Girl']
styles = ['Tee', 'Golf', 'Fancy']
dates = ['2005-01-31',
         '2005-02-01',
         '2005-02-02',
         '2005-03-01',
         '2005-03-02',
         '2005-04-03',
         '2005-05-06']


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

        units = [12, 10, 11, 15, 13, 9, 17, 3, 7]
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
                self.assertEqual(row[dt], sum(ss.units for ss in shirt_sales if ss.style == style and unicode(ss.shipped) == dt))

        pt = pivot(ShirtSales.objects, 'shipped', 'style', 'units')

        for row in pt:
            shipped = row['shipped']
            for style in styles:
                self.assertEqual(row[style], sum(ss.units for ss in shirt_sales if unicode(ss.shipped) == unicode(shipped) and ss.style == style))

    def test_pivot_on_foreignkey(self):
        shirt_sales = ShirtSales.objects.all()

        pt = pivot(ShirtSales, 'shipped', 'store__region__name', 'units')

        for row in pt:
            shipped = row['shipped']
            for name in ['North', 'South', 'East', 'West']:
                self.assertEqual(row[name], sum(ss.units for ss in shirt_sales if unicode(ss.shipped) == unicode(shipped) and ss.store.region.name == name))

        pt = pivot(ShirtSales, 'shipped', 'store__name', 'units')

        for row in pt:
            shipped = row['shipped']
            for name in ['ABC Shirts', 'Shirt Emporium', 'Just Shirts', 'Shirts R Us', 'Shirts N More']:
                self.assertEqual(row[name], sum(ss.units for ss in shirt_sales if unicode(ss.shipped) == unicode(shipped) and ss.store.name == name))
