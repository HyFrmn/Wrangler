function removeDOM_id(element)
{
     var e = document.getElementById(element);
     if(!e)
          alert("There is no element with the id: "+element);
     e.parentNode.removeChild(e);
}

function renameJobDialog(job) {	
	//Build Dialog
	dialog = Builder.node('form', {action: '/jobs/rename', method: 'post', id: 'dialog', onSubmit: "new Ajax.Request('/jobs/rename', {asynchronous:true, evalScripts:true, onComplete:function(request){Modalbox.hide()}, onFailure:function(request){alert(request.responseText)}, parameters:Form.serialize(this)}); return false;"})
	label = Builder.node('label')
	label_span = Builder.node('span')
	label_span.innerHTML = 'New Name:'
	label.appendChild(label_span)
	name_input = Builder.node('input', {type: 'text', value: job.name, name: 'job_name', id: 'job_name'})
	label.appendChild(name_input)
	dialog.appendChild(label)
	submit_button = Builder.node('input', {type: 'submit', value: 'Rename'})
	dialog.appendChild(submit_button)
	hidden_id = Builder.node('input', {type: 'hidden', value: job.id, id: 'job_id', name: 'job_id'})
	dialog.appendChild(hidden_id)	
	Modalbox.show(dialog, {title: 'Rename Job'});
}

function setJobPriorityDialog(job) {	
	//Build Dialog
	dialog = Builder.node('form', {action: '/jobs/priority', method: 'post', id: 'job_priority_dialog', onSubmit: "new Ajax.Request('/jobs/priority', {asynchronous:true, evalScripts:true, onComplete:function(request){Modalbox.hide()}, onFailure:function(request){alert(request.responseText)}, parameters:Form.serialize(this)}); return false;"})
	label = Builder.node('label')
	label_span = Builder.node('span')
	label_span.innerHTML = 'New Priority:'
	label.appendChild(label_span)
	name_input = Builder.node('input', {type: 'text', value: job.priority, name: 'job_priority', id: 'job_priority'})
	label.appendChild(name_input)
	dialog.appendChild(label)
	submit_button = Builder.node('input', {type: 'submit', value: 'Set Priority'})
	dialog.appendChild(submit_button)
	hidden_id = Builder.node('input', {type: 'hidden', value: job.id, id: 'job_id', name: 'job_id'})
	dialog.appendChild(hidden_id)	
	Modalbox.show(dialog, {title: 'Set job Priority'});
}

function adjustJobPriorityDialog(job) {	
	//Build Dialog
	dialog = Builder.node('form', {action: '/jobs/adjust_priority', method: 'post', id: 'job_adjust_priority_dialog', onSubmit: "new Ajax.Request('/jobs/adjust_priority', {asynchronous:true, evalScripts:true, onComplete:function(request){Modalbox.hide()}, onFailure:function(request){alert(request.responseText)}, parameters:Form.serialize(this)}); return false;"})
	label = Builder.node('label')
	label_span = Builder.node('span')
	label_span.innerHTML = 'Priority Adjustment:'
	label.appendChild(label_span)
	name_input = Builder.node('input', {type: 'text', value: 0, name: 'job_priority', id: 'job_priority'})
	label.appendChild(name_input)
	dialog.appendChild(label)
	submit_button = Builder.node('input', {type: 'submit', value: 'Set Priority'})
	dialog.appendChild(submit_button)
	hidden_id = Builder.node('input', {type: 'hidden', value: job.id, id: 'job_id', name: 'job_id'})
	dialog.appendChild(hidden_id)	
	Modalbox.show(dialog, {title: 'Adjust job Priority'});
}

function setTaskPriorityDialog(task) {	
	//Build Dialog
	dialog = Builder.node('form', {action: '/tasks/priority', method: 'post', id: 'task_priority_dialog', onSubmit: "new Ajax.Request('/tasks/priority', {asynchronous:true, evalScripts:true, onComplete:function(request){Modalbox.hide()}, onFailure:function(request){alert(request.responseText)}, parameters:Form.serialize(this)}); return false;"})
	label = Builder.node('label')
	label_span = Builder.node('span')
	label_span.innerHTML = 'New Priority:'
	label.appendChild(label_span)
	name_input = Builder.node('input', {type: 'text', value: task.priority, name: 'task_priority', id: 'task_priority'})
	label.appendChild(name_input)
	dialog.appendChild(label)
	submit_button = Builder.node('input', {type: 'submit', value: 'Set Priority'})
	dialog.appendChild(submit_button)
	hidden_id = Builder.node('input', {type: 'hidden', value: task.id, id: 'task_id', name: 'task_id'})
	dialog.appendChild(hidden_id)	
	Modalbox.show(dialog, {title: 'Set Task Priority'});
}

function adjustTaskPriorityDialog(task) {	
	//Build Dialog
	dialog = Builder.node('form', {action: '/tasks/adjust_priority', method: 'post', id: 'task_adjust_priority_dialog', onSubmit: "new Ajax.Request('/tasks/adjust_priority', {asynchronous:true, evalScripts:true, onComplete:function(request){Modalbox.hide()}, onFailure:function(request){alert(request.responseText)}, parameters:Form.serialize(this)}); return false;"})
	label = Builder.node('label')
	label_span = Builder.node('span')
	label_span.innerHTML = 'Priority Adjustment:'
	label.appendChild(label_span)
	name_input = Builder.node('input', {type: 'text', value: 0, name: 'task_priority', id: 'task_priority'})
	label.appendChild(name_input)
	dialog.appendChild(label)
	submit_button = Builder.node('input', {type: 'submit', value: 'Set Priority'})
	dialog.appendChild(submit_button)
	hidden_id = Builder.node('input', {type: 'hidden', value: task.id, id: 'task_id', name: 'task_id'})
	dialog.appendChild(hidden_id)	
	Modalbox.show(dialog, {title: 'Adjust Task Priority'});
}

function getRowData(tr){
	fields = tr.getElementsBySelector('td');
	task_data = {};
	for (var i = 0; i < fields.length; i++){
	    field = fields[i]
	    field_name = field.readAttribute('field');
	    field_value = field.readAttribute('value');
	    if (!field_value){
	        field_value = field.innerHTML;
	    }
	    task_data[field_name] = field_value
	}
	return task_data
}

var getJobData = function(e){
	return getRowData(e.findElement('tr'))
}

var jobMenuItems = [
  {
    name: 'Rename',
    className: 'rename', 
    callback: function(e) {
        job = getJobData(e);
        renameJobDialog(job);
        alert(job.name);
    }
  },{
    name: 'Set Priority',
    className: 'priority', 
    callback: function(e) {
        job = getJobData(e);
        setJobPriorityDialog(job);
    }
  },{
    name: 'Adjust Priority',
    className: 'adjust',
    callback: function(e){
		job = getJobData(e);
		adjustJobPriorityDialog(job); 
	}
  },{
    separator: true
  },{
    name: 'Queue',
    className: 'save',
    callback: function(e) {
	  job = getJobData(e)
      new Ajax.Request('/jobs/queue',{
	      asynchronous:true,
	      evalScripts:true,
	      onFailure:function(request){alert(request.responseText)},
	      parameters: job});
	   }  
	},{
	    name: 'Pause',
	    className: 'save',
	    callback: function(e) {
		  job = getJobData(e)
	      new Ajax.Request('/jobs/pause',{
		      asynchronous:true,
		      evalScripts:true,
		      onFailure:function(request){alert(request.responseText)},
		      parameters: job });
		}
	},{
		name: 'Stop',
	    className: 'save',
	    callback: function(e) {
		  job = getJobData(e)
	      new Ajax.Request('/jobs/stop',{
		      asynchronous:true,
		      evalScripts:true,
		      onFailure:function(request){alert(request.responseText)},
		      parameters: job });
		   }
     }
]

var taskMenuItems = [
  {
    name: 'Set Priority',
    className: 'priority', 
    callback: function(e) {
        task = getRowData(e.findElement('tr'));
        setTaskPriorityDialog(task)
    }
  },{
    name: 'Adjust Priority',
    className: 'adjust',
    callback: function(e){
		task = getRowData(e.findElement('tr'));
		adjustTaskPriorityDialog(task); 
	}
  },{
    separator: true
  },{
    name: 'Queue',
    className: 'save',
    callback: function() {
      alert('Saving...');
    }
  }
]
