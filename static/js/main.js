var Main = function() {}

Main.prototype.opendialog = function(dialogid) {
	var dialog = document.querySelector('#' + dialogid)
	var overlay = document.querySelector('#overlay')
	if(dialog) {
		this.resetdialogs()
		dialog.style.display = 'block'
		overlay.style.display = 'block'
	} 
};

Main.prototype.resetdialogs = function() {
	var dialogs = document.querySelectorAll('.dialog')
	var overlay = document.querySelector('#overlay')
	for (var i = dialogs.length - 1; i >= 0; i--) {
		dialogs[i].style.display = 'none'
	};
	overlay.style.display = 'none'
};

Main.prototype.seterror = function(id, message) {
	var el = document.querySelector('#' + id)
	if(el) {
		el.style.display = 'block'
		el.innerHTML = message
	}
};

Main.prototype.login = function(username, password) {
	var self = this
	ajax.post(
		'/api/v1/login/email', { 
		username: username, password: password
	}, function(res, status) {
		if(status == 401)
			self.seterror('login-error', 'Please check your credentials')
	})
};
