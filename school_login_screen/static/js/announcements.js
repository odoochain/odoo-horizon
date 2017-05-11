$.ajax({
  url: "/announcements",
  type:"POST",
  contentType:"application/json",
  dataType:"json",
  data:"{}",
}).done(function( data ) {
    console.log(data);
    $.each(data.result, function(i, announcement) {
        $('<li class="mdl-list__item mdl-list__item--three-line">').append(
            $('<span class="mdl-list__item-primary-content">').append(
                announcement.author_avatar ? $('<img alt="Avatar" class="mdl-list__item-avatar">').attr("src","/web/image/res.partner/"+announcement.author_id[0]+"/image_small") : $('<i class="material-icons mdl-list__item-avatar">').text("person"),
                $('<span>').text(announcement.author_id[1]),
                $('<span class="mdl-list__item-text-body">').html(announcement.body))
        ).appendTo('.announcements-list');
    });
    
});