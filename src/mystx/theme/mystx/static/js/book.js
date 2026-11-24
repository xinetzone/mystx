/* 页眉工具箱：全屏切换（不依赖第三方库） */
(function () {
  "use strict";

  window.toggleFullscreen = function () {
    if (!document.fullscreenElement) {
      var target = document.documentElement;
      var request = target.requestFullscreen || target.webkitRequestFullscreen;
      if (request) {
        request.call(target);
      }
    } else {
      var exit = document.exitFullscreen || document.webkitExitFullscreen;
      if (exit) {
        exit.call(document);
      }
    }
  };
})();
