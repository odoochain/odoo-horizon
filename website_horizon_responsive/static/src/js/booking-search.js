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
        var query = $('#query').val();
        var day = $('#day').val();
        var start = moment().local().set('hour',0).set('minutes',0).set('seconds',0).set('milliseconds',0);
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
            $('.mobile_list').empty()
            var list = result.result;
            for(var idx in list) {
                var li = list[idx];
                $('.mobile_list').append(
                  "<li><div class='d-flex justify-content-between'><span class='pr-3'>10:00<span class='mx-1'>›</span>11:00</span><span>TEST</span><span>A021</span></div></li>"
                );
            }    
         },
        });
    });
});