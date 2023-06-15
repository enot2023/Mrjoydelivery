$(document).ready(function(){

    // add to cart
    $('.add_to_cart').on('click',function(e){
        e.preventDefault();
        food_id=$(this).attr('data-id');
        
         url=$(this).attr('data-url');
        

        $.ajax({
            type:'GET',
            url:url,
            success: function(response){
                console.log(response)
                if(response.status == 'login_required'){
                    swal(response.message,'', 'info').then(function(){
                        window.location='/login';
                    })
                }else if(response.status=='Failed'){
                        swal(response.message,'', 'error')
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    );
                    
                }
            }
        });
    })


    // place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id=$(this).attr('id');
        var qty = $(this).attr('data-qty');
        console.log(qty);
        console.log
        console.log(the_id);
        $('#'+the_id).html(qty);
    })

    // decrease cart
    $('.decrease_cart').on('click',function(e){
        e.preventDefault();
        food_id=$(this).attr('data-id');
        cart_id=$(this).attr('id');
        url=$(this).attr('data-url');
        

        $.ajax({
            type:'GET',
            url:url,
            success: function(response){
                console.log(response)
                if(response.status == 'login_required'){
                    swal(response.message,'', 'info').then(function(){
                        window.location='/login';
                    });
                }
                else if(response.status == 'Failed'){
                    swal(response.message,'', 'error')
                    console.log(response)
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    
                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total'],
                    );
                    if(window.location.pathname=='/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
                    }
                }
                
            }
        });
    })


    // delete cart item
    $('.delete_cart').on('click',function(evt){
        evt.preventDefault();
       
        cart_id=$(this).attr('data-id');
        
        url=$(this).attr('data-url');
    
        $.ajax({
            type:'GET',
            url:url,
            success: function(response){
                console.log(response)
                if(response.status == 'Failed'){
                    swal(response.message,'', 'error')
                    // console.log(response);
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    console.log(response);
                    swal(response.status,response.message,"success")

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total'],
                    );

                    removeCartItem(0, cart_id);
                    checkEmptyCart();
                }
                
            }
        })
    })

    // delete the cart element if the qtyy is0
    function removeCartItem(cartItemQty,card_id){
        if(cartItemQty<=0){
            // remove the cart item element
            document.getElementById("cart-item-"+card_id).remove()
        }
    }

    // check the card is empty
    function checkEmptyCart(){
        var cart_counter=document.getElementById('cart_counter').innerHTML
        if(cart_counter==0){
            document.getElementById("empty-cart").style.display="block";
        }
    }
    
    // apply cart amount
    function applyCartAmounts(subtotal,tax_dict,grand_total){
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#total').html(grand_total)

            for(key1 in tax_dict){
                // console.log(tax_dict[key1])
                for(key2 in tax_dict[key1]){
                    console.log(tax_dict[key1][key2])
                    $('#tax-'+key1).html(tax_dict[key1][key2])
                }
            }

        }
        
    }

    // add opening hour
    $('.add_hour').on('click',function(e){
        e.preventDefault();
        var day=document.getElementById('id_day').value
        var from_hour=document.getElementById('id_from_hour').value
        var to_hour=document.getElementById('id_to_hour').value
        var is_closed=document.getElementById('id_is_closed').checked
        var csrf_token=$('input[name=csrfmiddlewaretoken]').val()
        var url =document.getElementById('add_hour_url').value

        if(is_closed){
            is_closed='True'
            condition="day != ''"

        }else{
            is_closed='False'
            condition="day != '' && from_hour != '' && to_hour != ''"
        }

        console.log(day,from_hour,to_hour,is_closed,csrf_token)
        if(eval(condition)){
            $.ajax({
                type:'POST',
                url:url,
                data:{
                    'day':day,
                    'from_hour':from_hour,
                    'to_hour':to_hour,
                    'is_closed':is_closed,
                    'csrfmiddlewaretoken':csrf_token,
                },
                success: function(response) {
                    console.log(response);
                    if (response.status == 'Success') {
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-"response.id><td><b>' + response.day + '</b></td><td>Closed</td><td><a href="#" class="removed_hour" data-url="/vendor/opening-hours/remove/'+response+'/">Remove</a></td></tr>';
                        }else{
                            var html = '<tr id="hour-"response.id><td><b>' + response.day + '</b></td><td>' + response.from_hour + ' - ' + response.to_hour + '</td><td><a href="#" class="removed_hour" data-url="/vendor/opening-hours/remove/'+response+'/">Remove</a></td></tr>';

                        }
                        $(".opening_hours").append(html);
                        document.getElementById("opening_hours").reset();
                    } else {
                        swal(response.message, '', 'error');
                    }
                }
                
            })
            
        }
        else{
            swal('please fill all the fields', '','info')
        }
        

    })

    // removed opening hour

    $(document).on('click','.remove_hour',function(e){
        e.preventDefault();

        url=$(this).attr('data-url');

        $.ajax({
            type:'GET',
            url:url,
            success: function(response) {
                if (response.status =='Success') {
                        document.getElementById('hour-' +response.id).remove();
                }
            }
        })
    })

});
