$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal .modal-content").html("");
        $("#modal").modal("show");
      },
      success: function (data) {
        $("#modal .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $(".blogger-blog-list").html(data.html_blogger_blog_list)
          $(".messages-block").html(data.html_messages_block)
          $("#modal").modal("hide");
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#modal .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  let authUpdateNavbar = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {

          $("#navbar").html(data.html_navbar);
          $("#modal").modal("hide");
          $(".button-create").html(data.html_button_create_blog)
          $(".messages-block").html(data.html_messages_block)
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#modal .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  var loadBloggerForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#blogger-profile-content").html("");
      },
      success: function (data) {
        $("#blogger-profile-content").html(data.html_form);
      }
    });
  };

  var saveBloggerForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#blogger-profile-content").html(data.html_profile_content);
          $(".messages-block").html(data.html_messages_block)
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#blogger-profile-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  var loadBloggerPictureForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#picture-block").html("");
        $(".blogger-blog-list").html("");
        console.log('Here1')
      },
      success: function (data) {
        $("#picture-block").html(data.html_form);
        console.log('Here2')
      }
    });
  };

  var saveBloggerPictureForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#picture-block").html(data.html_picture_block);
          $(".messages-block").html(data.html_messages_block)
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#picture-block").html(data.html_form);
        }
      }
    });
    return false;
  };

  let blogUpdateBlogContent = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#blog-detail").html(data.html_blog_detail);
          $(".blogger-blog-list").html(data.html_blogger_blog_list)
          $("#modal").modal("hide");
          $(".messages-block").html(data.html_messages_block)
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#modal .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  let blogBloggerUpdateBlogContent = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#blog-detail").html(data.html_blog_detail);
          $(".blogger-blog-list").html(data.html_blogger_blog_list)
          $("#modal").modal("hide");
          $(".messages-block").html(data.html_messages_block)
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#modal .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  let updateChangePasswordForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#modal .modal-content").html(data.html_form);
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#modal .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  let changePasswordForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#modal").modal("hide");
          $(".messages-block").html(data.html_messages_block)
        }
        else {
          $(".messages-block").html(data.html_messages_block)
          $("#modal .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */

  // auth
  $("body").on("click", "#sign-up-nav-button", loadForm);
  // $("body").on("click", "#sign-up-nav-button", formRefreshScripts);
  $("#modal").on("submit", ".sign-up-form", authUpdateNavbar);

  $("body").on("click", "#log-in-nav-button", loadForm);
  // $("body").on("click", "#log-in-nav-button", formRefreshScripts);
  $("#modal").on("submit", ".log-in-form", authUpdateNavbar);

  $("body").on("click", "#update-blogger-button", loadBloggerForm);
  // $("body").on("click", "#update-blogger-button", formRefreshScripts);
  $("body").on("submit", ".update-blogger-form", saveBloggerForm);

  $("body").on("click", "#update-blogger-picture-button", loadBloggerPictureForm);
  // $("body").on("submit", ".update-blogger-picture-form", saveBloggerPictureForm)

  $("body").on("click", "#change-password-button", loadForm);
  $("body").on("submit", ".check-password-form", updateChangePasswordForm)
  $("body").on("submit", ".change-password-form", changePasswordForm)


  // blog
  $("body").on("click", ".create-blog-button", loadForm);
  // $("body").on("click", ".create-blog-button",formRefreshScripts);
  $("#modal").on("submit", ".create-blog-form", saveForm);

  $("body").on("click", ".update-blog-button", loadForm);
  // $("body").on("click", ".update-blog-button", formRefreshScripts);
  $("#modal").on("submit", ".update-blog-form", blogUpdateBlogContent);

  $("body").on("click", ".delete-blog-button", loadForm);
  $("#modal").on("submit", ".delete-blog-blogger-form", blogBloggerUpdateBlogContent);

  $("body").on("click", ".create-comment-button", loadForm);
  // $("body").on("click", ".create-comment-button", formRefreshScripts);
  $("#modal").on("submit", ".comment-create-form", saveForm);

  $("body").on("click", "#contact-us-nav-button", loadForm);
  // $("body").on("click", "#contact-us-nav-button", formRefreshScripts);
  $("#modal").on("submit", ".contact-us-form", saveForm);


});