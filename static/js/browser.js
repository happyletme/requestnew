var ua = navigator.userAgent.toLowerCase();

var isStrict = document.compatMode == "CSS1Compat",
    isOpera = ua.indexOf("opera") > -1,
    isSafari = (/webkit|khtml/).test(ua),
    isSafari3 = isSafari && ua.indexOf('webkit/5') != -1,
    isIE = !isOpera && ua.indexOf("msie") > -1,
    isIE7 = !isOpera && ua.indexOf("msie 7") > -1,
    isGecko = !isSafari && ua.indexOf("gecko") > -1,
    isBorderBox = isIE && !isStrict,
    isWindows = (ua.indexOf("windows") != -1 || ua.indexOf("win32") != -1),
    isMac = (ua.indexOf("macintosh") != -1 || ua.indexOf("mac os x") != -1),
    isAir = (ua.indexOf("adobeair") != -1),
    isLinux = (ua.indexOf("linux") != -1),
    isSecure = window.location.href.toLowerCase().indexOf("https") === 0;