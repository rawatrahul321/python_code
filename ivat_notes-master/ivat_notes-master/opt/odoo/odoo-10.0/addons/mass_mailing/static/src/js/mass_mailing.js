odoo.define('mass_mailing.mass_mailing', function (require) {

var FieldTextHtml = require('web_editor.backend').FieldTextHtml;
var KanbanRecord = require('web_kanban.Record');
var KanbanColumn = require("web_kanban.Column");
var KanbanView = require('web_kanban.KanbanView');

KanbanRecord.include({
    on_card_clicked: function (event) {
        if (this.model === 'mail.mass_mailing.campaign') {
            this.$('.oe_mailings').click();
        } else {
            this._super.apply(this, arguments);
        }
    },
});

function setMessageRead(messageId){
  $.ajax({
    type: "POST",
    url: "/same_url", // URL of OpenERP Handler
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    data: '{"jsonrpc":"2.0","method":"call","params":{"model":"mail.message","method":"set_message_read","args":[[' + messageId + '],true,true,{"default_model":false,"default_res_id":0,"default_parent_id":' + messageId + '}],"kwargs":{},"session_id":"' + sessionid + '","context":{"lang":"en_US","tz":"EST","uid":' + responseData['uid'] + '}},"id":"DBE"}',
    // script call was *not* successful
    error: function(XMLHttpRequest, textStatus, errorThrown) { 

    }, // error 
    // script call was successful 
    // data contains the JSON values returned by OpenERP 
    success: function(data){
      if (data.result && data.result.error) { // script returned error
            $('div#loginResult').text("Warning: " + data.result.error);
            $('div#loginResult').addClass("notice");
        }
        else if (data.error) { // OpenERP error
            $('div#loginResult').text("Error-Message: " + data.error.message + " | Error-Code: " + data.error.code + " | Error-Type: " + data.error.data.type);
            $('div#loginResult').addClass("error");
      } // if
      else { // successful transaction
            // do something successful!
      } //else
    } // success
  }); // ajax
};

var ajax = require('web.ajax');



ajax.jsonRpc("/some_url", 'call', {

                  'input_data' : $('#input').val(),

                     })





.then(function (data) {


         var output_data = data[‘output_data’]  
         $("#output").html(output_data);     

});

KanbanColumn.include({
    init: function () {
        this._super.apply(this, arguments);
        if (this.dataset.model === 'mail.mass_mailing') {
            this.draggable = false;
        }
    },
});

KanbanView.include({
    on_groups_started: function() {
        this._super.apply(this, arguments);
        if (this.dataset.model === 'mail.mass_mailing') {
            this.$el.find('.oe_kanban_draghandle').removeClass('oe_kanban_draghandle');
        }
    },
});

FieldTextHtml.include({
    get_datarecord: function() {
        /* Avoid extremely long URIs by whitelisting fields in the datarecord
        that get set as a get parameter */
        var datarecord = this._super();
        if (this.view.model === 'mail.mass_mailing') {
            // these fields can potentially get very long, let's remove them
            var blacklist = ['mailing_domain', 'contact_list_ids'];
            for (var k in blacklist) {
                delete datarecord[blacklist[k]];
            }
            delete datarecord[this.name];
        }
        return datarecord;
    },
});

});
