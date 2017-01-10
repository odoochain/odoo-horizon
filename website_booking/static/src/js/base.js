odoo.define('website_booking.BaseWidget', function (require) {
"use strict";

var Widget = require('web.Widget');
var data = require('web.data');

var BookingBaseWidget = Widget.extend({
    
    init:function(parent,options){
        this._super(parent);
        this.dataset = new data.DataSet(this, 'school.booking', false);
    },

    show: function(){
        this.$el.removeClass('oe_hidden');
    },
    
    hide: function(){
        this.$el.addClass('oe_hidden');
    },
    
    
});

return BookingBaseWidget;

});