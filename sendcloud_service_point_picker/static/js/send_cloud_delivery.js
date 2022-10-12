odoo.define('sendcloud_service_point_picker.checkout', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    /* Handle interactive carrier choice + cart update */
    var $pay_button = $('#o_payment_form_pay');
    var $servicePointbtn = $('a[id^="open_sendcloud_service_point"]');
    var is_service_point = false;
    var delivery_line = false;

    var prepare_address = function(pointObject) {
        return '<br /> <div class="o_service_point_address"> <span style="font-weight:bold">'+ pointObject.name +'</span>' +
               '<a href="#" class="btn btn-default o_clear_service_point" style="color:black" title="Remove Service Point"><i class="fa fa-times-circle"></i> </a>' +
               '<br /> <span>' + pointObject.street + ',' + pointObject.house_number + '</span>' +
               '<br /> <span>' + pointObject.postal_code + '</span>' +
               '<br /> <span>' + pointObject.city +'</span> </div>'
    };

    var _writeDataSaleOrder = function (order_id, vals) {
        ajax.jsonRpc("/web/dataset/call_kw", 'call', {
                model: 'sale.order',
                method: 'write',
                args: [order_id,vals],
                kwargs: {}
            });
    };


    var _openSendCloudServicePointMap = function(sendcloud_details) {
        var config = {
          apiKey: sendcloud_details['key'],
          country: sendcloud_details['country_code'],
          postalCode: sendcloud_details['postcode'],
          language: 'en-us',
          carriers: sendcloud_details['carrier_name'],
          // servicePointId: '8718',
          // postNumber: sendcloud_details['postcode']
        };
        sendcloud.servicePoints.open(
          config,
          function(servicePointObject, postNumber) {
              var point_details = JSON.stringify(servicePointObject);
              var address_details = prepare_address(servicePointObject);
              //For remove existing service point address if added.
              delivery_line.find('br').remove();
              $('.o_service_point_address').remove();
              //For add service point address.
              delivery_line.append(address_details);
              //For clear service point.
              delivery_line.find('.o_clear_service_point').click(function(ev) {
                 delivery_line.find('br').remove();
                 $('.o_service_point_address').remove();
                 dp.add(ajax.jsonRpc('/shop/update_service_point_details', 'call', {'order_id':sendcloud_details.order_id,'sb_service_point_details':false}));
              });
              dp.add(ajax.jsonRpc('/shop/update_service_point_details', 'call', {'order_id':sendcloud_details.order_id,'sb_service_point_details':point_details}));
          },
          function(errors) {
            errors.forEach(function(error) {
              console.log('Failure callback, reason: ' + error)
            })
          }
        );
    };

    var _onCarrierUpdateAnswer = function(result) {
        var $amount_delivery = $('#order_delivery .monetary_field');
        var $amount_untaxed = $('#order_total_untaxed .monetary_field');
        var $amount_tax = $('#order_total_taxes .monetary_field');
        var $amount_total = $('#order_total .monetary_field');
        var $carrier_badge = $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .badge.d-none');
        var $compute_badge = $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .o_delivery_compute');
        var $discount = $('#order_discounted');

        if ($discount && result.new_amount_order_discounted) {
            // Cross module without bridge
            // Update discount of the order
            $discount.find('.oe_currency_value').text(result.new_amount_order_discounted);

            // We are in freeshipping, so every carrier is Free
            $('#delivery_carrier .badge').text(_t('Free'));
        }
        if (result.is_sendcloud_service_point_enable === true && is_service_point) {
            _openSendCloudServicePointMap.call(this,result['sendcloud_details']);
            is_service_point = false;
        }

        if (result.status === true) {
            $amount_delivery.html(result.new_amount_delivery);
            $amount_untaxed.html(result.new_amount_untaxed);
            $amount_tax.html(result.new_amount_tax);
            $amount_total.html(result.new_amount_total);
            $carrier_badge.children('span').text(result.new_amount_delivery);
            $carrier_badge.removeClass('d-none');
            $compute_badge.addClass('d-none');
//            $pay_button.data('disabled_reasons').carrier_selection = false;
//            $pay_button.prop('disabled', _.contains($pay_button.data('disabled_reasons'), true));
        }
        else {
            console.error(result.error_message);
            $compute_badge.html(result.error_message);
            $amount_delivery.html(result.new_amount_delivery);
            $amount_untaxed.html(result.new_amount_untaxed);
            $amount_tax.html(result.new_amount_tax);
            $amount_total.html(result.new_amount_total);
        }
    };

    var _onCarrierClick = function(ev) {
        $pay_button.data('disabled_reasons', $pay_button.data('disabled_reasons') || {});
//        $pay_button.data('disabled_reasons').carrier_selection = true;
        $pay_button.prop('disabled', true);
        var carrier_id = $(ev.currentTarget).val();
        var values = {'carrier_id': carrier_id};
        dp.add(ajax.jsonRpc('/shop/update_carrier', 'call', values))
          .then(_onCarrierUpdateAnswer);
    };

    var $carriers = $("#delivery_carrier input[name='delivery_type']");
    $carriers.unbind();
    $carriers.click(_onCarrierClick);

    $servicePointbtn.click(function(ev) {
        is_service_point = true;
        delivery_line = $(ev.currentTarget.parentElement.parentElement);
        $(ev.currentTarget.parentElement.parentElement).children()[0].click()
    });
});
