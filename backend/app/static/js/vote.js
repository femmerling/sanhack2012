
function vote(t_id, uid, amnt){
$.ajax({
    type: "GET",
    url: "/rating/create/"+t_id+"/"+uid+"/"+amnt,
    dataType: "json",
    success: function(res){
        $('#current-rating').width(res.width);
        $('#current-rating-result').html(res.status);
    }
});
}