var btnOuter = $(".button_outer");

function readFile() {

  var preview = document.querySelector('#result');
  var file = document.querySelector('input[type=file]').files[0];
  var reader  = new FileReader();

  reader.addEventListener("load", function () {

    loadImage(
        reader.result,
        function (img) {
          try {preview.src = img.toDataURL("image/jpeg");}
          catch(e) {$(".error_msg").text("Неверный формат...");}
        },
        {
            orientation: true,
            maxHeight: 300,
            canvas: true
        }
    );

    // preview.src = reader.result;

  }, false);
  // console.log(preview.src);
  // console.log(file);

  if (file) {
    reader.readAsDataURL(file);

    btnOuter.addClass("file_uploading");
    setTimeout(function(){
      btnOuter.addClass("file_uploaded");
    },3000);

    setTimeout(function(){
      $("#uploaded_view").addClass("show");
    },3500);
    $("#push4magic").removeClass('d-none');
  }

}

$(".file_remove").on("click", function(e){
  $("#uploaded_view").removeClass("show");
  // $("#uploaded_view").find("img").remove();
  btnOuter.removeClass("file_uploading");
  btnOuter.removeClass("file_uploaded");
  $("#push4magic").addClass('d-none');
});
