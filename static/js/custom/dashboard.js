$(function () {
    //Json data by api call for order table
    $.get(orderListApiUrl, function (response) {
        if(response) {
            var table = '';
            var totalCost = 0;
            $.each(response, function(index, order) {
                totalCost += parseFloat(order.total);
                
                // Convert datetime to EAT
                var date = new Date(order.datetime);
                var options = { timeZone: 'Africa/Nairobi', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
                var dateTimeEAT = date.toLocaleString('en-US', options);

                table += '<tr>' +
                    '<td>'+ dateTimeEAT +'</td>'+
                    '<td>'+ order.order_id +'</td>'+
                    '<td>'+ order.customer_name +'</td>'+
                    '<td>'+ order.total.toFixed(2) +' Ksh</td></tr>';
            });
            table += '<tr><td colspan="3" style="text-align: end"><b>Total</b></td><td><b>'+ totalCost.toFixed(2) +' Ksh</b></td></tr>';
            $("table").find('tbody').empty().html(table);
        }
    });
});