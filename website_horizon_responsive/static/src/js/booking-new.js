$(document).ready(function(){
	$('#from_hour').timepicker({
        'timeFormat': 'H:i',
        'minTime': '8:00',
        'maxTime': '21:30',
    });
    $('#from_hour').on('change', function() {
        var newTime = $('#from_hour').timepicker('getTime');
        $('#to_hour').timepicker('option', 'minTime', newTime);
    });
    $('#to_hour').timepicker({
        'timeFormat': 'H:i',
        'minTime': '8:30',
        'maxTime': '22:00',
        'showDuration': true,
    });
    $('#today').on('click',function() {
        $('#today').prop( "disabled", false );
        $('#tommorow').prop( "disabled", false );
        $('#day').prop( "value", "today" );
    });
});