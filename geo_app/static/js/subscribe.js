function subscribe() {
    var e = document.getElementById("btn_follow");
    e.setAttribute('class', 'btn btn-danger')
    e.setAttribute('onclick', 'unsubscribe()')
    e.innerHTML = 'Отписаться'
    $.ajax({
        url: "#",
        type: "post",
        data: {'action': 'follow'},
        success: function() {
            $("#subAlert").show();
            $("#subAlert").addClass('show');
        }
    });
}
function unsubscribe() {
    var e = document.getElementById("btn_follow");
    e.setAttribute('class', 'btn btn-success')
    e.setAttribute('onclick', 'subscribe()')
    e.innerHTML = 'Подписаться'
    $.ajax({
        url: "#",
        type: "post",
        data: {'action': 'unfollow'},
        success: function() {
            $("#unsubAlert").show();
            $("#unsubAlert").addClass('show');
        }
    });
}