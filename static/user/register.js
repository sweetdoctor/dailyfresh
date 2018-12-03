var errorName = true
var errorPwd = true
var errorConfirmPwd = true
var errorCheckout = false
var errorEmail = true
$(function () {
    $('#user_name').blur(function () {
        checkName()
    })
    $('#pwd').blur(function () {
        checkPwd()
    })
    $('#cpwd').blur(function () {
        checkConfirmPwd()
    })
    $('#email').blur(function () {
        checkEmail()
    })
    $('#allow').click(function() {
		if($(this).is(':checked'))
		{
			errorCheckout = false;
			$(this).siblings('span').hide();
		}
		else
		{
			errorCheckout = true;
			$(this).siblings('span').html('请勾选同意');
			$(this).siblings('span').show();
		}
	});

});

function checkName() {
    name = $('#user_name').val().length;
    if (name==0){
        $('#user_name').next().html('用户名不能为空');
        $('#user_name').next().show();
        errorName = true
    }
    else if(name > 15){
        $('#user_name').next().html('用户名不能超过20个字符')
        $('#user_name').next().show();
        errorName = true
    }
    else{
        $.get('/user/register/checkname/'+$('#user_name').val(), function (data) {
            if (data==0){
                $('#user_name').next().html('该用户已经存在')
                $('#user_name').next().show()
                errorName = true
            }
            else {
                $('#user_name').next().hide();
                errorName = false
            }
        })
    }
}
function checkPwd() {
    pwdLength = $('#pwd').val().length;
    if(pwdLength<6 || pwdLength > 20){
        $('#pwd').next().html('密码长度最少6位，最长12位')
        $('#pwd').next().show()
        errorPwd = true
    }
    else {
        $('#pwd').next().hide()
        errorPwd = false
    }
}
function checkConfirmPwd() {
    pwd = $('#pwd').val();
    cpwd = $('#cpwd').val();
    if(pwd != cpwd){
        $('#cpwd').next().html('两次密码输入不一致')
        $('#cpwd').next().show()
        errorConfirmPwd = true
    }
    else {
        $('#cpwd').next().hide()
        errorConfirmPwd  = false
    }
}
function checkEmail() {
    var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;

		if(re.test($('#email').val()))
		{
			$('#email').next().hide();
			errorEmail = false;
		}
		else
		{
			$('#email').next().html('你输入的邮箱格式不正确')
			$('#email').next().show();
			errorEmail = true;
		}
}
function checkIsAgree() {

}
$(function () {
    $('#reg_form').submit(function () {
    //     alert('jiance')
    checkName()
    checkPwd()
    checkConfirmPwd()
    checkEmail()
    if(errorName == false && errorPwd == false && errorConfirmPwd == false &&errorEmail == false && errorCheckout==false){
        // alert('zhuzhi')
        return true
    }
    return false

})
})
