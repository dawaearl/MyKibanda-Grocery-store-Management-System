var productModal = $("#productModal");
    $(function () {

        //JSON data by API call
        $.get(productListApiUrl, function (response) {
            if(response) {
                var table = '';
                $.each(response, function(index, product) {
                    table += '<tr data-id="'+ product.product_id +'" data-name="'+ product.name +'" data-unit="'+ product.uom_id +'" data-price="'+ product.price_per_unit +'">' +
                        '<td>'+ product.name +'</td>'+
                        '<td>'+ product.uom_name +'</td>'+
                        '<td>'+ product.price_per_unit +'</td>'+
                        '<td><span class="btn btn-xs btn-danger delete-product">Delete</span></td></tr>';
                });
                $("table").find('tbody').empty().html(table);
            }
        });

        // Fetch UOM data when page loads
        $.get(uomListApiUrl, function(response) {
            if(response) {
                var options = '<option value="">Select Unit</option>';
                $.each(response, function(index, uom) {
                    options += '<option value="'+ uom.uom_id +'">'+ uom.uom_name +'</option>';
                });
                $("select[name='uom_id']").html(options);
            }
        });
    });

    // Add this right after form initialization
    $("#productForm").on('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted with values:', {
            name: $('[name="name"]').val(),
            uom_id: $('[name="uom_id"]').val(),
            price_per_unit: $('[name="price_per_unit"]').val()
        });
    });

    // Save Product
    $("#saveProduct").on("click", function () {
        // Debug logging
        console.log("Form data before serialization:", $("#productForm").serialize());
        
        var data = $("#productForm").serializeArray();
        console.log("Serialized form data:", data);
        
        var requestPayload = {
            name: null,
            uom_id: null,
            price_per_unit: null
        };
        
        for (var i=0;i<data.length;++i) {
            var element = data[i];
            console.log("Processing element:", element);
            
            // Check exact field names from form
            switch(element.name) {
                case 'name':
                case 'product_name':
                    requestPayload.name = element.value;
                    break;
                case 'uom':
                case 'uom_id':
                    requestPayload.uom_id = element.value ? parseInt(element.value) : null;
                    break;
                case 'price':
                case 'price_per_unit':
                    requestPayload.price_per_unit = element.value ? parseFloat(element.value) : null;
                    break;
            }
        }
        
        console.log("Final payload:", requestPayload);
        
        // Detailed validation
        if (!requestPayload.name) {
            alert('Please enter product name');
            return;
        }
        if (!requestPayload.uom_id) {
            alert('Please select unit');
            return;
        }
        if (!requestPayload.price_per_unit) {
            alert('Please enter price');
            return;
        }
        
        callApi("POST", productSaveApiUrl, requestPayload);
    });

    $(document).on("click", ".delete-product", function (){
        var tr = $(this).closest('tr');
        var data = {
            product_id : tr.data('id')
        };
        var isDelete = confirm("Are you sure to delete "+ tr.data('name') +" item?");
        if (isDelete) {
            callApi("POST", productDeleteApiUrl, data);
        }
    });

    productModal.on('hide.bs.modal', function(){
        $("#id").val('0');
        $("#name, #unit, #price").val('');
        productModal.find('.modal-title').text('Add New Product');
    });

    productModal.on('show.bs.modal', function(){
        //JSON data by API call
        $.get(uomListApiUrl, function (response) {
            if(response) {
                var options = '<option value="">--Select--</option>';
                $.each(response, function(index, uom) {
                    options += '<option value="'+ uom.uom_id +'">'+ uom.uom_name +'</option>';
                });
                $("#uoms").empty().html(options);
            }
        });
    });