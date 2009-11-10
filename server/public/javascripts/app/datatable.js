taskTableDefs = [{ 
					key: 'id',
					label: 'ID',
				},
				{
					key: 'status',
					label: 'Status',
				},
				{
					key: 'priority',
					label: 'Priority'
				},
				{
					key: 'command',
					label: 'Command'
				},
				
];

//Default callbacks
//View Callbacks
function mouseoverRowCallback(e){
	tr = Event.findElement(e, 'tr');
	tr.addClassName(this.options.mouseoverClass);
}

function mouseoutRowCallback(e){
	tr = Event.findElement(e, 'tr');
	tr.removeClassName(this.options.mouseoverClass)
}

function selectRowCallback(e){
	if (this.selected){
		this.selected.removeClassName(this.options.selectedClass);
	}
	tr = Event.findElement(e, 'tr');
	tr.addClassName(this.options.selectedClass);
	this.selected = tr;
	console.log(tr);
}

var DataTable = Class.create();

DataTable.prototype = {
	//Initialize Object
	initialize: function(element, def, options){
		this.element = element;

		DEFAULT_OPTIONS = {
			// Data Input
			data: false,
			url: false,

			//Pagination
			pageCount: 10,
			paginate: false,
			search: false,
			
			//Row Callbacks
			mouseoverRowCallback: mouseoverRowCallback,
			mouseoutRowCallback: mouseoutRowCallback,
			clickRowCallback: selectRowCallback,

			//CSS
			headerClass: 'data-table-header',
			mouseoverClass: 'mouseover',
			selectedClass: 'selected',
		}

		this.options = Object.extend(DEFAULT_OPTIONS, options || {});
		
                this.ajaxParams = {
                     page: 1,
		}
		//Parse Data Defintion. 
		this.parseDefs(def);
		
		//Attributes
		this.selected = null;
		
		//Setup HTML
		this.container = $(element);
		if (!this.container){
		    alert('Missing container for datatable ' + element + '.')
		}
		this.createTable();
		this.getData(this.createRows.bind(this));
	},
	
	parseDefs : function(def){
		this.def = new Array();
		def.each(function(d){
			d = Object.extend({
				key: null,
				label: null,
				clickCallback: null,
				formatter: null, 
			}, d);
			this.def.push(d)
		}.bind(this))
	},
	
	
	
	//Model
	getData : function(callback){
		if (!this.options.data && !this.options.url){alert(this.msgs.errorData);}
		this.data = this.options.data ? this.options.data : false;
		if(this.data) {callback(); } else { this.getAjaxData(this.options.url, callback); }
	},
	getAjaxData : function(url, callback){
		var transmit = new Ajax.Request(url,{
			onLoading : function(){ $(this.element).update(this.msgs.loading); }.bind(this),
			onSuccess: function(transport) {
				this.data = transport.responseJSON;
				callback();
			}.bind(this),
			onFailure : function(){ alert(this.msgs.errorURL);},
			parameters : this.ajaxParams
		});
	},
	createCache : function(){
		this.cache = this.data;
	},
	
	//View
	createTable : function(){
		this.table = Builder.node('table', { 'class' : 'data-table', 'id' : (this.element + '-data-table') } );
		this.container.appendChild(this.table);
		this.createHeader();
	},
	
	createHeader : function(){
		thead = Builder.node('thead');
		tr = Builder.node('tr', { 'class' : this.options.headerClass});
		thead.appendChild(tr);
		this.def.each(function(d){
			td = Builder.node('td');
			td.innerHTML = d.label;
			tr.appendChild(td);
		}.bind(this));
		this.table.appendChild(thead);
	},
	
	createRows : function(){
		even = false;
		this.data.each(function(data){
			tr = this.createRow(data);
			if (even){
				tr.addClassName('even');
				even=false;
			} else {
				tr.addClassName('odd');
				even=true;
			}
		}.bind(this));
	},
	
	createRow : function(data){
		//Build Row
		var tr = Builder.node('tr');
		if (this.options.mouseoverRowCallback){
			tr.observe('mouseover', this.options.mouseoverRowCallback.bind(this));
		}
		if (this.options.mouseoutRowCallback){
			tr.observe('mouseout', this.options.mouseoutRowCallback.bind(this));
		}
		if (this.options.clickRowCallback){
			tr.observe('click', this.options.clickRowCallback.bind(this));
		}
		
		//Build Fields
		var values = Object.values(data);
		this.def.each(function(d){
			td = Builder.node('td',{ 'field' : d.key});
			td.innerHTML = data[d.key];
			if (d.clickCallback){
				td.observe('click', d.clickCallback)
			}
			tr.appendChild(td);
		}.bind(this));	
		this.table.appendChild(tr);
		return tr
	},
	
	clearRows : function(){
		even = true
		this.table.childElements().slice(1).forEach(function(child){
			this.table.removeChild(child);
		}.bind(this));
	},
	
	updateTable : function(url, callback){
		this.options.url = url
		this.clearRows()
		this.getData(function(){
			this.createRows();
			callback();
			}.bind(this));
	},	
	
	//Control
    nextPage : function(callback){
        this.ajaxParams.page += 1;
        this.updateTable(this.options.url, callback);
    },
    prevPage : function(callback){
        this.ajaxParams.page -= 1;
        if (this.ajaxParams.page < 1){
            this.ajaxParams.page = 1;
        }
        this.updateTable(this.options.url, callback);
    }	
	
}
