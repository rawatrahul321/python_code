
var ajax = require('web.ajax');



ajax.jsonRpc("/some_url", 'call', {

                  'input_data' : $('#input).val(),

                     })





.then(function (data) {


         var output_data = data[‘output_data’]  #Output from controller in form of data dictionary

         $("#output").html(output_data);     

});