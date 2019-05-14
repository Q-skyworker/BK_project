/*!
 * bkFileSelector v1.0
 * author ：蓝鲸智云
 * Copyright (c) 2012-2018 Tencent BlueKing. All Rights Reserved.
 */

(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() : typeof define === 'function' && define.amd ? define(factory) : (global.bkMessage = factory());
})(this, function () {
  'use strict';

  var count = 0;

  /**
   *  编译DOM节点字符串
   *  @param html {String} 拼接的DOM字符串
   *  @return DOM {DOMNode} DOM节点
   */
  var _compile = function(html) {
      var temp = document.createElement('div'),
          children = null,
          fragment = document.createDocumentFragment();

      temp.innerHTML = html;
      children = temp.childNodes;

      for(var i = 0, length = children.length; i < length; i++) {
          fragment.appendChild(children[i].cloneNode(true));
      }

      return fragment;
  }

  /**
   *  插件的构造函数
   *  @param 用户自定义的参数
   */
  function bkMessage (options) {
    var opts = options || {}

    if (typeof opts === 'string') {
      opts = {
        message: opts
      }
    }

    this.theme = opts.theme || 'primary';
    this.icon = opts.icon === false ? false : opts.icon;
    this.message = opts.message || '';
    this.delay = opts.delay || (opts.delay === 0 ? 0 : 3000);
    this.hasCloseIcon = opts.hasCloseIcon || false;
    this.onClose = opts.onClose || function () {};
    this.onShow = opts.onShow || function () {};

    _init.call(this);
  }

  /**
   *  初始化函数
   */
  var _init = function () {
    _initStyle.call(this);
    _initEvents.call(this);
  }

  /**
   *  初始化样式
   */
  var _initStyle = function () {
    var _this = this;
    var id = 'bkMessage_' + ++count;
    var closeIcon = this.hasCloseIcon ? ('<div class="bk-message-close">'+
                                          '<i class="bk-icon icon-close"></i>'+
                                        '</div>') : '';
    var icon = '', bkIcon;

    switch (this.theme) {
      case 'error':
        bkIcon = 'close';
        break;
      case 'warning':
        bkIcon = 'exclamation';
        break;
      case 'success':
        bkIcon = 'check-1';
        break;
      case 'primary':
        bkIcon = 'dialogue-shape';
        break;
    }

    bkIcon = this.icon ? this.icon : bkIcon;
    icon = '<div class="bk-message-icon">'+
              '<i class="bk-icon icon-' + bkIcon + '"></i>'+
            '</div>';

    var message = typeof this.message === 'string' ? this.message : this.message.outerHTML;

    var html = '<div class="bk-message ' + this.theme + ' dom-version" id="' + id + '">'+
                  icon+
                  '<div class="bk-message-content">'+
                    message+
                  '</div>'+
                  closeIcon+
                '</div>';

    document.body.appendChild(_compile(html));
    this.id = id

    setTimeout(function () {
      var $html = document.getElementById('bkMessage_' + count);

      $html.className = $html.className.replace('dom-version', '');
      _this.$html = $html;
      _this.onShow && _this.onShow(_this);
    }, 0)
  }

  /**
   *  初始化事件
   */
  function _initEvents () {
    var _this = this;

    setTimeout (function () {
      var $html = _this.$html;
      var $icon = $html.querySelector('.bk-message-close')

      if (_this.delay) {
        setTimeout (function () {
          _close.call(_this, $html);
        }, _this.delay);
      }

      if ($icon) {
        $icon.addEventListener('click', function (e) {
          e.stopPropagation();
          _close.call(_this, $html);
        }, false);
      }
    }, 0)
  }

  /**
   *  隐藏组件
   */
  function _hide ($el) {
    $el.className += 'dom-version';
  }

  /**
   *  移除DOM节点
   */
  function _remove ($el) {
    setTimeout (function () {
      $el.parentNode.removeChild($el);
    }, 210)
  }

  /**
   *  关闭消息提示组件
   */
  function _close ($el) {
    _hide($el);
    _remove($el);
    this.onClose && this.onClose(this);
  }

  bkMessage.prototype.hide = function () {
    _close.call(this, document.getElementById(this.id));
  }

  return bkMessage;
})
