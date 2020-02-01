let $user_photo = $("#user_photo");

function deletePhoto() {
  $.ajax({
    url  : delete_photo_url,
    type : 'POST',
  }).done(function (data, textStatus, jqXHR) {
    changePhoto({}, data)
  }).fail(function (jqXHR, textStatus, errorThrown) {
    if (jqXHR.status === 404) {
      toastr.error("", "Пожалуйста, обновите страницу");
    } else {

    }
  });
}

function changePhoto(e, response) {
  $user_photo.attr("src", response.image_url);
}

$(document).ready(function () {
  new Dropzone(document.body, {
    url           : change_photo_url,
    clickable     : "#select-photo",
    acceptedFiles : "image/*",
    headers       : {
      "X-CSRFToken" : csrftoken
    },
    success       : changePhoto,
  });

  $("#delete-photo").click(deletePhoto);

  $(".dateinput").pickadate({
    format       : "mmmm dd, yyyy",
    selectYears  : 100,
    selectMonths : true
  });
  // if (activeTab !== '') {
  //   $('#account-pill-' + activeTab).tab('show');
  // }
});
