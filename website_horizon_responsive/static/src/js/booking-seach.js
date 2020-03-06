$(document).ready(function(){
    
    
    $('#today').on('click',function() {
        $('#today').addClass("bg-danger border border-danger border-0")
        $('#tomorrow').removeClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "0" );
    });
    
    $('#tomorrow').on('click',function() {
        $('#today').removeClass("bg-danger border border-danger border-0")
        $('#tomorrow').addClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "1" );
    });   
    
    function search() {
        var self = this;
        var fromTime = $('#from_hour').timepicker('getTime');
        var toTime = $('#to_hour').timepicker('getTime');
        if (fromTime < toTime) {
            var start = moment().local().set('hour',fromTime.getHours()).set('minutes',fromTime.getMinutes()).set('seconds',0).set('milliseconds',0);
            var stop = moment().local().set('hour',toTime.getHours()).set('minutes',toTime.getMinutes()).set('seconds',0).set('milliseconds',0);
            var day = $('#day').attr('value');
            if( day == 1 ) {
                start.add(1, 'days');
                stop.add(1, 'days');
            }
            $.ajax({
              type: "POST",
              dataType: "json",
              contentType: 'application/json',
              url: '/booking/rooms',
              data: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    "start": start.toISOString(),
                    "end": stop.toISOString(),
                    "self_id": 0,
                },
                id: Math.floor(Math.random()*100000000),
              }),
              success: function( result ) {
                console.log(result);
                $('#room').empty().html(' ');
                $('#room').append(
                  $("<option></option>")
                    .attr("value",0)
                    .text('Selectionnez un local...')
                );
                var rooms = result.result;
                if(rooms.length > 0) {
                    $('#room').removeAttr( "disabled" )
                    for(var room_idx in rooms) {
                        var room = rooms[room_idx];
                        $('#room').append(
                          $("<option></option>")
                            .attr("value",room.id)
                            .text(room.name)
                        );
                    }    
                } else {
                    $('#room').addAttr( "disabled", true);
                }
              }
            });
        }
    }
}