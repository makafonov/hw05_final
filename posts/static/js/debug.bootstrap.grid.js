$(function() {
var cols = $("[class*=col-]"),
    lightColor = "rgba(102,178,255,.3)",
    darkColor = "rgba(102,178, 255, .6)";
cols.css({
    "background": lightColor,
    "border": ("2px solid " + darkColor)
}).each(function () {
    $(this).append("<span class=\"debug\">" + $(this).attr("class").match(/col-(\S+)/g) + "</span>");
}).find(".debug").css({
    "font-size": 8,
    "font-weight": "normal"
});
});

