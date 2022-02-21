$(document).ready(function () {
  $(".filter-box").on("click", function () {
    if ($(this).is(":checked")) {
      $("#filterresult").show();
    } else {
      $("#filterresult").load();
    }
    var _filterObj = {};
    $(".filter-box").each(function () {
      var _filterKey = $(this).data("filter");
      _filterObj[_filterKey] = Array.from(
        document.querySelectorAll(
          "input[data-filter=" + _filterKey + "]:checked"
        )
      ).map(function (el) {
        return el.value;
      });
    });
    //sending to server
    $.ajax({
      url: "filter-data",
      data: _filterObj,
      dataType: "json",
      beforeSend: function () {},
      success: function (res) {
        $("#filterresult").html(res.data);
        console.log(res);
      },
    });
  });
});
