$(document).ready(function(){
    $('add_to_cart').on('click',function(e){
        e.preventDefault();
        food_id=$(this).attr('data-id');
        alert(food_id);
        url=$(this).attr('data-id');

        $ajax({
            type:'GET',
            url:url
        })

    })
});