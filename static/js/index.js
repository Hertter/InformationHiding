$(function () {
    var imgBase64 = '';
    var change1 = document.getElementById('change1');
    var imgTag1 = document.getElementById('chooes_img1');
    var Oimg = document.getElementById('Oimg');
    var Gimg = document.getElementById('Gimg');
    var Eimg = document.getElementById('Eimg');
    // 当从本地选择页面后出发onchange事件
    change1.onchange = function (event) {
        var file = event.target.files[0];
        if (file == undefined) return false;
        url = URL.createObjectURL(file);
        $('.table').hide();
        imgTag1.src = url;
        Oimg.src = url;
        var reader = new FileReader();
        var imgUrlBase64 = '';
        if (file) {
            //将文件以Data URL形式读入页面
            imgUrlBase64 = reader.readAsDataURL(file);
            reader.onload = function (e) {
                imgBase64 = reader.result;
            }
        }
    };

    // $(".myModal").click(function () {
    // });

    $('#getinfo').click(function () {
        // 发送请求获取嵌入的信息
        // $('.infotext').text('从图像中提取的信息为：' + 'ds');
        $('.table').show();
    })
    $("#submit").click(function () {
        var toName = $("input[name='algorithm']:checked").val();
        var toUrl = 'http://127.0.0.1:5000/'+ toName + '/embed';
        $('#form1').attr('action', toUrl);
        $('.warning').hide();
        // $('#submit').attr('disabled',"true");
        // setTimeout(function(){
        //     $('#submit').removeAttr("disabled");
        // },500)
        //这里验证表单是否可以提交  如果返回false阻止提交
        if ($('#embedText').val().trim() == '') {
            $.Toast("嵌入的信息为空", "必须填入嵌入的信息", "error", {
                stack: true,
                has_icon: false,
                has_close_btn: true,
                fullscreen: false,
                timeout: 2000,
                sticky: false,
                has_progress: true,
                rtl: false,
                position_class: "toast-top-right"
            });
            return;
        }
        if ($('.copies').val() > 10000) {
            $.Toast("嵌入的信息太长", "嵌入的信息不能超过10000份", "error", {
                stack: true,
                has_icon: false,
                has_close_btn: true,
                fullscreen: false,
                timeout: 2000,
                sticky: false,
                has_progress: true,
                rtl: false,
                position_class: "toast-top-right"
            });
            return;
        }
        console.log($('input[name="format"]:checked').val());
        console.log($('input[name="algorithm"]:checked').val());
        if($('input[name="format"]:checked').val() == 'jpg' && $('input[name="algorithm"]:checked').val() == 'lsb') $('.warning').show();
        $('#form1').ajaxForm(function(data){
            $('.format-title').text('输出格式为：.' + $('input[name="format"]:checked').val().toUpperCase( ));
            $('.algorithm-title').text('选择的算法类型：' + $('input[name="algorithm"]:checked').val().toUpperCase( ));
            $('.respinfo').text(data.msg_out);
            $("#myModal").modal("show");
            setTimeout(function(){
                Gimg.src = data.image_base64_1;
                Eimg.src = data.image_base64_2;
                $('.psnr').text(data.psnr);
                $('.ssim').text(data.ssim);
            })
        })

        // 发送请求获取嵌入后的图像和嵌入后读取的信息

    })


    $('.close').click(function () {
        $('.table').hide();
        // $('#submit').removeAttr("disabled");
    })
    $('#closeModal').click(function () {
        $('.table').hide();
        // $('#submit').removeAttr("disabled");
    })
})