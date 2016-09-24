from django.test import TestCase

from models import ShirtSales
from pivot import pivot


class Tests(TestCase):

    def test_pivot(self):
        # Generate a bunch of data and pivot it
        regions = ['North', 'East', 'South', 'West', 'Foreign']
        genders = ['Boy', 'Girl']
        styles = ['Tee', 'Golf', 'Fancy']
        dates = ['2005-01-31',
                 '2005-02-01',
                 '2005-02-02',
                 '2005-03-01',
                 '2005-03-02',
                 '2005-04-03',
                 '2005-05-06']
        units = [12, 10, 11, 15, 13, 9, 17, 3, 7]
        prices = [11.04, 13.00, 11.96, 11.27, 12.12, 13.74, 11.44, 12.63, 12.06, 13.42, 11.48]

        shirt_sales = [ShirtSales(region=r,
                                  gender=g,
                                  style=s,
                                  shipped=d)
                       for r in regions
                       for g in genders
                       for s in styles
                       for d in dates]

        for indx, shirt_sale in enumerate(shirt_sales):
            shirt_sale.units = units[indx % len(units)]
            shirt_sale.price = prices[indx % len(prices)]

        ShirtSales.objects.bulk_create(shirt_sales)

        pt = pivot(ShirtSales.objects.all(), 'region', 'gender', 'units')

        for row in pt:
            region = row['region']
            for gender in genders:
                self.assertEqual(row[gender], sum(ss.units for ss in shirt_sales if ss.region == region and ss.gender == gender))

        pt = pivot(ShirtSales, 'region', 'shipped', 'units')

        for row in pt:
            region = row['region']
            for dt in dates:
                self.assertEqual(row[dt], sum(ss.units for ss in shirt_sales if ss.region == region and unicode(ss.shipped) == dt))