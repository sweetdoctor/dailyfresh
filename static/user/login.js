$(function () {
    $('.name_input').blur(function () {
        checkUser()
    });
    $('.pass_input').blur(function () {
        checkPwd()
    })
})

function checkUser() {
    nameLength = $('.name_input').val().length;
    if(nameLength!==0){
        error_user = false
        $('.name_input').next().hide()

    }
    else {
        error_user = true
        $('.name_input').next().html('请输入用户名')
        $('.name_input').next().show()
    }
}

function checkPwd() {
    pwdLength = $('.pass_input').val().length
    if(pwdLength == 0){
        error_pass = true
        $('.pass_input').next().html('请输入密码')
        $('.pass_input').next().show()
    }
    else {
        error_pass = false
        $('.pass_input').next().hide()
    }
}
$('#form').submit(function () {
    checkUser()
    checkPwd()
    if(error_pass==false && error_user==false){
        return true
    }
    else {
        // alert('dd')
        return false
    }
    // return true
})