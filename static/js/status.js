$(function() {

  $('#start').click(function() {
    $.ajax({
      dataType: 'json',
      type: 'post',
      url: '/start',
      success: function(data) {
        if (data.started) {
          window.location.reload();
        }
        else {
          alert(data.message || 'Failed to start task worker.');
        }
      }
    });
  });

  $('#stop').click(function() {
    $.ajax({
      dataType: 'json',
      type: 'post',
      url: '/stop',
      success: function(data) {
        if (data.stop_sent) {
          window.location.reload();
        }
        else {
          alert(data.message || 'Failed to send stop signal to the worker.');
        }
      }
    });
  });

  $('#shutdown').click(function() {
    $.ajax({
      url: '/shutdown',
      type: 'post',
      complete: function() { window.location.reload(); }
    });
  });

});
