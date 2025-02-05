odoo.define('caret_textile.production_generic', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var basic_fields = require('web.basic_fields');
var core = require('web.core');
var field_registry = require('web.field_registry');
var time = require('web.time');
var utils = require('web.utils');

var FieldBinaryFile = basic_fields.FieldBinaryFile;
var _t = core._t;

var FieldPdfViewer = FieldBinaryFile.extend({
    supportedFieldTypes: ['binary'],
    template: 'FieldPdfViewer',
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.PDFViewerApplication = false;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {DOMElement} iframe
     */
    _disableButtons: function (iframe) {
        if (this.mode === 'readonly') {
            $(iframe).contents().find('button#download').hide();
        }
        $(iframe).contents().find('button#openFile').hide();
    },
    /**
     * @private
     * @returns {string} the pdf viewer URI
     */
    _getURI: function () {
        var queryObj = {
            model: this.model,
            field: this.name,
            id: this.res_id,
        };
        var page = this.recordData[this.name + '_page'] || 1;
        var queryString = $.param(queryObj);
        var url = encodeURIComponent('/web/image?' + queryString);
        var viewerURL = '/web/static/lib/pdfjs/web/viewer.html?file=';
        return viewerURL + url + '#page=' + page;
    },
    /**
     * @private
     * @override
     */
    _render: function () {
        var self = this;
        var $pdfViewer = this.$('.o_form_pdf_controls').children().add(this.$('.o_pdfview_iframe'));
        var $selectUpload = this.$('.o_select_file_button').first();
        var $iFrame = this.$('.o_pdfview_iframe');

        $iFrame.on('load', function () {
            self.PDFViewerApplication = this.contentWindow.window.PDFViewerApplication;
            self._disableButtons(this);
        });
        if (this.mode === "readonly" && this.value) {
            $iFrame.attr('src', this._getURI());
        } else {
            if (this.value) {
                var binSize = utils.is_bin_size(this.value);
                $pdfViewer.removeClass('o_hidden');
                $selectUpload.addClass('o_hidden');
                if (binSize) {
                    $iFrame.attr('src', this._getURI());
                }
            } else {
                $pdfViewer.addClass('o_hidden');
                $selectUpload.removeClass('o_hidden');
            }
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     * @param {Event} ev
     */
    on_file_change: function (ev) {
        this._super.apply(this, arguments);
        if (this.PDFViewerApplication) {
            var files = ev.target.files;
            if (!files || files.length === 0) {
              return;
            }
            var file = files[0];
            // TOCheck: is there requirement to fallback on FileReader if browser don't support URL
            this.PDFViewerApplication.open(URL.createObjectURL(file), 0);
        }
    },
    /**
     * Remove the behaviour of on_save_as in FieldBinaryFile.
     *
     * @override
     * @private
     * @param {MouseEvent} ev
     */
    on_save_as: function (ev) {
        ev.stopPropagation();
    },

});


field_registry
    //.add('bullet_state', SetBulletStatus);
    //.add('mrp_time_counter', TimeCounter)
    .add('pdf_viewer', FieldPdfViewer);

});
