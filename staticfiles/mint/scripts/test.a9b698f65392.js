$('.checklike').click(function(){
    $.ajax(
    {
        type:"GET",
        url: "/checklike/{{context.project_id}}",
        timeout:10000,
        beforeSend: function(){
          $('[aria-controls="collapseTwo"]').append("<div class='d-flex spinner-border spinner2 text-dark position-absolute' role='status' style='right: 10%;'><span class='sr-only'>Loading...</span></div>")
          $('[aria-controls="collapseTwo"]').attr('disabled', true)
        },
        success: function( data ) 
        {
          
          if (data === 'True') {
            $('.tooltipTwo').attr('title','You have liked the tweet').tooltip('update').tooltip('show');
            setTimeout(function () {
              $('.tooltipTwo').tooltip('dispose');
            }, 2000)
            
          } 
          
          else if (data === 'False'){
            $('.tooltipTwo').attr('title', 'You havent liked the tweet').tooltip('update').tooltip('show');
            setTimeout(function () {
              $('.tooltipTwo').tooltip('dispose');
            }, 2000)
            
          }

            
        },
        complete: function(){
                        $('.spinner2').remove()
          $('[aria-controls="collapseTwo"]').attr('disabled', false)
          
        },
        error: function (xhr, ajaxOptions, thrownError) {
          $('.modal-body').text(thrownError)
          $('.modal').modal('show')
        }
      })
    });
$('.checkfollow').click(function(){
      
    $.ajax(
    {
        type:"GET",
        url: "/checkfollow/{{context.project_id}}",
        timeout: 10000,
        beforeSend: function(){
        $('[aria-controls="collapseOne"]').append("<div class='d-flex spinner-border spinner1 text-dark position-absolute' role='status' style='right: 10%;'><span class='sr-only'>Loading...</span></div>")
        $('[aria-controls="collapseOne"]').attr('disabled', true)
        },
        success: function( data ) 
        {
        
        if (data === 'True') {
            $('.tooltipOne').attr('title','You have followed this user').tooltip('update').tooltip('show');
            
            setTimeout(function () {
            $('.tooltipOne').tooltip('dispose');
            }, 2000)
            
        } 
        
        else if (data === 'False'){
            $('.tooltipOne').attr('title', 'You havent followed this user').tooltip('update').tooltip('show');
            setTimeout(function () {
            $('.tooltipOne').tooltip('dispose');
            }, 2000)
            
        }
            
        },
        complete: function() {
        $('.spinner1').remove()
        $('[aria-controls="collapseOne"]').attr('disabled', false)
        },
        error: function (xhr, ajaxOptions, thrownError) {
        $('.modal-body').text(thrownError)
        $('.modal').modal('show')
        }
    })
});

$('.checkretweet').click(function(){
        
    $.ajax(
    {
        type:"GET",
        url: "/checkretweet/{{context.project_id}}",
        timeout:10000,
        beforeSend: function(){
            $('[aria-controls="collapseThree"]').append("<div class='d-flex spinner-border spinner3 text-dark position-absolute' role='status' style='right: 10%;'><span class='sr-only'>Loading...</span></div>")
            $('[aria-controls="collapseThree"]').attr('disabled', true)
        },
        success: function( data ) 
        {
            
            if (data === 'True') {
            $('.tooltipThree').attr('title','You have retweeted this tweet').tooltip('update').tooltip('show');
            setTimeout(function () {
                $('.tooltipThree').tooltip('dispose');
            }, 2000)
            
            } 
            
            else if (data === 'False'){
            $('.tooltipThree').attr('title', 'You havent retweeted this tweet').tooltip('update').tooltip('show');
            setTimeout(function () {
                $('.tooltipThree').tooltip('dispose');
            }, 2000)
            
            }
            
            
        },
        complete: function() {
            $('.spinner3').remove()
            $('[aria-controls="collapseThree"]').attr('disabled', false)
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('.modal-body').text(thrownError)
            $('.modal').modal('show')
        },
        })
    });
$('.complete_form').submit(function(e){
    e.preventDefault();
    $.ajax(
    {
        type:"POST",
        url: "/project/{{context.project_id}}/verify",
        data: {
        'email': $('#email').val(),
        'eth': $('#eth').val(),
        'sol': $('#sol').val(),
        'csrfmiddlewaretoken': '{{ csrf_token }}',
        },
        timeout: 25000,
        beforeSend: function(){
        $('.complete_loader').append("<div class='d-flex align-items-center spinner-border spinner9 text-dark position-absolute' role='status' style='right: 5%; top: 20px; '><span class='sr-only'>Loading...</span></div>")
        $('button[type="submit"]').attr('disabled', true)
        },
        success: function( data ) 
        {
        myToastEl = $('#liveToast')
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
            if (data.followers_state == true){
            $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>You have the minimum number of followers!</div></div>')
            }
            else if (data.followers_state == false) {
            $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You dont have the minimum number of followers!<div></div>')
            }
            if (data.followers_state == true){
            $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>Your account met the minimum creation month requirement!</div></div>')
            }
            else if (data.followers_state == false) {
            $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>Your account doesnt meet the month creation requirement!<div></div>')
            }
            $('button[type="submit"]').attr('disabled', false)
        }
        else {
            console.log(data)
            if (data == 290){
            $('.toast-body').append('<div class=" container-fluid alert alert-success d-flex align-items-center" role="alert"><svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:"><use xlink:href="#check-circle-fill"/></svg><div>Registration complete!</div></div>')
            $('button[type="submit"]').attr('disabled', true)
            $('button[type="submit"]').text('Registered')
            
            } else if (data == 300) {
            $('.toast-body').append('<div class="alert alert-danger d-flex align-items-center" role="alert" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg><div>You are already registered!!!<div></div>')
            $('button[type="submit"]').attr('disabled', true)
            $('button[type="submit"]').text('Registered')
            } else {
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
        $('.modal-body').text(thrownError)
        $('.modal').modal('show')
        $('button[type="submit"]').attr('disabled', false)
        }
    })
})
    