// $(function (){
//     var loadBloggerForm = function () {
//     console.log('HERE1')
//     var btn = $(this);
//     $.ajax({
//       url: btn.attr("data-url"),
//       type: 'get',
//       dataType: 'json',
//       beforeSend: function () {
//         $("#blogger-profile-content").html("");
//       },
//       success: function (data) {
//         $("#blogger-profile-content").html(data.html_form);
//         // console.log(data.html_form)
//       }
//     });
//   };
//
//   var saveBloggerForm = function () {
//     console.log('saveBloggerForm')
//     var form = $(this);
//     $.ajax({
//       url: form.attr("action"),
//       data: form.serialize(),
//       type: form.attr("method"),
//       dataType: 'json',
//       success: function (data) {
//         if (data.form_is_valid) {
//           console.log('1')
//           console.log(data)
//           $("#blogger-profile-content").html(data.html_blogger_detail);
//         }
//         else {
//           console.log('2')
//           console.log(data)
//           $("#blogger-profile-content").html(data.html_form);
//         }
//       }
//     });
//     return false;
//   };
//
//   var loadBloggerPictureForm = function () {
//     console.log('HERE1')
//     var btn = $(this);
//     $.ajax({
//       url: btn.attr("data-url"),
//       type: 'get',
//       dataType: 'json',
//       beforeSend: function () {
//         $("#picture-block").html("");
//       },
//       success: function (data) {
//         $("#picture-block").html(data.html_form);
//         // console.log(data.html_form)
//       }
//     });
//   };
//
//   var saveBloggerPictureForm = function () {
//     console.log('saveBloggerPictureForm')
//     var form = $(this);
//     $.ajax({
//       url: form.attr("action"),
//       data: form.serialize(),
//       type: form.attr("method"),
//       dataType: 'json',
//       success: function (data) {
//         if (data.form_is_valid) {
//           console.log('1')
//           console.log(data)
//           $("#picture-block").html(data.html_picture_block);
//         }
//         else {
//           console.log('2')
//           console.log(data)
//           $("#picture-block").html(data.html_form);
//         }
//       }
//     });
//     return false;
//   };
//
//
//   $("#update-blogger-button").click(loadBloggerForm);
//   $("#blogger-profile-content").on("submit", ".update-blogger-form", saveBloggerForm);
//
//   $("#update-blogger-picture-button").click(loadBloggerPictureForm);
//   $("#picture-block").on("submit", ".update-blogger-picture-form", saveBloggerPictureForm);
// })
