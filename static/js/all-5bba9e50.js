window.requestAnimFrame = function () {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame
}(), window.cancelAnimFrame = function () {
    return window.cancelAnimationFrame || window.webkitCancelAnimationFrame || window.webkitCancelRequestAnimationFrame || window.mozCancelAnimationFrame
}();
let util = {
    bind: function (t, e) {
        return function () {
            t.apply(e, arguments)
        }
    }, forEach: function (t, e, i) {
        let n, s, r = t.length;
        for (s = 0; r > s && (n = e.call(i, s, t[s]), n !== !1); s++) ;
    }, onResizeEnd: function (t, e, i) {
        let n;
        return function () {
            e = e || 250, clearTimeout(n), n = setTimeout(function () {
                t.apply(i, arguments)
            }, e)
        }
    }, addListener: function (t, e, i, n) {
        "addEventListener" in t && t.addEventListener(e, i, n)
    }
};
!function (t, e, i) {
    "use strict";
    let n = e.documentElement, s = {
        create: function (t) {
            return e.createElement(t)
        }, old: !!/(Android\s(1.|2.))|(Silk\/1.)/i.test(navigator.userAgent), pfx: function () {
            let t = e.createElement("dummy").style, n = ["Webkit", "Moz", "O", "ms"], s = {};
            return function (e) {
                if ("undefined" == typeof s[e]) {
                    let r = e.charAt(0).toUpperCase() + e.substr(1), o = (e + " " + n.join(r + " ") + r).split(" ");
                    s[e] = null;
                    for (let a in o) if (t[o[a]] !== i) {
                        s[e] = o[a];
                        break
                    }
                }
                return s[e]
            }
        }()
    }, r = {
        css3Dtransform: function () {
            let t = !s.old && null !== s.pfx("perspective");
            return !!t
        }(),
        addEventListener: !!t.addEventListener,
        querySelectorAll: !!e.querySelectorAll,
        classList: "classList" in n,
        viewportUnit: function (t) {
            try {
                t.style.width = "1vw";
                let e = "" !== t.style.width;
                return !!e
            } catch (i) {
                return !1
            }
        }(s.create("dummy")),
        canvas: function (t) {
            return !(!t.getContext || !t.getContext("2d"))
        }(s.create("canvas")),
        svg: !!e.createElementNS && !!e.createElementNS("http://www.w3.org/2000/svg", "svg").createSVGRect,
        touch: !!("ontouchstart" in t || t.navigator && t.navigator.msPointerEnabled && t.MSGesture || t.DocumentTouch && e instanceof DocumentTouch)
    };
    t.feature = r
}(window, document), function (t, e) {
    "use strict";

    function i(t) {
        this.element = t, this.speed = 4, this.lastPosition, this.wHeight, this.initialized = !1, this.ticking = !1
    }

    function n(t) {
        let e = new i(t);
        return e.init(), e
    }

    i.prototype = {
        constructor: i, sizes: function () {
            this.lastPosition = -1, this.wHeight = t.innerHeight, this.lastPosition = t.pageYOffset, this.element.style.display = "block", this.element.height = this.wHeight, this.element.stop = this.element.height + 200, this.element.start = 0
        }, setTransform: function (t, e) {
            t.style.webkitTransform = t.style.transform = "translateZ(0) translateY(" + (1 - e / 2) + "px)", t.style.opacity = this.element.height < 1e3 ? 1 - e / 160 : 1 - e / 220
        }, loop: function () {
            let e = t.pageYOffset;
            if (this.lastPosition === e) {
                if (this.ticking = !1, this.initialized) return !1;
                this.initialized = !0
            } else this.lastPosition = e;
            this.lastPosition >= this.element.start - this.wHeight && this.lastPosition <= this.element.stop && this.setTransform(this.element, this.element.start + this.lastPosition / this.speed), this.ticking = !1
        }, handleEvent: function () {
            this.requestTick()
        }, requestTick: function () {
            this.ticking || (requestAnimFrame(this.loop.bind(this)), this.ticking = !0)
        }, init: function () {
            t.addEventListener && e.querySelectorAll && (this.throttledUpdate = util.onResizeEnd(this.sizes, 100, this), t.addEventListener("resize", this.throttledUpdate, !1), t.addEventListener("scroll", this, !1), this.requestTick(), this.sizes())
        }
    }, t.plx = n
}(window, document), function (t, e) {
    "function" == typeof define && define.amd ? define([], e(t)) : "object" == typeof exports ? module.exports = e(t) : t.smoothScroll = e(t)
}("undefined" != typeof global ? global : this.window || this.global, function (t) {
    "use strict";
    let e, i, n, s, r, o, a, l = {}, c = "querySelector" in document && "addEventListener" in t, h = {
        selector: "[data-scroll]",
        selectorHeader: null,
        speed: 500,
        easing: "easeInOutCubic",
        offset: 0,
        callback: function () {
        }
    }, u = function () {
        let t = {}, e = !1, i = 0, n = arguments.length;
        "[object Boolean]" === Object.prototype.toString.call(arguments[0]) && (e = arguments[0], i++);
        for (let s = function (i) {
            for (let n in i) Object.prototype.hasOwnProperty.call(i, n) && (t[n] = e && "[object Object]" === Object.prototype.toString.call(i[n]) ? u(!0, t[n], i[n]) : i[n])
        }; n > i; i++) {
            let r = arguments[i];
            s(r)
        }
        return t
    }, d = function (t) {
        return Math.max(t.scrollHeight, t.offsetHeight, t.clientHeight)
    }, m = function (t, e) {
        for (Element.prototype.matches || (Element.prototype.matches = Element.prototype.matchesSelector || Element.prototype.mozMatchesSelector || Element.prototype.msMatchesSelector || Element.prototype.oMatchesSelector || Element.prototype.webkitMatchesSelector || function (t) {
            for (let e = (this.document || this.ownerDocument).querySelectorAll(t), i = e.length; --i >= 0 && e.item(i) !== this;) ;
            return i > -1
        }); t && t !== document; t = t.parentNode) if (t.matches(e)) return t;
        return null
    }, f = function (t, e) {
        let i = .5 > e ? 4 * e * e * e : (e - 1) * (2 * e - 2) * (2 * e - 2) + 1;
        return i || e
    }, v = function (t, e, i) {
        let n = 0;
        if (t.offsetParent) do n += t.offsetTop, t = t.offsetParent; while (t);
        return n = Math.max(n - e - i, 0), Math.min(n, g() - p())
    }, p = function () {
        return Math.max(document.documentElement.clientHeight, t.innerHeight || 0)
    }, g = function () {
        return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight)
    }, y = function (t) {
        return t && "object" == typeof JSON && "function" == typeof JSON.parse ? JSON.parse(t) : {}
    }, b = function (t) {
        return t ? d(t) + t.offsetTop : 0
    }, w = function (e, i, n) {
        n || (e.id && "home" === e.id ? (e.querySelector(".wrapper").setAttribute("tabindex", "-1"), e.querySelector(".wrapper").focus()) : (e.focus(), document.activeElement.id !== e.id && (e.setAttribute("tabindex", "-1"), e.focus()), t.scrollTo(0, i)))
    };
    l.animateScroll = function (i, n, o) {
        let l = y(n ? n.getAttribute("data-options") : null), c = u(e || h, o || {}, l),
            d = "[object Number]" === Object.prototype.toString.call(i) ? !0 : !1, m = d || !i.tagName ? null : i;
        if (d || m) {
            let p = t.pageYOffset;
            c.selectorHeader && !s && (s = document.querySelector(c.selectorHeader)), r || (r = b(s));
            let E, L, S = d ? i : v(m, r, parseInt(c.offset, 10)), x = S - p, k = g(), A = 0, N = function (e, s, r) {
                let o = t.pageYOffset;
                (e == s || o == s || t.innerHeight + o >= k) && (clearInterval(r), w(i, s, d), c.callback(i, n))
            }, T = function () {
                A += 16, E = A / parseInt(c.speed, 10), E = E > 1 ? 1 : E, L = p + x * f(c.easing, E), t.scrollTo(0, Math.floor(L)), N(L, S, a)
            }, q = function () {
                clearInterval(a), a = setInterval(T, 16)
            };
            0 === t.pageYOffset && t.scrollTo(0, 0), q()
        }
    };
    let E = function () {
        let e;
        try {
            e = decodeURIComponent(t.location.hash)
        } catch (s) {
            e = t.location.hash
        }
        i && (i.id = i.getAttribute("data-scroll-id"), l.animateScroll(i, n), i = null, n = null)
    }, L = function (s) {
        if (0 === s.button && !s.metaKey && !s.ctrlKey && (n = m(s.target, e.selector), n && "a" === n.tagName.toLowerCase() && n.hostname === t.location.hostname && n.pathname === t.location.pathname && /#/.test(n.href))) {
            let r;
            try {
                r = decodeURIComponent(n.hash)
            } catch (o) {
                r = n.hash
            }
            if ("#" === r) {
                s.preventDefault(), i = document.body;
                let a = i.id ? i.id : "smooth-scroll-top";
                return i.setAttribute("data-scroll-id", a), i.id = "", void (t.location.hash.substring(1) === a ? E() : t.location.hash = a)
            }
            i = document.querySelector(r), i && (i.setAttribute("data-scroll-id", i.id), i.id = "", n.hash === t.location.hash && (s.preventDefault(), E()))
        }
    }, S = function () {
        o || (o = setTimeout(function () {
            o = null, r = b(s)
        }, 66))
    };
    return l.destroy = function () {
        e && (document.removeEventListener("click", L, !1), t.removeEventListener("resize", S, !1), e = null, i = null, n = null, s = null, r = null, o = null, a = null)
    }, l.init = function (i) {
        c && (l.destroy(), e = u(h, i || {}), s = e.selectorHeader ? document.querySelector(e.selectorHeader) : null, r = b(s), document.addEventListener("click", L, !1), t.addEventListener("hashchange", E, !1), s && t.addEventListener("resize", S, !1))
    }, l
}), function (t, e) {
    "use strict";

    function i() {
        this.loaded = !1, this.header = e.querySelector("header"), this.initialWidth = t.innerWidth || e.documentElement.clientWidth || e.getElementsByTagName("body")[0].clientWidth, this.cvs = e.createElement("canvas"), this.ctx = this.cvs.getContext("2d")
    }

    function n() {
        let t = new i;
        return t.init(), t
    }

    i.prototype = {
        constructor: i, init: function () {
            for (this.box = this.header.getBoundingClientRect(), this.w = this.box.width, this.h = this.box.height, this.numDotsOrig = 150, this.size = 1.6, this.w > 700 && (this.size = 2), this.w > 1300 && this.w < 1600 ? this.numDotsOrig = 200 : this.w > 1600 && this.w < 2e3 ? this.numDotsOrig = 250 : this.w > 2e3 && (this.numDotsOrig = 300), this.numDots = this.numDotsOrig, this.currDot, this.maxRad = this.w / 1.2, this.minRad = this.w / 2.5, this.w > 500 && this.w < 800 ? (this.maxRad = this.w / 1.5, this.minRad = this.w / 3) : this.w > 800 && this.w < 1e3 ? (this.maxRad = this.w / 1.8, this.minRad = this.w / 6) : this.w > 1e3 && this.w < 1600 ? (this.maxRad = this.w / 2, this.minRad = this.w / 6) : this.w > 1600 && (this.maxRad = this.w / 2.3, this.minRad = this.w / 8), this.radDiff = this.maxRad - this.minRad, this.dots = [], this.centerPt = {
                x: 0,
                y: 0
            }, this.prevFrameTime = 0; this.numDots--;) this.currDot = {}, this.currDot.radius = this.minRad + Math.random() * this.radDiff, this.currDot.ang = (1 - 2 * Math.random()) * Math.PI, this.currDot.speed = .005 * (1 - 2 * Math.random()), this.currDot.intensity = Math.round(255 * Math.random()), this.currDot.fillColor = "rgb(" + 255 * this.currDot.intensity + "," + this.currDot.intensity + "," + this.currDot.intensity + ")", this.dots.push(this.currDot);
            this._centerPt = this.centerPt, this._context = this.ctx, this.dX = 0, this.dY = 0, this.prevFrameTime = 0, this.cvs.width = this.w, this.cvs.height = this.h, this.centerPt.x = Math.round(this.w / 2), this.centerPt.y = Math.round(this.h / 2), this.loaded || (this.generateDomStructure(), this.initThrottle(), this.requestUpdate(), this.loaded = !0)
        }, requestUpdate: function (e) {
            let i = e - (this.prevFrameTime || 0);
            if (t.matchMedia ? t.matchMedia("(prefers-reduced-motion)").matches || requestAnimFrame(util.bind(this.requestUpdate, this)) : requestAnimFrame(util.bind(this.requestUpdate, this)), !(30 > i && this.prevFrameTime)) {
                this.prevFrameTime = e;
                let n = this.numDotsOrig;
                for (this._context.clearRect(0, 0, this.cvs.width, this.cvs.height); n--;) this.currDot = this.dots[n], this.dX = this._centerPt.x + Math.sin(this.currDot.ang) * this.currDot.radius, this.dY = this._centerPt.y + Math.cos(this.currDot.ang) * this.currDot.radius, this.currDot.ang += this.currDot.speed, this._context.fillStyle = this.currDot.fillColor, this._context.fillRect(this.dX, this.dY, this.size, this.size)
            }
        }, resize: function () {
            this.currWidth = t.innerWidth || e.documentElement.clientWidth || e.getElementsByTagName("body")[0].clientWidth, this.currWidth !== this.initialWidth && (this.initialWidth = this.currWidth, cancelAnimFrame(util.bind(this.update, this)), this.init())
        }, generateDomStructure: function () {
            this.remove = e.querySelector("canvas"), this.remove && this.remove.parentNode.removeChild(this.remove), this.cvs.classList.add("canvas--hidden"), this.header.appendChild(this.cvs), this.cvs.classList.add("canvas--active")
        }, initThrottle: function () {
            this.throttledUpdate = util.onResizeEnd(this.resize, 100, this), util.addListener(t, "resize", this.throttledUpdate, !1)
        }
    }, t.universe = n
}(window, document), function (t, e) {
    if ("object" == typeof exports && "object" == typeof module) module.exports = e(); else if ("function" == typeof define && define.amd) define([], e); else {
        let i = e();
        for (let n in i) ("object" == typeof exports ? exports : t)[n] = i[n]
    }
}(this, function () {
    return function (t) {
        function e(n) {
            if (i[n]) return i[n].exports;
            let s = i[n] = {exports: {}, id: n, loaded: !1};
            return t[n].call(s.exports, s, s.exports, e), s.loaded = !0, s.exports
        }

        let i = {};
        return e.m = t, e.c = i, e.p = "", e(0)
    }([function (t, e, i) {
        t.exports = i(1)
    }, function (t, e, i) {
        "use strict";

        function n(t) {
            return t && t.__esModule ? t : {"default": t}
        }

        function s(t, e) {
            function i(t, e) {
                let i = j, n = i.classNameActiveSlide;
                t.forEach(function (t) {
                    t.classList.contains(n) && t.classList.remove(n)
                }), t[e].classList.add(n)
            }

            function n(t) {
                let e = j, i = e.infinite, n = t.slice(0, i), s = t.slice(t.length - i, t.length);
                return n.forEach(function (t) {
                    let e = t.cloneNode(!0);
                    D.appendChild(e)
                }), s.reverse().forEach(function (t) {
                    let e = t.cloneNode(!0);
                    D.insertBefore(e, D.firstChild)
                }), D.addEventListener(_.transitionEnd, b), d.call(D.children)
            }

            function s(e, i, n) {
                c["default"](t, e + ".lory." + i, n)
            }

            function o(t, e, i) {
                let n = D && D.style;
                n && (n[_.transition + "TimingFunction"] = i, n[_.transition + "Duration"] = e + "ms", n[_.transform] = _.hasTranslate3d ? "translate3d(" + t + "px, 0, 0)" : "translate(" + t + "px, 0)")
            }

            function l(t, e) {
                let n = j, r = n.slideSpeed, a = n.slidesToScroll, l = n.infinite, c = n.rewind, h = n.rewindSpeed,
                    u = n.ease, m = n.classNameActiveSlide, f = r, v = e ? O + 1 : O - 1, p = Math.round(A - N);
                s("before", "slide", {
                    index: O,
                    nextSlide: v
                }), "number" != typeof t && (t = e ? O + a : O - a), t = Math.min(Math.max(t, 0), T.length - 1), l && void 0 === e && (t += l);
                let g = Math.min(Math.max(-1 * T[t].offsetLeft, -1 * p), 0);
                c && Math.abs(k.x) === p && e && (g = 0, t = 0, f = h), o(g, f, u), k.x = g, T[t].offsetLeft <= p && (O = t), !l || t !== T.length - l && 0 !== t || (e && (O = l), e || (O = T.length - 2 * l), k.x = -1 * T[O].offsetLeft, H = function () {
                    o(-1 * T[O].offsetLeft, 0, void 0)
                }), m && i(d.call(T), O), s("after", "slide", {currentSlide: O})
            }

            function h() {
                s("before", "init"), _ = a["default"](), j = r({}, u["default"], e);
                let o = j, l = o.classNameFrame, c = o.classNameSlideContainer, h = o.classNamePrevCtrl,
                    f = o.classNameNextCtrl, v = o.enableMouseEvents, y = o.classNameActiveSlide;
                q = t.getElementsByClassName(l)[0], D = q.getElementsByClassName(c)[0], M = t.getElementsByClassName(h)[0], C = t.getElementsByClassName(f)[0], k = {
                    x: D.offsetLeft,
                    y: D.offsetTop
                }, T = j.infinite ? n(d.call(D.children)) : d.call(D.children), m(), y && i(T, O), M && C && (M.addEventListener("click", p), C.addEventListener("click", g)), q.addEventListener("touchstart", w), v && (q.addEventListener("mousedown", w), q.addEventListener("click", S)), j.window.addEventListener("resize", x), s("after", "init")
            }

            function m() {
                let t = j, e = (t.infinite, t.ease), n = t.rewindSpeed, s = t.rewindOnResize,
                    r = t.classNameActiveSlide;
                A = D.getBoundingClientRect().width || D.offsetWidth, N = q.getBoundingClientRect().width || q.offsetWidth, N === A && (A = T.reduce(function (t, e) {
                    return t + e.getBoundingClientRect().width || e.offsetWidth
                }, 0)), s ? O = 0 : (e = null, n = 0), o(-1 * T[O].offsetLeft, n, e), k.x = -1 * T[O].offsetLeft, r && i(d.call(T), O)
            }

            function f(t) {
                l(t)
            }

            function v() {
                return O - j.infinite || 0
            }

            function p() {
                l(!1, !1)
            }

            function g() {
                l(!1, !0)
            }

            function y() {
                s("before", "destroy"), q.removeEventListener(_.transitionEnd, b), q.removeEventListener("touchstart", w), q.removeEventListener("touchmove", E), q.removeEventListener("touchend", L), q.removeEventListener("mousemove", E), q.removeEventListener("mousedown", w), q.removeEventListener("mouseup", L), q.removeEventListener("mouseleave", L), q.removeEventListener("click", S), j.window.removeEventListener("resize", x), M && M.removeEventListener("click", p), C && C.removeEventListener("click", g), j.infinite && Array.apply(null, Array(j.infinite)).forEach(function () {
                    D.firstChild && D.removeChild(D.firstChild), D.lastChild && D.removeChild(D.lastChild)
                }), s("after", "destroy")
            }

            function b() {
                H && (H(), H = void 0)
            }

            function w(t) {
                let e = j, i = e.enableMouseEvents, n = t.touches ? t.touches[0] : t;
                i && (q.addEventListener("mousemove", E), q.addEventListener("mouseup", L), q.addEventListener("mouseleave", L)), q.addEventListener("touchmove", E), q.addEventListener("touchend", L);
                let r = n.pageX, o = n.pageY;
                z = {x: r, y: o, time: Date.now()}, F = void 0, B = {}, s("on", "touchstart", {event: t})
            }

            function E(t) {
                let e = t.touches ? t.touches[0] : t, i = e.pageX, n = e.pageY;
                B = {
                    x: i - z.x,
                    y: n - z.y
                }, "undefined" == typeof F && (F = !!(F || Math.abs(B.x) < Math.abs(B.y))), !F && z && (t.preventDefault(), o(k.x + B.x, 0, null)), s("on", "touchmove", {event: t})
            }

            function L(t) {
                let e = z ? Date.now() - z.time : void 0,
                    i = Number(e) < 300 && Math.abs(B.x) > 25 || Math.abs(B.x) > N / 10,
                    n = !O && B.x > 0 || O === T.length - 1 && B.x < 0, r = B.x < 0;
                F || (i && !n ? l(!1, r) : o(k.x, j.snapBackSpeed)), z = void 0, q.removeEventListener("touchmove", E), q.removeEventListener("touchend", L), q.removeEventListener("mousemove", E), q.removeEventListener("mouseup", L), q.removeEventListener("mouseleave", L), s("on", "touchend", {event: t})
            }

            function S(t) {
                B.x && t.preventDefault()
            }

            function x(t) {
                m(), s("on", "resize", {event: t})
            }

            let k = void 0, A = void 0, N = void 0, T = void 0, q = void 0, D = void 0, M = void 0, C = void 0,
                _ = void 0, H = void 0, O = 0, j = {};
            "undefined" != typeof jQuery && t instanceof jQuery && (t = t[0]);
            let z = void 0, B = void 0, F = void 0;
            return h(), {setup: h, reset: m, slideTo: f, returnIndex: v, prev: p, next: g, destroy: y}
        }

        Object.defineProperty(e, "__esModule", {value: !0});
        let r = Object.assign || function (t) {
            for (let e = 1; e < arguments.length; e++) {
                let i = arguments[e];
                for (let n in i) Object.prototype.hasOwnProperty.call(i, n) && (t[n] = i[n])
            }
            return t
        };
        e.lory = s;
        let o = i(2), a = n(o), l = i(3), c = n(l), h = i(5), u = n(h), d = Array.prototype.slice
    }, function (t, e) {
        (function (t) {
            "use strict";

            function i() {
                let e = void 0, i = void 0, n = void 0, s = void 0;
                return function () {
                    let r = document.createElement("_"), o = r.style, a = void 0;
                    "" === o[a = "webkitTransition"] && (n = "webkitTransitionEnd", i = a), "" === o[a = "transition"] && (n = "transitionend", i = a), "" === o[a = "webkitTransform"] && (e = a), "" === o[a = "msTransform"] && (e = a), "" === o[a = "transform"] && (e = a), document.body.insertBefore(r, null), o[e] = "translate3d(0, 0, 0)", s = !!t.getComputedStyle(r).getPropertyValue(e), document.body.removeChild(r)
                }(), {transform: e, transition: i, transitionEnd: n, hasTranslate3d: s}
            }

            Object.defineProperty(e, "__esModule", {value: !0}), e["default"] = i
        }).call(e, function () {
            return this
        }())
    }, function (t, e, i) {
        "use strict";

        function n(t) {
            return t && t.__esModule ? t : {"default": t}
        }

        function s(t, e, i) {
            let n = new o["default"](e, {bubbles: !0, cancelable: !0, detail: i});
            t.dispatchEvent(n)
        }

        Object.defineProperty(e, "__esModule", {value: !0}), e["default"] = s;
        let r = i(4), o = n(r)
    }, function (t, e) {
        (function (e) {
            function i() {
                try {
                    let t = new n("cat", {detail: {foo: "bar"}});
                    return "cat" === t.type && "bar" === t.detail.foo
                } catch (e) {
                }
                return !1
            }

            let n = e.CustomEvent;
            t.exports = i() ? n : "function" == typeof document.createEvent ? function (t, e) {
                let i = document.createEvent("CustomEvent");
                return e ? i.initCustomEvent(t, e.bubbles, e.cancelable, e.detail) : i.initCustomEvent(t, !1, !1, void 0), i
            } : function (t, e) {
                let i = document.createEventObject();
                return i.type = t, e ? (i.bubbles = Boolean(e.bubbles), i.cancelable = Boolean(e.cancelable), i.detail = e.detail) : (i.bubbles = !1, i.cancelable = !1, i.detail = void 0), i
            }
        }).call(e, function () {
            return this
        }())
    }, function (t, e) {
        "use strict";
        Object.defineProperty(e, "__esModule", {value: !0}), e["default"] = {
            slidesToScroll: 1,
            slideSpeed: 300,
            rewindSpeed: 600,
            snapBackSpeed: 200,
            ease: "ease",
            rewind: !1,
            infinite: !1,
            classNameFrame: "js_frame",
            classNameSlideContainer: "js_slides",
            classNamePrevCtrl: "js_prev",
            classNameNextCtrl: "js_next",
            classNameActiveSlide: "active",
            enableMouseEvents: !1,
            window: window,
            rewindOnResize: !0
        }
    }])
}), function (t, e, i) {
    let n = {
            messages: {
                required: "The %s field is required.",
                consent: "You need to agree our %s before submitting",
                valid_email: "The %s field must contain a valid email address.",
                valid_url: "The %s field must contain a valid URL."
            }, callback: function () {
            }
        }, s = /^(.+?)\[(.+)\]$/,
        r = /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/,
        o = function (t, e, s) {
            this.callback = s || n.callback, this.errors = [], this.fields = {}, this.form = this._formByNameOrNode(t) || {}, this.messages = {}, this.handlers = {}, this.conditionals = {};
            for (let r = 0, o = e.length; o > r; r++) {
                let a = e[r];
                if ((a.name || a.names) && a.rules) if (a.names) for (let l = 0, c = a.names.length; c > l; l++) this._addField(a, a.names[l]); else this._addField(a, a.name)
            }
            let h = this.form.onsubmit;
            this.form.onsubmit = function (t) {
                return function (e) {
                    try {
                        return t._validateForm(e) && (h === i || h())
                    } catch (n) {
                    }
                }
            }(this)
        }, a = function (t, e) {
            let i;
            {
                if (!(t.length > 0) || "radio" !== t[0].type && "checkbox" !== t[0].type) return t[e];
                for (i = 0, elementLength = t.length; i < elementLength; i++) if (t[i].checked) return t[i][e]
            }
        };
    o.prototype._formByNameOrNode = function (t) {
        return "object" == typeof t ? t : e.forms[t]
    }, o.prototype._addField = function (t, e) {
        this.fields[e] = {
            name: e,
            display: t.display || e,
            rules: t.rules,
            depends: t.depends,
            id: null,
            element: null,
            type: null,
            value: null,
            checked: null
        }
    }, o.prototype._validateForm = function (t) {
        this.errors = [];
        for (let e in this.fields) if (this.fields.hasOwnProperty(e)) {
            let n = this.fields[e] || {}, s = this.form[n.name];
            s && s !== i && (n.id = a(s, "id"), n.element = s, n.type = s.length > 0 ? s[0].type : s.type, n.value = a(s, "value"), n.checked = a(s, "checked"), n.depends && "function" == typeof n.depends ? n.depends.call(this, n) && this._validateField(n) : n.depends && "string" == typeof n.depends && this.conditionals[n.depends] ? this.conditionals[n.depends].call(this, n) && this._validateField(n) : this._validateField(n))
        }
        return "function" == typeof this.callback && this.callback(this.errors, t), this.errors.length > 0 && (t && t.preventDefault ? t.preventDefault() : event && (event.returnValue = !1)), !0
    }, o.prototype._validateField = function (t) {
        let e, r, o, a = t.rules.split("|"), l = t.rules.indexOf("required"),
            c = !t.value || "" === t.value || t.value === i;
        for (e = 0, o = a.length; o > e; e++) {
            let h = a[e], u = null, d = !1, m = s.exec(h);
            if ((-1 !== l || -1 !== h.indexOf("!callback_") || !c) && (m && (h = m[1], u = m[2]), "!" === h.charAt(0) && (h = h.substring(1, h.length)), "function" == typeof this._hooks[h] ? this._hooks[h].apply(this, [t, u]) || (d = !0) : "callback_" === h.substring(0, 9) && (h = h.substring(9, h.length), "function" == typeof this.handlers[h] && this.handlers[h].apply(this, [t.value, u, t]) === !1 && (d = !0)), d)) {
                let f = this.messages[t.name + "." + h] || this.messages[h] || n.messages[h],
                    v = "An error has occurred with the " + t.display + " field.";
                f && (v = f.replace("%s", t.display), u && (v = v.replace("%s", this.fields[u] ? this.fields[u].display : u)));
                let p;
                for (r = 0; r < this.errors.length; r += 1) t.id === this.errors[r].id && (p = this.errors[r]);
                let g = p || {
                    id: t.id,
                    display: t.display,
                    element: t.element,
                    name: t.name,
                    message: v,
                    messages: [],
                    rule: h
                };
                g.messages.push(v), p || this.errors.push(g)
            }
        }
    }, o.prototype._hooks = {
        required: function (t) {
            let e = t.value;
            return "checkbox" === t.type || "radio" === t.type ? t.checked === !0 : null !== e && "" !== e
        }, consent: function (t) {
            let e = t.value;
            return "checkbox" === t.type || "radio" === t.type ? t.checked === !0 : null !== e && "" !== e
        }, "default": function (t, e) {
            return t.value !== e
        }, valid_email: function (t) {
            return r.test(t.value)
        }
    }, t.FormValidator = o
}(window, document), "undefined" != typeof module && module.exports && (module.exports = FormValidator), function (t, e) {
    "use strict";

    function i() {
        this.body = e.body, this.html = e.documentElement, this.openingProject = !1, this.currentHash = "#home", this.initialWidth = t.innerWidth || this.html.clientWidth || this.body.clientWidth, this.currWidth = 0, this.ua = navigator.userAgent || navigator.vendor || t.opera, feature.querySelectorAll && (this.errorEl = e.querySelector(".errors"), this.sliderEl = e.querySelector(".slider"), this.nav = e.querySelector(".js-nav"), this.wrapper = e.querySelector("header .wrapper"), this.nextBtn = e.querySelector(".btn--next")), this.top = 0, this.wasNavigationTapped = !1, this.nav && feature.querySelectorAll && (this.links = this.nav.querySelectorAll("a"), this.activeLink = this.links[0])
    }

    function n() {
        let t = new i;
        return t.init(), t
    }

    i.prototype = {
        constructor: i, init: function () {
            if (/(Opera Mini)/i.test(this.ua) && (this.html.className += " opera-mini"), ("WebkitAppearance" in this.html.style || /Firefox/i.test(this.ua)) && /Android/i.test(this.ua) && (this.html.className += " android-webkit"), this.iOS = /iPad|iPhone|iPod/.test(this.ua) && !t.MSStream, this.isFacebookApp() && this.iOS && (this.html.className += " facebook"), this.iOS && (this.html.className += " ios"), (e.documentMode || /Edge/.test(this.ua)) && (this.html.className += " ie"), this.images = e.getElementsByTagName("img"), feature.classList && feature.querySelectorAll && (this.images && util.forEach(this.images, function (t) {
                this.lazyLoadImage(this.images[t], "data-src")
            }, this), this.validateForm()), !(feature.svg && feature.classList && feature.canvas && feature.addEventListener && feature.css3Dtransform && feature.querySelectorAll && feature.viewportUnit)) return void (this.html.className += " no-modern");
            feature.touch && (this.html.className += " touch"), this.html.className += " modern";
            let i = this;
            smoothScroll.init(), e.querySelector("header") && universe(), e.querySelector("header h1") && !this.html.classList.contains("android-webkit") && (t.matchMedia ? t.matchMedia("(prefers-reduced-motion)").matches || plx(e.querySelector(".wrapper__wrap")) : plx(e.querySelector(".wrapper__wrap"))), this.selectBox(), this.calcViewport(), this.contactForm = e.querySelector("#contactform"), this.contactForm && util.addListener(this.contactForm, "submit", function (t) {
                t.preventDefault()
            }, !1);
        }, closeProject: function () {
            let t = e.querySelectorAll(".hero__fullscreen");
            this.html.classList.remove("noscrolling"), e.querySelector(".btn--close").classList.remove("active"), t && util.forEach(t, function (e) {
                t[e].classList.remove("active")
            }, this);
            let i = e.querySelector(".section--projects");
            i.setAttribute("tabindex", "-1"), i.focus(), history.replaceState(null, null, "#projects")
        }, handleHashChange: function (t) {
            t.preventDefault(), this.html.classList.contains("noscrolling") && !this.openingProject && this.closeProject()
        }, handleKeyup: function (t) {
            27 === t.keyCode && this.html.classList.contains("noscrolling") && this.closeProject()
        }, imagesLoaded: function () {
            this.setupLocations(), this.highlightOnScroll()
        }, calcViewport: function () {
            this.viewportWidth = t.innerWidth || 0, this.viewportHeight = t.innerHeight || 0, this.bodyheight = Math.max(this.body.scrollHeight, this.body.offsetHeight, this.html.clientHeight, this.html.scrollHeight, this.html.offsetHeight)
        }, isFacebookApp: function () {
            return this.ua.indexOf("FBAN") > -1 || this.ua.indexOf("FBAV") > -1
        }, header: function (i) {
            let n = t.innerWidth, s = e.querySelector("header");
            s && (!i && 860 > n && n > 300 ? s.style.height = t.innerHeight + "px" : i && s.hasAttribute("style") && n > 860 ? s.removeAttribute("style") : 300 > n && s.removeAttribute("style"))
        }, initProjects: function () {
            let t = this, i = e.querySelectorAll(".hero"), n = e.querySelectorAll(".hero__fullscreen"),
                s = e.querySelector(".btn--close");
            i && (util.forEach(i, function (r) {
                util.addListener(i[r], "click", function (i) {
                    i.preventDefault(), t.html.classList.add("noscrolling"), n[r].classList.add("active"), n[r].scrollTop = 0, n[r].setAttribute("tabindex", "-1"), n[r].focus(), s.classList.add("active"), t.openingProject = !0, history.pushState && history.pushState(null, null, "#projects/" + n[r].id), n[r].addEventListener("touchstart", function (t) {
                        this.scrollHeight !== this.clientHeight && (0 === this.scrollTop && (this.scrollTop = 1), this.scrollTop === this.scrollHeight - this.clientHeight && (this.scrollTop = this.scrollHeight - this.clientHeight - 1)), this.allowUp = this.scrollTop > 0, this.allowDown = this.scrollTop < this.scrollHeight - this.clientHeight, this.lastY = 0, this.lastY = t.originalEvent ? t.originalEvent.pageY : t.pageY, (up && this.allowUp || down && this.allowDown) && t.preventDefault()
                    }, !1), n[r].addEventListener("touchmove", function (t) {
                        let e = t.pageY > this.lastY, i = !e;
                        this.lastY = t.pageY, e && this.allowUp || i && this.allowDown ? t.stopPropagation() : t.preventDefault()
                    }, !1);
                    let o = e.querySelectorAll(".hero__image img")[r];
                    t.lazyLoadImage(o, "data-lazy-src", !0), setTimeout(function () {
                        t.openingProject = !1
                    }, 0)
                }, !1)
            }, this), s && util.addListener(s, "click", function (e) {
                e.preventDefault(), t.openingProject = !1, t.handleHashChange(e)
            }, !1))
        }, lazyLoadImage: function (t, e, i) {
            if (t && t.getAttribute(e)) {
                let n = new Image;
                n.src = t.getAttribute(e), n.onload = function () {
                    i ? setTimeout(function () {
                        t.src = n.src, t.removeAttribute(e), t.parentNode.classList.remove("loading")
                    }, 600) : (t.src = n.src, t.removeAttribute(e), t.parentNode.classList.remove("loading"))
                }
            }
        }, selectBox: function () {
            this.selectBox = e.querySelector(".select__wrapper"), this.selectBox && (this.selectEl = this.selectBox.querySelector("select"), util.addListener(this.selectEl, "change", function () {
                e.querySelector(".select").innerHTML = this.value + " <svg fill='#fff' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7.41 7.84L12 12.42l4.59-4.58L18 9.25l-6 6-6-6z'/><path d='M0-.75h24v24H0z' fill='none'/></svg>"
            }, !1))
        }, validateForm: function () {
            let t = this;
            this.validator = new FormValidator("contactform", [{
                name: "email",
                display: "Email",
                rules: "required|valid_email"
            }, {name: "details", display: "Project Details", rules: "required"}, {
                name: "consent",
                display: "Privacy Policy",
                rules: "consent"
            }, {name: "url", rules: "valid_url"}], function (i) {
                if (i.length > 0) {
                    for (let n = "", s = 0, r = i.length; r > s; s++) n += i[s].message + "<br />";
                    t.errorEl.classList.add("active"), t.errorEl.innerHTML = n;
                    let o = e.querySelector("#errors"), a = {offset: 100};
                    smoothScroll.animateScroll(o, null, a)
                } else t.errorEl.classList.remove("active"), t.submitForm()
            })
        }, submitForm: function () {
            return this.validation = e.getElementById("title"), "" !== this.validation.value ? (t.location = "https://viljamisdesign.com/thanks/?status=true", !1) : void this.contactForm.submit()
        }, initCarousel: function () {
            this.sliderEl = e.querySelector(".slider"), this.sliderEl && (this.slider = lory(this.sliderEl, {
                infinite: 6,
                slidesToScroll: 1,
                rewindOnResize: !1,
                slideSpeed: 400,
                classNameActiveSlide: "js-active",
                ease: "cubic-bezier(0.455, 0.03, 0.515, 0.955)"
            }), util.addListener(this.sliderEl, "after.lory.slide", util.bind(this.slideEvent, this), !1))
        }, nextSlide: function (t) {
            t.preventDefault(), this.slider.next()
        }, slideEvent: function (t) {
            let e = this;
            e.slideElems && (util.forEach(e.slideElems, function (t) {
                e.slideElems[t].classList.remove("active")
            }), e.slideElems[t.detail.currentSlide + 1].classList.add("active"), e.slideElems[t.detail.currentSlide + 2].classList.add("active"))
        }, initSlider: function () {
            this.deadlineOutput = e.getElementById("deadlineoutput"), this.budgetOutput = e.getElementById("budgetoutput"), this.inputs = e.querySelectorAll('input[type="range"]');
            let t = this;
            this.inputs && util.forEach(this.inputs, function (e, i) {
                util.addListener(i, "input", function () {
                    let e = Math.ceil((this.value - this.min) / (this.max - this.min) * 100);
                    i.style.background = "-webkit-linear-gradient(left, #ED4B37 0%, #ED4B37 " + e + "%, #204b76 " + e + "%)", i.classList.contains("deadline") && (t.deadlineOutput.value = "12" === i.value ? "12+ months" : "1" === i.value ? "1 month" : "0" === i.value ? "Unknown" : i.valueAsNumber + " months"), i.classList.contains("budget") && (t.budgetOutput.value = "60" === i.value ? "$60K+" : "5" === i.value ? "Unknown" : "$" + i.valueAsNumber + "K")
                })
            })
        }, stickyHandler: function () {
            this.top = t.pageYOffset || 0, this.nav && (this.top > this.viewportHeight - 300 && this.top < this.viewportHeight - 69 ? this.nav.className = "js-nav nav--active nav--publish nav--unsticky" : this.top > this.viewportHeight - 70 ? this.nav.className = "js-nav nav--active nav--sticky" : (this.nav.className = "js-nav nav--active nav--unsticky", this.wasNavigationTapped || this.selectActiveMenuItem(0)))
        }, setupLocations: function () {
            let t = this;
            t.links && (this.content = [], t.nav && !t.nav.classList.contains("sub") && (this.timeout = setTimeout(function () {
                util.forEach(t.links, function (i) {
                    t.href = t.links[i].getAttribute("href").replace("#", ""), t.content.push(e.getElementById(t.href).offsetTop + 200)
                })
            }, 500)))
        }, isMobile: function () {
            this.mobileEl = e.getElementById("ismobile"), this.mobileEl && (this.mobileEl.value = this.viewportWidth > 800 ? "false" : "true")
        }, resize: function () {
            let i = this;

            this.calcViewport(), clearTimeout(this.timeout), this.setupLocations(), this.currWidth = t.innerWidth || this.html.clientWidth || this.body.clientWidth, this.currWidth !== this.initialWidth && (this.initialWidth = this.currWidth, this.isMobile(), this.activeArticles = e.querySelectorAll("article.active"), this.reactivateArticles = e.querySelectorAll("article.original"), util.forEach(this.activeArticles, function (t) {
                i.activeArticles[t].classList.remove("active")
            }), util.forEach(this.reactivateArticles, function (t) {
                i.reactivateArticles[t].classList.add("active")
            }), this.viewportWidth > 1e3 ? (this.slider && this.destroyCarousel(), this.initCarousel(), this.slideElems = e.querySelectorAll(".articles article")) : this.viewportWidth < 1e3 && this.slider && this.destroyCarousel())

        }, destroyCarousel: function () {
            this.slider.destroy(), this.slideElems = null, this.sliderEl = null, this.slider = null
        }, selectActiveMenuItem: function (t) {
            let e = this;
            util.forEach(e.links, function (t) {
                e.links[t].className = e.links[t].className.replace(/[\s]{0,}active/, "")
            }), e.links[t].className += e.links[t].className ? " active" : "active", e.activeLink = e.links[t]
        }, highlightOnScroll: function () {
            if (this.nav) {
                let e = this, i = e.activeLink.getAttribute("href");
                !e.wasNavigationTapped && e.content && (util.forEach(e.content, function (t, i) {
                    i > e.top && (i < e.top + 300 || e.top + e.viewportHeight >= e.bodyheight) && e.selectActiveMenuItem(t)
                }), e.currentHash !== i && (e.currentHash = i, history.pushState && "#home" === i && history.pushState(null, null, t.location.pathname + t.location.search)))
            }
        }, selectAndScroll: function () {
            let e = this;
            e.links && util.forEach(e.links, function (i) {
                util.addListener(e.links[i], "click", function (n) {
                    e.wasNavigationTapped = !0, e.nav && !e.nav.classList.contains("sub") && (n.preventDefault(), e.selectActiveMenuItem(i), e.thisID = this.getAttribute("href"), history.pushState && ("#home" == e.thisID ? (history.pushState(null, null, e.thisID), setTimeout(function () {
                        history.pushState(null, null, t.location.pathname + t.location.search)
                    }, 0)) : history.pushState(null, null, e.thisID))), e.clearTapCheck()
                }, !1)
            })
        }, clearTapCheck: function () {
            let t = this;
            setTimeout(function () {
                t.wasNavigationTapped = !1
            }, 600)
        }, initContactButtons: function () {
            let t = this;
            this.contactButtons = e.querySelectorAll("[data-contact]"), this.contactButtons && (this.html.classList.contains("android-webkit") || util.forEach(t.contactButtons, function (i) {
                util.addListener(t.contactButtons[i], "click", function () {
                    t.wasNavigationTapped = !0, setTimeout(function () {
                        e.getElementById("fullname").focus()
                    }, 1e3), t.selectActiveMenuItem(4), t.clearTapCheck()
                })
            }))
        }
    }, t.website = n
}(window, document), website();
