(function (e) {
    "use strict";
    let t = this, n = navigator.serviceWorker;
    if (!n) return t.UpUp = null, e;
    let s = {"service-worker-url": "/static/js/serviceworker-2378b519.js"}, r = !1;
    t.UpUp = {
        start: function (e) {
            this.addSettings(e), n.register(s["service-worker-url"], {scope: "./"}).then(function (e) {
                (e.installing || n.controller).postMessage({action: "set-settings", settings: s})
            })["catch"](function (e) {
            })
        }, addSettings: function (t) {
            t = t || {}, "string" == typeof t && (t = {content: t}), ["content", "content-url", "assets", "service-worker-url", "cache-version"].forEach(function (n) {
                t[n] !== e && (s[n] = t[n])
            })
        }, debug: function (e) {
            r = !(arguments.length > 0 && !e)
        }
    }
}).call(this), null !== UpUp && UpUp.start({
    "content-url": "offline.html",
    assets: ["/js/all-5bba9e50.js"]
});