//init neverbounce state
var auto_lookup = false;

//initialize global variables
var csrf_token_g;
var wallet_type_g;
var least_balance_g;
var slug_g;


//Handles page focus event and load event for project page
export function handleAjax(slug,mentions) {
    //mention default value is false until otherwise specified
    mentions = mentions || false;
    //sends an ajax request to verify actions
    $.ajax(
    {
        type:"GET",
        url: `/project/${slug}/check`,
        cache:false,
        timeout: 20000,
        beforeSend: function(){
            //
            $(`.action`).append(`<div class='d-flex spinner-border spinner1 text-dark position-absolute' role='status' style='right: 10%;'><span class='sr-only'>Loading...</span></div>`)
            if (mentions == true){
              $(`.checkmention`).append(`<div class='d-flex spinner-border spinner10 text-dark position-absolute' role='status' style='right: 10%;'><span class='sr-only'>Loading...</span></div>`)
            }
        },
        success: function( data ) 
        {
          console.log(data)
          function checkbuttons(state, classNameVal){
            if ((state === true) && !($(`.${classNameVal} .fa-circle-check`).length)) {
              $(`.${classNameVal} .fa-circle-exclamation`).remove()
              $(`.${classNameVal}`).append("<i class='fa-solid text-success fa-circle-check'></i>")
              }
              else if ((state === false) && !($(`.${classNameVal} .fa-circle-exclamation`).length)) {
                  $(`.${classNameVal} .fa-circle-check`).remove()
                  $(`.${classNameVal}`).append("<i class='fa-solid text-danger fa-circle-exclamation'></i>")
              }
          }
          if (data.constructor == Array || data.constructor == Object){
            checkbuttons(data.retweet_state,'checkretweet')
            checkbuttons(data.comment_state,'checkcomment')
            checkbuttons(data.mention_state,'checkmention')
            checkbuttons(data.follow_state,'checkfollow')
            checkbuttons(data.like_state,'checklike')
            checkbuttons(data.month_state,'checkmonth')
            checkbuttons(data.followers_state,'checkfollowers')
              if (mentions == true){
                checkbuttons(data.mention_state,'checkmention')
              }

          }
            
            
        },
        complete: function() {
            $(`.spinner1`).remove()
            if (mentions == true){
              $(`.spinner10`).remove()
            }
            
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('.modal-body').text(thrownError)
            $('.modal').modal('show')
        }
        })
    }


function handleInput() {
      $("#email").on('focus', function() {
        if (!auto_lookup){
          var ele = document.querySelector('#email', true)
          _nb.fields.registerListener(ele)
          auto_lookup = true;
          }
      }
      )
      $("#email").on("input", function() {
        $("#email").removeClass("is-invalid");
        $('button[type="submit"]').attr('disabled', true)
    })
      var isSolana;
      var isEthereum;
      var PublicKey = solanaWeb3.PublicKey;
      $("#sol").on("input", function() {
        $('#sol').removeClass('is-invalid')
        $('button[type="submit"]').attr('disabled', false)
        try {
            let address = $('#sol').val()
            let pubkey = new PublicKey(address)
            let  isSolana =  PublicKey.isOnCurve(pubkey.toBuffer())
            if (isSolana){
            $('.valid-feedback').text('Looks good!')
              $('#sol').removeClass('is-invalid')
              $('#sol').addClass('is-valid')
              $('button[type="submit"]').attr('disabled', false)
            } else {
              $('.invalid-feedback').text('Please enter valid wallet address')
              $('#sol').removeClass('is-valid')
              $('#sol').addClass('is-invalid') 
              $('button[type="submit"]').attr('disabled', true)
            }
            
        } catch (error) {
          $('.invalid-feedback').text('Please enter valid wallet address')
            $('#sol').removeClass('is-valid')
            $('#sol').addClass('is-invalid')
            $('button[type="submit"]').attr('disabled', true)
        }
      }
      )
      $("#eth").on("input", function() {
        $('button[type="submit"]').attr('disabled', true)
        let address = $('#eth').val()
        let isEthereum = Web3.utils.isAddress(address)
        if (isEthereum){
          $('.valid-feedback').text('Looks good!')
          $('#eth').removeClass('is-invalid')
          $('#eth').addClass('is-valid')
          $('button[type="submit"]').attr('disabled', false)
          
        } else {
          $('.invalid-feedback').text('Please enter valid wallet address')
          $('#eth').removeClass('is-valid')
          $('#eth').addClass('is-invalid')
          $('button[type="submit"]').attr('disabled', true)
          
        }
      }
      )
}
handleInput()
function checkwalletbalance(slug, csrf_token){
  $.ajax(
    {
      type: "POST",
      url: `/checkwalletbalance/${slug}`,
      cache:false,
      data: {
        'eth': $('#eth').val(),
        'sol': $('#sol').val(),
        'csrfmiddlewaretoken': `${csrf_token}`,
      },
    timeout: 20000,
    beforeSend: function(){
      $('.complete_loader').append("<div class='d-flex align-items-center spinner-border spinner9 text-dark position-absolute' role='status' style='right: 5%; top: 20px; '><span class='sr-only'>Loading...</span></div>")
      $('button[type="submit"]').attr('disabled', true)
    },
    success: function( balance ) 
        {
          let myToastEl = $('#liveToast')
          var myToast = bootstrap.Toast.getOrCreateInstance(myToastEl)
          if (balance.constructor == Array || balance.constructor == Object){
            if (wallet_type_g == 'ETH'){
              if ((balance.value) >= (least_balance_g)){
                $('#eth').removeClass('is-invalid')
                $('.valid-feedback').text(`Wallet Balance: ${balance.value} ETH`)
                $('#eth').addClass('is-valid')
                $('button[type="submit"]').attr('disabled', false)
                $('.spinner9').remove()
                submit(slug_g, csrf_token_g)
              }else{
                $('#eth').removeClass('is-valid')
                $('#eth').addClass('is-invalid')
                $('.invalid-feedback').text(`Wallet Balance: ${balance.value} ETH, Required: ${least_balance_g} ETH`)
                $('.spinner9').remove()
            }
          }
          if (wallet_type_g == 'SOL'){
            if ((balance.value) >= (least_balance_g)){
              $('#sol').removeClass('is-invalid')
              $('.valid-feedback').text(`Wallet Balance: ${balance.value} SOL`)
              $('#sol').addClass('is-valid')
              $('button[type="submit"]').attr('disabled', false)
              $('.spinner9').remove()
              submit(slug_g, csrf_token_g)
            }else{
              $('#sol').removeClass('is-valid')
              $('#sol').addClass('is-invalid')
              $('.invalid-feedback').text(`Wallet Balance: ${balance.value} SOL, Required: ${least_balance_g} SOL`)
              $('.spinner9').remove()
            }
          }
        } else{
            if (balance == 501) {
                $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>Invalid Wallet Address!!!<div></div>')
                $('button[type="submit"]').attr('disabled', true)
                $('.spinner9').remove()
                myToast.show()
                setTimeout(function () {
                $('.toast-body').empty();
                }, 6000)
            }
            
        }
        
      },
      complete: function() {

      },
      error: function (xhr, ajaxOptions, thrownError) {
        $('.modal-body').text(`${thrownError}`)
        $('.modal').modal('show')
        $('button[type="submit"]').attr('disabled', false)
        $('.spinner9').remove()
      }

    })
}

function submit(slug, csrf_token){
    $.ajax(
      {
        type:"POST",
        url: `/project/${slug}/verify`,
        cache:false,
        data: {
          'email': $('#email').val(),
          'eth': $('#eth').val(),
          'sol': $('#sol').val(),
          'csrfmiddlewaretoken': `${csrf_token}`,
        },
        timeout: 60000,
        beforeSend: function(){
          $('.complete_loader').append("<div class='d-flex align-items-center spinner-border spinner9 text-dark position-absolute' role='status' style='right: 5%; top: 20px; '><span class='sr-only'>Loading...</span></div>")
          $('button[type="submit"]').attr('disabled', true)
        },
        success: function( data ) 
        {
          let myToastEl = $('#liveToast')
          var myToast = bootstrap.Toast.getOrCreateInstance(myToastEl)
          if (data.constructor == Array || data.constructor == Object){
            if (data.like_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You liked the tweet!</div></div>')
            }
            else if (data.like_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You didnt like this  tweet!<div></div>')
            }
            if (data.follow_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You followed the user!</div></div>')
            }
            else if (data.follow_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You didnt follow the user!<div></div>')
            }
            if (data.retweet_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You retweeted the tweet!</div></div>')
            }
            else if (data.retweet_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You didnt retweet the tweet!<div></div>')
            }
            if (data.comment_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You commented on the tweet!</div></div>')
            }
            else if (data.comment_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You didnt comment on the tweet!<div></div>')
            }
            if (data.mention_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You mentioned twitter user(s) on the tweet!</div></div>')
            }else if (data.mention_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You didnt mention enough account on this tweet!')
            }
            if (data.followers_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You have the minimum number of followers!</div></div>')
            }
            else if (data.followers_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You dont have the minimum number of followers!<div></div>')
            }
            if (data.month_state == true){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>Your account met the minimum creation month requirement!</div></div>')
            }
            else if (data.month_state == false) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>Your account doesnt meet the month creation requirement!<div></div>')
            }
            $('button[type="submit"]').attr('disabled', false)
          }
          else {
            if (data == 200){
              $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>Registration complete!</div></div>')
              $('button[type="submit"]').attr('disabled', true)
              $('button[type="submit"]').text('Registered')
              $('#email').attr('disabled', true)
              $('#sol').attr('disabled', true)
              $('#eth').attr('disabled', true)
              
            } else if (data == 300) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You are already registered!!!<div></div>')
              $('button[type="submit"]').attr('disabled', true)
              $('button[type="submit"]').text('Registered')
              $('#email').attr('disabled', true)
              $('#sol').attr('disabled', true)
              $('#eth').attr('disabled', true)
            } else if (data == 501) {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>Invalid Wallet Address!!!<div></div>')
              $('button[type="submit"]').attr('disabled', true)
            
            }else if (data == 400) {
              $('#email').addClass('is-invalid')
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>Low wallet balance!!<div></div>')
              $('button[type="submit"]').attr('disabled', true)
            
            }else {
              $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>Unknown Error, Contact admin!!<div></div>')
              $('button[type="submit"]').attr('disabled', false)
            }
          }  
          myToast.show()
          setTimeout(function () {
            $('.toast-body').empty();
          }, 6000)
        },
        complete: function() {
          $('.spinner9').remove()
        },
        error: function (xhr, ajaxOptions, thrownError) {
          $('.modal-body').text(`${thrownError}`)
          $('.modal').modal('show')
          $('button[type="submit"]').attr('disabled', false)
        }
      })} 

export function assignVariables(wallet_type, least_balance, slug, csrf_token){
    wallet_type_g = wallet_type
    csrf_token_g = csrf_token
    least_balance_g = least_balance
    slug_g = slug
}
function completeForm(e){
    e.preventDefault()
    $('.complete_loader').append("<div class='d-flex align-items-center spinner-border spinner9 text-dark position-absolute' role='status' style='right: 5%; top: 20px; '><span class='sr-only'>Loading...</span></div>")
    $('button[type="submit"]').attr('disabled', true)
    if (wallet_type_g == 'ETH'){
      let address = $('#eth').val()
      let isEthereum = Web3.utils.isAddress(address)
      if (isEthereum){
        $('.spinner9').remove()
        //submit(slug_g, csrf_token_g) 
        if (least_balance_g != 0){
          checkwalletbalance(slug_g, csrf_token_g)
        }else {
          submit(slug_g, csrf_token_g)
        }
      } else {
        $('#eth').removeClass('is-valid')
        $('#eth').addClass('is-invalid')
        $('button[type="submit"]').attr('disabled', true)
        
      }
      }
      if (wallet_type_g == 'SOL') {
      try {
      let address = $('#sol').val()
      var PublicKey = solanaWeb3.PublicKey;
      let pubkey = new PublicKey(address)
      let  isSolana =  PublicKey.isOnCurve(pubkey.toBuffer())
      if (isSolana){
        $('.spinner9').remove()
        //submit(slug_g, csrf_token_g)
        if (least_balance_g != 0){
          checkwalletbalance(slug_g, csrf_token_g)
        }else {
          submit(slug_g, csrf_token_g)
        }
      } else {
        $('#sol').removeClass('is-valid')
        $('#sol').addClass('is-invalid')
        $('button[type="submit"]').attr('disabled', true)
      }
      
     } catch (error) {
        $('#sol').removeClass('is-valid')
        $('#sol').addClass('is-invalid')
        $('button[type="submit"]').attr('disabled', true)
        $('.spinner9').remove()
    }
    }
    if (wallet_type_g == 'NIL') {
      submit(slug_g, csrf_token_g)
    }
}
function completeFormHandler(){
    $('.complete_form').submit(function(e){
      e.preventDefault()
      if (!auto_lookup){
        completeForm(e)
      }else {
        //DONT PROCESS FORM
      }
  })
}
completeFormHandler()
function copyReferralHandler() {
  /* Get the text field */
  var copyText = document.getElementById("referral_link");

  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */

    /* Copy the text inside the text field */
  navigator.clipboard.writeText(copyText.value);

  /* Alert the copied text */
  $('#copyToClipboard').html("<span class='mx-2'>Copied</span><i class='fa-solid fa-clipboard-check my-2'></i>")
  $('#copyToClipboard').attr('disabled', true);
}
$('.referral_request').click(function(e){
    e.preventDefault()
    $.ajax({
      url: `/project/${slug_g}/referral`,
      type: 'POST',
      data: {
        'csrfmiddlewaretoken': csrf_token_g
      },
      beforeSend: function() {
        $('.referral_loader').append("<div class='d-flex align-items-center spinner-border spinner13 text-dark position-absolute' role='status' style='right: 5%; top: 20px; '><span class='sr-only'>Loading...</span></div>")
        $('.referral_request').attr('disabled', true)
      },
      success: function(data){
        if (data.response == 200){
          $('.referral_request').remove()
          $('.referral_loader').append(`<input type="text" class="form-control" value="${data.value}" id="referral_link" readonly><a href='https://twitter.com/intent/tweet?text=${data.value}' class="mt-3 btn btn-primary btn-block btn-large"> <span>Share </span> <i class="fa-brands fa-twitter text-white my-2"></i></a><button class="mt-3 mx-2 btn btn-secondary btn-block btn-large" id="copyToClipboard"><span class='mx-2'>Copy</span><i class="fa-solid fa-clipboard my-2"></i></button>`)
          $('#copyToClipboard').click(function(){
            copyReferralHandler()
          })
        }

      },
      error: function (thrownError) {
        $('.modal-body').text(`${thrownError}`)
        $('.modal').modal('show')
        $('.referral_request').attr('disabled', false)
      },
      complete: function() {
        $('.spinner13').remove()
      },
    })
  })
  $('#copyToClipboard').click(
    function(){
      copyReferralHandler()
    }
  )
  
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
              $('.modal-body').text(`Too many request, comfirm your email and try again later`)
              $('.modal').modal('show')
          } else {
          // Do stuff when other API errors occur
          // - Our recommendation is to hide any loaders and treat these emails the same way you would treat an Unknown email
          $('.modal-body').text(`Contact administrator`)
          $('.modal').modal('show')

          }
      }
    
      // Do stuff when input changes, (e.g. hide loader)
  });

  // Handle loading status (API request has been made)
  field.addEventListener('nb:loading', function(e) {
      // Do stuff while waiting on API response
      $('button[type="submit"]').attr('disabled', true)
      
  });

  let form = document.querySelector('.complete_form');
  form.addEventListener('nb:submit', function(e){
    e.preventDefault()
    completeForm(e)
  }
  
  )
    

  // Handle results (API call has succeeded)
  field.addEventListener('nb:result', function(e) {
      if (e.detail.result.is(_nb.settings.getAcceptedStatusCodes())) {
          // Do stuff for good email
          $('button[type="submit"]').attr('disabled', false)
          $('#sol').attr('disabled', false)
          $('#eth').attr('disabled', false)
      }
      else {
          // Do stuff for bad email
          $('button[type="submit"]').attr('disabled', true)
          $('#sol').attr('disabled', true)
          $('#eth').attr('disabled', true)
      }
  });

  // Handle soft results (fails regex; doesn't bother making API request)
  field.addEventListener('nb:soft-result', function(e) {
      // Do stuff when input doesn't even look like an email (i.e. missing @ or no .com/.net/etc...)
  });
});

