var SiteHelper = function() {};
SiteHelper.prototype.openDialog = function(a) {
    a = document.querySelector("#" + a);
    var b = document.querySelector("#overlay");
    a && (this.resetDialogs(), a.style.display = "block", b.style.display = "block")
};
SiteHelper.prototype.resetDialogs = function() {
    for (var a = document.querySelectorAll(".dialog"), b = document.querySelector("#overlay"), c = a.length - 1; 0 <= c; c--) {
        a[c].style.display = "none"
    }
    b.style.display = "none"
};
SiteHelper.prototype.setError = function(a, b) {
    var c = document.querySelector("#" + a);
    c && (c.style.display = "block", c.innerHTML = b)
};
SiteHelper.prototype.login = function(a, b) {
    var c = this;
    ajax.post("/api/v1/login/standard", {
        username: a
        , password: b
    }, function(a, b) {
        json = JSON.parse(a);
        200 == b ? location.reload() : c.setError("login-error", json.error || "Something happened")
    })
};
SiteHelper.prototype.register = function(a, b, c, d) {
    for (var f = document.querySelectorAll(".field.error"), e = f.length - 1; 0 <= e; e--) {
        f[e].className = "field"
    }
    ajax.post("/api/v1/account/create", {
        username: a
        , mail: b
        , password: c
        , passwordr: d
    }, function(a, b) {
        json = JSON.parse(a);
        if (200 == b) {
            location.reload()
        } else {
            for (var c in json) {
                var d = document.querySelector('[name="' + c + '"]')
                    .parentNode;
                d.className = "field error";
                d.querySelector("p")
                    .innerHTML = json[c]
            }
        }
    })
};
SiteHelper.prototype.sendFacebookToken = function(a) {
    var b = this;
    ajax.post("/api/v1/login/facebook", {
        access_token: a
    }, function(a, d) {
        200 == d ? (json = JSON.parse(a), window.location = json.redirect) : b.openDialog("fblogin-dialog")
    })
};
SiteHelper.prototype.facebookLogin = function() {
    var a = this;
    FB.getLoginStatus(function(b) {
        "connected" == b.status ? a.sendFacebookToken(b.authResponse.accessToken) : FB.login(function(b) {
            "connected" == b.status && a.sendFacebookToken(b.authResponse.accessToken)
        })
    })
};