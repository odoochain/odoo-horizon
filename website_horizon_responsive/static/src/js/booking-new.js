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
        $('#today').addClass("bg-danger border border-danger border-0")
        $('#tomorrow').removeClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "today" );
    });
    $('#tomorrow').on('click',function() {
        $('#today').removeClass("bg-danger border border-danger border-0")
        $('#tomorrow').addClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "tomorrow" );
    });
});