/* global $, moment */

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
    
    $('#search-booking').on('click',function() {
        var self = this;
        var query = $('#query').attr('value');
        var day = $('#day').attr('value');
        var start = moment().local().set('hour',0).set('minutes',fromTime.getMinutes()).set('seconds',0).set('milliseconds',0);
        var stop = moment().local().set('hour',23).set('minutes',59).set('seconds',59).set('milliseconds',0);
        if( day == 1 ) {
            start.add(1, 'days');
            stop.add(1, 'days');
        }
        $.ajax({
          type: "POST",
          dataType: "json",
          contentType: 'application/json',
          url: '/booking/search',
          data: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: {
                "start": start.toISOString(),
                "end": stop.toISOString(),
                "query": query,
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
         },
        });
    });
});