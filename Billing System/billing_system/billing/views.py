from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, Billing, BillingItem
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from decimal import Decimal

def billing_page(request):
    bill = None  # To store the bill data to be passed to the template
    if request.method == 'POST':
        # Collect form data
        customer_email = request.POST.get('customer_email')
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        paid_amount = Decimal(request.POST.get('paid_amount'))  # Ensure paid amount is a Decimal

        # Initialize variables for total calculation
        total_amount = Decimal(0)  # Ensure total amount is a Decimal
        total_tax = Decimal(0)  # To calculate total tax
        purchased_products = []

        try:
            # Loop over the product IDs and quantities
            for prod_id, qty in zip(product_ids, quantities):
                # Query product from the database using the product_id
                product = Product.objects.get(product_id=prod_id)

                # Convert product price to Decimal before multiplying with quantity
                price_per_unit = Decimal(product.price_per_unit)

                # Calculate total for this product
                total_amount += price_per_unit * int(qty)  # Ensure qty is an integer

                # Calculate tax for the product
                tax_percentage = Decimal(product.tax_percentage)  # Get tax percentage from product
                tax_amount = (price_per_unit * int(qty)) * (tax_percentage / 100)

                # Add product details to the purchased products list
                purchased_products.append({
                    'name': product.name,
                    'product_id': product.product_id,
                    'quantity': qty,
                    'total': price_per_unit * int(qty),
                    'tax_percentage': tax_percentage,
                    'tax_amount': tax_amount,
                    'total_with_tax': (price_per_unit * int(qty)) + tax_amount
                })

                # Add the tax amount to total tax
                total_tax += tax_amount

        except Product.DoesNotExist:
            # If product does not exist in the database, return an error message
            return render(request, 'billing/billing_form.html', {'error': 'Product not found'})

        # Calculate the change
        change = paid_amount - total_amount - total_tax

        # Denominations to be used for calculating change
        denominations = [2000, 500, 200, 100, 50, 20, 10, 5, 2, 1]
        change_denominations = {}
        for denomination in denominations:
            if change >= denomination:
                count = change // denomination
                change_denominations[denomination] = int(count)
                change -= denomination * count

        # Prepare the email message (HTML format)
        bill_summary = f"""
        <html>
        <body>
            <h2>Billing Summary</h2>
            <p><strong>Customer Email:</strong> {customer_email}</p>
            <table border="1" cellpadding="5">
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Product ID</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total Price</th>
                        <th>Tax %</th>
                        <th>Tax Amount</th>
                        <th>Total with Tax</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add product details in the table
        for product in purchased_products:
            bill_summary += f"""
            <tr>
                <td>{product['name']}</td>
                <td>{product['product_id']}</td>
                <td>{product['quantity']}</td>
                <td>₹{product['total']}</td>
                <td>₹{product['total']}</td>
                <td>{product['tax_percentage']}%</td>
                <td>₹{product['tax_amount']}</td>
                <td>₹{product['total_with_tax']}</td>
            </tr>
            """

        bill_summary += f"""
                </tbody>
            </table>
            <br>
            <p><strong>Total price without tax:</strong> ₹{total_amount}</p>
            <p><strong>Total tax payable:</strong> ₹{total_tax}</p>
            <p><strong>Net price of the purchased items:</strong> ₹{total_amount + total_tax}</p>
            <p><strong>Rounded down value of the purchased items net price:</strong> ₹{total_amount + total_tax - (total_amount + total_tax % 1)}</p>
            <p><strong>Balance payable to the customer:</strong> ₹{change}</p>
            <h3>Balance Denominations:</h3>
            <ul>
        """

        # Add change denominations to the email
        if not change_denominations:
            bill_summary += "<li>No change to be returned.</li>"
        else:
            for denomination, count in change_denominations.items():
                bill_summary += f"<li>₹{denomination}: {count} notes</li>"

        bill_summary += """
            </ul>
        </body>
        </html>
        """

        try:
            send_mail(
                subject="Your Invoice",
                message=bill_summary,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[customer_email],
                fail_silently=False,
                html_message=bill_summary  # Sending HTML content
            )
        except Exception as e:
            return render(request, 'billing/billing_form.html', {'error': f"Email failed to send. Error: {str(e)}"})

        # Prepare bill data to pass to the template
        bill = {
            'customer_email': customer_email,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'change': change,
            'change_denominations': change_denominations,
            'total_tax': total_tax,
            'net_price': total_amount + total_tax
        }

        # Return the response with the bill data
        return render(request, 'billing/billing_form.html', {'bill': bill})

    # If GET request, return empty form
    return render(request, 'billing/billing_form.html')

def calculate_change(available_denominations, change):
    result = {}
    for denomination in sorted(available_denominations, reverse=True):
        if change >= denomination:
            count = change // denomination
            result[denomination] = count
            change -= denomination * count
    return result
