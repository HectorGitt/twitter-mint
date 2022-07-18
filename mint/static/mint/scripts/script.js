function handleAjax(classNameVal, spinnerVal){
    $.ajax(
    {
        type:"GET",
        url: `/${classNameVal}/{{context.project_id}}`,
        timeout: 10000,
        beforeSend: function(){
            $(`.${classNameVal}`).append(`<div class='d-flex spinner-border ${spinnerVal} text-dark position-absolute' role='status' style='right: 10%;'><span class='sr-only'>Loading...</span></div>`)
            $(`.${classNameVal}`).attr('disabled', true)
        },
        success: function( data ) 
        {
            
            if ((data === 'True') && !($(`.${classNameVal} .fa-circle-check`).length)) {
            $(`.${classNameVal} .fa-circle-exclamation`).remove()
            $(`.${classNameVal}`).append("<i class='fa-solid text-success fa-circle-check'></i>")
            
            } 
            
            else if ((data === 'False') && !($(`.${classNameVal} .fa-circle-exclamation`).length)) {
                $(`.${classNameVal} .fa-circle-check`).remove()
                $(`.${classNameVal}`).append("<i class='fa-solid text-danger fa-circle-exclamation'></i>")
            }
            
        },
        complete: function() {
            $(`.${spinnerVal}`).remove()
            
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('.modal-body').text(thrownError)
            $('.modal').modal('show')
        }
        })
    }