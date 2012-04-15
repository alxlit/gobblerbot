$(function() {

  var adder = $('#task-add'),
      adderModules = $('<select>').prependTo(adder),
      adderTasks = adder.find('[name=tasks]');

  var tasks = {}, modules = []

  $.each(adderTasks.children('option'), function(i, task) {
    var module = (task = $(task)).val().split('.')[0];

    if (modules.indexOf(module) < 0) {
      modules.push(module);
    }

    tasks[module] = tasks[module] || [];
    tasks[module].push(task);
  });

  $.each(modules.sort(), function(i, module) {
    $('<option>').text(module).appendTo(adderModules);

    tasks[module] = tasks[module].sort(function(a, b) {
      return $(a).val().localeCompare($(b).val());
    });
  });

  adderModules.change(function() {
    var me = $(this), selected = me.find('option:selected').text();

    // Remove previous
    adderTasks.find('option').remove();

    // Update task options
    $.each(tasks[selected], function(i, task) {
      task.appendTo(adderTasks);
    });

    adderTasks.change(function() {
      var me = $(this), selected = me.find('option:selected');

      $('#task-doc').text(selected.data('doc') || '(No description available).');
    });

    adderTasks.change();

    adderTasks.find('option:first').attr('selected', true);
  });

  adderModules.change();

  adder.submit(function() {
    var module = adderModules.find(':selected').text(),
        name = adderTasks.find(':selected').text();

    $.ajax({
      data: { 'module': module, 'name': name },
      dataType: 'json',
      type: 'post',
      url: '/tasks/add',
      success: function(data) {
        if (data.added) {
          window.location.reload();
        }
        else {
          // Something's gone wrong
          alert(data.message || 'Failed to add task to queue.');
        }
      }
    });

    return false;
  });

  var queue = $('#task-queue');

  $.each(queue.find('tbody tr'), function(i, row) {
    var cells = (row = $(row)).find('td'), id = row.data('entry-id');

    row.find('a.remove').click(function() {
      $.ajax({
        data: { 'entry_id': id },
        url: '/tasks/remove',
        type: 'post',
        success: function() {
          if (queue.find('tbody tr').length === 1) {
            window.location.reload();
          }
          else {
            row.hide(400, function() {
              row.remove()
            });
          }
        }
      });

      return false;
    });

    row.find('a.up').click(function() {
      $.ajax({
        data: {
          'entry_id': id,
          'entry_position': i - 1
        },
        url: '/tasks/move',
        type: 'post',
        success: function() {
          var prev = row.prev();

          if (prev) {
            row.hide().remove().insertBefore(prev).show(400);
          }
        }
      });

      return false;
    });

    row.find('a.down').click(function() {
      $.ajax({
        data: {
          'entry_id': id,
          'entry_position': i + 1
        },
        url: '/tasks/move',
        type: 'post',
        success: function() {
          var next = row.next();

          if (next) {
            row.hide().remove().insertAfter(next).show(400);
          }
        }
      });

      return false;
    });
  });

});
