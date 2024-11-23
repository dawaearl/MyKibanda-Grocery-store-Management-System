var productPrices = {};

$(function () {
    //Json data by api call for order table
    $.get(productListApiUrl, function (response) {
        productPrices = {}
        if(response) {
            var options = '<option value="">--Select--</option>';
            $.each(response, function(index, product) {
                options += '<option value="'+ product.product_id +'">'+ product.name +'</option>';
                productPrices[product.product_id] = product.price_per_unit;
            });
            $(".product-box").find("select").empty().html(options);
        }
    });
});

$("#addMoreButton").click(function () {
    var row = $(".product-box").html();
    $(".product-box-extra").append(row);
    $(".product-box-extra .remove-row").last().removeClass('hideit');
    $(".product-box-extra .product-price").last().text('0.0');
    $(".product-box-extra .product-qty").last().val('1');
    $(".product-box-extra .product-total").last().text('0.0');
});

$(document).on("click", ".remove-row", function (){
    $(this).closest('.row').remove();
    calculateValue();
});

$(document).on("change", ".cart-product", function (){
    var product_id = $(this).val();
    var price = productPrices[product_id];

    $(this).closest('.row').find('#product_price').val(price);
    calculateValue();
});

$(document).on("change", ".product-qty", function (e){
    calculateValue();
});

$("#saveOrder").on("click", function() {
    // Validate customer name
    var customerName = $("#customerName").val().trim();
    if (!customerName) {
        alert("Please enter customer name");
        return;
    }

    // Build order items
    var orderItems = [];
    $(".product-item").each(function() {
        var productId = $(this).find(".cart-product").val();
        var quantity = parseInt($(this).find(".product-qty").val());
        var totalPrice = parseFloat($(this).find("#item_total").val());
        
        if (productId && quantity > 0) {
            orderItems.push({
                product_id: parseInt(productId),  // Ensure integer
                quantity: quantity,
                total_price: totalPrice
            });
        }
    });

    // Validate order items
    if (orderItems.length === 0) {
        alert("Please add at least one product");
        return;
    }

    var formData = {
        customer_name: customerName,
        grand_total: parseFloat($("#product_grand_total").val()),
        order_items: orderItems
    };

    console.log("Sending order data:", formData);

    $.ajax({
        url: orderSaveApiUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log("Order saved:", response);
            alert("Order saved successfully!");
            window.location.href = '/';
        },
        error: function(xhr, status, error) {
            console.error("Server response:", xhr.responseText);
            alert("Error saving order. Please try again.");
        }
    });
});