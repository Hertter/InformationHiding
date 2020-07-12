$(function () {
    var imgBase64_1 = '';
    var imgBase64_2 = '';
    var change1 = document.getElementById('change1');
    var change2 = document.getElementById('change2');
    var imgTag1 = document.getElementById('chooes_img1');
    var imgTag2 = document.getElementById('chooes_img2');
    var outimg1 = document.getElementById('outimg1');
    var outimg2 = document.getElementById('outimg2');
    var outimg3 = document.getElementById('outimg3');
    var outimg4 = document.getElementById('outimg4');
    // 当从本地选择页面后出发onchange事件
    change1.onchange = function (event) {
        var file = event.target.files[0];
        if (file == undefined) return false;
        url = URL.createObjectURL(file);
        $('.table').hide();
        imgTag1.src = url;
        var reader = new FileReader();
        var imgUrlBase64 = '';
        if (file) {
            //将文件以Data URL形式读入页面
            imgUrlBase64 = reader.readAsDataURL(file);
            reader.onload = function (e) {
                imgBase64_1 = reader.result;
            }
        }
    };

    change2.onchange = function (event) {
        var file = event.target.files[0];
        if (file == undefined) return false;
        url = URL.createObjectURL(file);
        $('.table').hide();
        imgTag2.src = url;
        var reader = new FileReader();
        var imgUrlBase64 = '';
        if (file) {
            //将文件以Data URL形式读入页面
            imgUrlBase64 = reader.readAsDataURL(file);
            reader.onload = function (e) {
                imgBase64_2 = reader.result;
            }
        }
    };
    $("#submit").click(function () {
        var toUrl = 'http://127.0.0.1:5000/dwt/embed';
        $('#form1').attr('action', toUrl);
        $('.format-title').text('输出格式为：.' + $('input[name="format"]:checked').val().toUpperCase( ));
        $('#form1').ajaxForm(function(data){
            $("#myModal").modal("show");
            setTimeout(function(){
                outimg1.src = data.image_base64_1;
                outimg2.src = data.image_base64_2;
                outimg3.src = data.image_base64_3;
                outimg4.src = data.image_base64_4;
                $('.psnr').text(data.psnr);
                $('.ssim').text(data.ssim);
            })
        })
    })
    $('#getinfo').click(function () {
        // 发送请求获取嵌入的信息
        // $('.infotext').text('从图像中提取的信息为：' + 'ds');
        $('.table').show();
    })

    $('.close').click(function () {
        $('.table').hide();
    })
    $('#closeModal').click(function () {
        $('.table').hide();
    })
})