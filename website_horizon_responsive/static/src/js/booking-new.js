$(document).ready(function(){
	$('#from_hour').timepicker({
        'timeFormat': 'H:i',
        'minTime': '8:00',
        'maxTime': '21:30',
    });
    
    $('#to_hour').timepicker({
        'timeFormat': 'H:i',
        'minTime': '8:30',
        'maxTime': '22:00',
        'showDuration': true,
    });
    
    $('#today').on('click',function() {
        $('#today').addClass("bg-danger border border-danger border-0")
        $('#tomorrow').removeClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "today" );
    });
    
    $('#tomorrow').on('click',function() {
        $('#today').removeClass("bg-danger border border-danger border-0")
        $('#tomorrow').addClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "tomorrow" );
    });
    
    function updateRoomList() {
        var self = this;
        var fromTime = $('#from_hour').timepicker('getTime');
        var toTime = $('#to_hour').timepicker('getTime');
        if (fromTime && toTime) {
            var start = moment(self.date).local().set('hour',fromTime.getHours()).set('minutes',fromTime.getMinutes()).set('seconds',0);
            var stop = moment(self.date).local().set('hour',toTime.getHours()).set('minutes',toTime.getMinutes()).set('seconds',0);
            $.ajax({
              url: '/booking/rooms',
              data: {
                jsonrpc: "2.0",
                method: "call",
                params: {
                    "start": start.toISOString(),
                    "end": stop.toISOString(),
                },
                id: '844108350'
              },
              success: function( result ) {
                console.log(result);
              }
            });
            
            /*
                var roomSelect = self.$('select.select-asset-id').empty().html(' ');
                for(var room_idx in rooms) {
                    var room = rooms[room_idx];
                    // add new value
                    roomSelect.append(
                      $("<option></option>")
                        .attr("value",room.id)
                        .text(room.name)
                    );
                }
                roomSelect.removeAttr( "disabled" )
        	    roomSelect.material_select();
        	    Materialize.updateTextFields();
        	    self.updateSendButton();*/
        }
    }
    
    $('#from_hour').on('change', function() {
        var fromTime = $('#from_hour').timepicker('getTime');
        var toTime = $('#to_hour').timepicker('getTime');
        $('#to_hour').timepicker('option', 'minTime', fromTime);
        if (fromTime > toTime) {
            $('#to_hour').timepicker('setTime', fromTime);
        }
        updateRoomList();
    });
    
    $('#to_hour').on('change', function() {
        updateRoomList();
    });
});