# Generated by Django 2.2.1 on 2019-05-04 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the company', max_length=100, verbose_name='name')),
                ('user', models.ForeignKey(help_text='User company relationship', on_delete=django.db.models.deletion.CASCADE, related_name='companies', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.CreateModel(
            name='LotPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Lot price name', max_length=100, verbose_name='name')),
                ('duration', models.IntegerField(default=1)),
                ('duration_unit', models.CharField(choices=[('hour', 'Hour'), ('day', 'Day')], help_text='Lot reservation unit', max_length=10, verbose_name='duration_unit')),
                ('pre_paid_amount', models.DecimalField(decimal_places=2, default=0, help_text='Lot reservation pre paid amount', max_digits=6, verbose_name='pre_paid')),
                ('amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount to be paid for lot reservation based on duration', max_digits=6, verbose_name='amount')),
                ('overdue_amount', models.DecimalField(decimal_places=2, default=0, help_text="Amount to be added in total amount if reservation crossit's reservation time. Overcharge amount set based on duration", max_digits=6, verbose_name='overdue_amount')),
                ('company', models.ForeignKey(help_text='Lot price list', on_delete=django.db.models.deletion.CASCADE, related_name='lot_prices', to='parking.Company', verbose_name='company')),
            ],
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Venue name', max_length=100, verbose_name='name')),
                ('category', models.CharField(choices=[('building', 'Building'), ('lot', 'Lot'), ('floor', 'Floor')], db_index=True, help_text='Venu Category', max_length=100, verbose_name='category')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('company', models.ForeignKey(help_text='Company relationship', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='venues', to='parking.Company', verbose_name='company')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, help_text='Child parent relationship', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='parking.Venue', verbose_name='parent')),
                ('venue_price', models.OneToOneField(help_text='Venue price relationship', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='venue', to='parking.LotPrice', verbose_name='venue_price')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_from', models.DateTimeField(help_text='Reservation start date time', verbose_name='book_from')),
                ('book_to', models.DateTimeField(help_text='Reservation end date time', verbose_name='book_to')),
                ('license', models.CharField(help_text='Vehicle license number', max_length=20, verbose_name='license')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('booked', 'booked'), ('active', 'Active'), ('closed', 'Closed'), ('canceled', 'Canceled')], default='pending', help_text='Reservation status', max_length=10, verbose_name='status')),
                ('amount', models.DecimalField(decimal_places=2, default=0, help_text='Reservation amount to be paid', max_digits=6, verbose_name='amount')),
                ('overdue_amount', models.DecimalField(decimal_places=2, default=0, help_text='Late fee charges to be paid', max_digits=6, verbose_name='overdue_amount')),
                ('payment_status', models.CharField(choices=[('pending', 'Payment pending'), ('partial paid', 'Partial Paid'), ('full paid', 'Full Paid')], default='pending', help_text='Reservation payment status', max_length=20, verbose_name='payment_status')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, help_text='Final amount to be paid for reservation', max_digits=6, verbose_name='total_amount')),
                ('total_amount_paid', models.DecimalField(decimal_places=2, default=0, help_text='Final amount to be paid for reservation', max_digits=6, verbose_name='total_amount')),
                ('venue', models.ForeignKey(help_text='Venue relationship', on_delete=django.db.models.deletion.CASCADE, related_name='reservation', to='parking.Venue', verbose_name='venue')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('free', 'Free'), ('cash', 'Cash'), ('card', 'Card')], help_text='Payment method', max_length=10, verbose_name='payment_type')),
                ('amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount paid for this payment method', max_digits=6, verbose_name='amount')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Payment entry creation date', verbose_name='created')),
                ('reservation', models.ForeignKey(help_text='Payment servation relationship', on_delete=django.db.models.deletion.CASCADE, related_name='payment_history', to='parking.Reservation', verbose_name='reservation')),
            ],
        ),
    ]
