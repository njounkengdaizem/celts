$(document).ready(function(){

    $('input.phone-input').on('input', function(){
        let matches = $(this).val().match(/\d/g);
        let digits = matches?matches.length:0;
        if (digits == 0 || digits == 10){
            this.setCustomValidity('')
        }
        else{
            this.setCustomValidity('Please Enter a Valid Phone Number')    
            this.reportValidity()        
        }
    })

    $('#saveExit').on('click', function(){
        let username = $('#username').attr('value')
        $('#contactForm').prop('action', `/profile/${username}/emergencyContact?action=exit`)
        if (formIsValid()){
            $('#contactForm').submit()
        }
    })

    $('#saveContinue').on('click', function(){
        let username = $('#username').attr('value')
        $('#contactForm').prop('action', `/profile/${username}/emergencyContact?action=continue`)
        if (formIsValid()){
            $('#contactForm').submit()
        }
    })
    
    function formIsValid(){
        let invalidInputs = $('input').map(function(i, e){
            if (! e.checkValidity()) {
                e.reportValidity()
                return e
            }
        })
        return invalidInputs.length == 0
    }
});