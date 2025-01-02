from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    product_id = models.CharField(max_length=50, unique=True)
    available_stocks = models.PositiveIntegerField()
    price_per_unit = models.FloatField()
    tax_percentage = models.FloatField()

    def __str__(self):
        return f"Product ID: {self.product_id}, Name: {self.name}, Price: {self.price_per_unit}"

class Billing(models.Model):
    customer_email = models.EmailField()
    total_amount = models.FloatField()
    paid_amount = models.FloatField()
    change = models.FloatField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill ID: {self.id} - {self.customer_email}"

class BillingItem(models.Model):
    bill = models.ForeignKey(Billing, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()  # Price after tax calculation

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
