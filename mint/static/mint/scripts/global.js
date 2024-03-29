export function countDown(dateTime){
    $('.clock').countdown(dateTime).on('update.countdown', function(event) {
        var format = '%H:%M:%S';
        if(event.offset.totalDays > 0) {
          format = '%-d day%!d ' + format;
        }
        if(event.offset.weeks > 0) {
          format = '%-w week%!w ' + format;
        }
        $(this).html(event.strftime(format));
      })
      .on('finish.countdown', function(event) {
        $(this).html('This offer has expired!')
          .parent().addClass('disabled');
          $('#email').attr('disabled', true)
          $('#sol').attr('disabled', true)
          $('#eth').attr('disabled', true)
          $('button[type="submit"]').text('Project Ended')
          $('button[type="submit"]').attr('disabled', true)

    });
}
