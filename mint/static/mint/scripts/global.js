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
/**
 * Hook into field registration events
 * The nb:registered event is fired on the body every time
 * _nb.fields.registerListener is called and during page load for
 * each field auto registered.
 *
 * All `nb:` prefixed events contain a `detail` object
 * with the following params:
 *   `id` - a reference ID for the field & form
 *   `result` - a result object
 *   `error` - error object from request
 */
 document.querySelector('body').addEventListener('nb:registered', function (event) {

  // Get field using id from registered event
  let field = document.querySelector('[data-nb-id="' + event.detail.id + '"]');

  // Handle clear events (input has changed or an API error was returned)
  field.addEventListener('nb:clear', function(e) {     
    $('button[type="submit"]').attr('disabled', true) 
      // Check for errors
      if (e.detail.result && e.detail.result.isError()) {
          if (e.detail.result.isThrottled()) {
              // Do stuff when the verification is throttled
              alert('Verification is throttled');
          }
          // Do stuff when other API errors occur
          // - Our recommendation is to hide any loaders and treat these emails the same way you would treat an Unknown email
          alert('Contact an administrator for assistance');
      }
    
      // Do stuff when input changes, (e.g. hide loader)
  });

  // Handle loading status (API request has been made)
  field.addEventListener('nb:loading', function(e) {
      // Do stuff while waiting on API response
      $('button[type="submit"]').attr('disabled', true)
      
  });

  // Handle results (API call has succeeded)
  field.addEventListener('nb:result', function(e) {
      if (e.detail.result.is(_nb.settings.getAcceptedStatusCodes())) {
          // Do stuff for good email
          $('button[type="submit"]').attr('disabled', false)
          $('#sol').attr('disabled', true)
          $('#eth').attr('disabled', true)
      }
      else {
          // Do stuff for bad email
      }
  });

  // Handle soft results (fails regex; doesn't bother making API request)
  field.addEventListener('nb:soft-result', function(e) {
      // Do stuff when input doesn't even look like an email (i.e. missing @ or no .com/.net/etc...)
  });
});