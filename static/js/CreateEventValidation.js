  $(document).ready(function() {
        $('#event_modalform').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            fields: {
                name: {
                    validators: {
                        notEmpty: {
                            message: 'The first name is required and cannot be empty'
                        }
                    }
                },
                description: {
                    validators: {
                        notEmpty: {
                            message: 'The first name is required and cannot be empty'
                        }
                    }
                },
                address: {
                    validators: {
                        notEmpty: {
                            message: 'The first name is required and cannot be empty'
                        }
                    }
                },
                price: {
                    validators: {
                        integer: {
                            message: 'The price has to be an integer'
                        },
                        notEmpty: {
                            message: 'The price is required and cannot be empty'
                        }  
                    }
                }
            }
        });
    });